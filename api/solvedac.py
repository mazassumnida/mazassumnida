"""Authenticated public profiles, shared by all badge styles."""

import hashlib
import json
import logging
import math
import time
from dataclasses import dataclass
from urllib.parse import quote

from curl_cffi import CurlOpt, requests
from curl_cffi.requests.exceptions import RequestException
from django.conf import settings
from django.core.cache import caches
from django.utils.http import parse_http_date_safe
from redis.exceptions import RedisError


USER_API = 'https://solved.ac/api/v4/users/'
MAX_PROFILE_BYTES = 64 * 1024
FRESH_SECONDS = 3600
STALE_SECONDS = 86400
REQUEST_BUDGET = 600
logger = logging.getLogger(__name__)


class ProfileUnavailable(Exception):
    pass


@dataclass(frozen=True)
class ProfileResult:
    data: dict
    stale: bool = False
    age: int = 0


def validate_profile(data):
    if not isinstance(data, dict):
        raise ValueError('Invalid profile')
    for field in ('rating', 'solvedCount', 'class'):
        value = data.get(field)
        if type(value) is not int or value < 0:
            raise ValueError('Invalid numeric profile field')
    if data['class'] > 10 or type(data.get('classPlus')) is not bool:
        raise ValueError('Invalid class')
    tier = data['tier']
    if tier is not None and (type(tier) is not int or not 0 <= tier <= 31):
        raise ValueError('Invalid tier')
    # Cache only fields used by the badges.
    return {key: data[key] for key in ('rating', 'solvedCount', 'class', 'classPlus', 'tier')}


def retry_seconds(value):
    """Retry-After can be a delay in seconds or an HTTP date."""
    if value and value.isascii() and value.isdecimal():
        return max(1, int(value))
    deadline = parse_http_date_safe(value or '')
    if deadline is not None:
        return max(1, math.ceil(deadline - time.time()))
    return 60


def stale_or_unavailable(record):
    if record and time.time() - record['fetched_at'] < STALE_SECONDS:
        return ProfileResult(record['profile'], stale=True)
    raise ProfileUnavailable()


def fetch_profile(handle):
    client_id = settings.SOLVED_AC_CLIENT_ID
    client_secret = settings.SOLVED_AC_CLIENT_SECRET
    if not client_id or not client_secret:
        logger.error('solved.ac client credentials are not configured')
        raise ProfileUnavailable()
    # A credential change must also invalidate authentication cooldowns.
    scope = hashlib.sha256(f'{client_id}\0{client_secret}'.encode()).hexdigest()
    identity = hashlib.sha256(handle.encode()).hexdigest()
    prefix = f'solved-ac:v4:{scope}'
    key = f'{prefix}:profile:{identity}'
    cache = caches['solved_ac']
    try:
        return cached_profile(cache, prefix, key, handle, client_id, client_secret)
    except (RedisError, OSError):
        # Do not bypass the shared request budget when its cache is unavailable.
        logger.error('solved.ac cache is unavailable')
        raise ProfileUnavailable() from None


def cached_profile(cache, prefix, key, handle, client_id, client_secret):
    record = cache.get(key)
    if cache.get(f'{key}:missing'):
        raise ProfileUnavailable()
    if record and time.time() - record['fetched_at'] < FRESH_SECONDS:
        return ProfileResult(record['profile'], age=max(0, int(time.time() - record['fetched_at'])))
    if cache.get(f'{prefix}:cooldown') or cache.get(f'{key}:retry'):
        return stale_or_unavailable(record)
    # Atomic add works across workers with Redis. Let the lease expire rather
    # than deleting a lock that a subsequent worker might already own.
    if not cache.add(f'{key}:refresh', True, timeout=15):
        return stale_or_unavailable(record)
    if not cache.take_token(f'{prefix}:budget', capacity=REQUEST_BUDGET, refill_per_second=2):
        return stale_or_unavailable(record)

    try:
        response = requests.get(
            USER_API + quote(handle, safe=''),
            headers={'x-client-id': client_id, 'x-client-secret': client_secret},
            timeout=(2, 4), allow_redirects=False,
            curl_options={CurlOpt.MAXFILESIZE_LARGE: MAX_PROFILE_BYTES},
        )
        status = response.status_code
        if status == 404:
            cache.delete(key)
            cache.set(f'{key}:missing', True, timeout=60)
            raise ProfileUnavailable()
        if status == 429:
            cache.extend_cooldown(
                f'{prefix}:cooldown', retry_seconds(response.headers.get('Retry-After')))
            logger.warning('solved.ac rate limit reached')
            return stale_or_unavailable(record)
        if status in (401, 403):
            cache.extend_cooldown(f'{prefix}:cooldown', 60)
            logger.error('solved.ac app authentication failed (HTTP %s)', status)
            return stale_or_unavailable(record)
        if status != 200 or len(response.content) > MAX_PROFILE_BYTES:
            raise ValueError('Invalid profile response')
        profile = validate_profile(json.loads(response.content))
    except (RequestException, ValueError, KeyError, RecursionError):
        cache.set(f'{key}:retry', True, timeout=30)
        logger.warning('solved.ac profile request failed')
        return stale_or_unavailable(record)

    cache.set(key, {'profile': profile, 'fetched_at': time.time()}, timeout=STALE_SECONDS)
    return ProfileResult(profile)
