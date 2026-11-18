import hashlib
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from email.utils import formatdate
from unittest.mock import MagicMock, patch
from urllib.parse import quote
from xml.etree import ElementTree

from curl_cffi import CurlOpt
from curl_cffi.requests.exceptions import Timeout
from django.core.cache import caches
from django.test import SimpleTestCase, override_settings
from redis.exceptions import ConnectionError as RedisConnectionError

from .solvedac import (
    FRESH_SECONDS, MAX_PROFILE_BYTES, STALE_SECONDS, USER_API,
    ProfileUnavailable, fetch_profile, retry_seconds,
)
from .views import TIER_RATES


PATHS = (
    '/api/generate_badge', '/api/v2/generate_badge',
    '/api/mini/generate_badge', '/api/pastel/generate_badge',
)
PROFILE = {'rating': 1300, 'solvedCount': 1234, 'class': 4, 'classPlus': True, 'tier': 14}
CLIENT_ID = 'test-client'
CLIENT_SECRET = 'test-secret'
PREFIX = 'solved-ac:v4:' + hashlib.sha256(
    f'{CLIENT_ID}\0{CLIENT_SECRET}'.encode()).hexdigest()


def upstream(data=PROFILE, status=200, headers=None):
    body = data if isinstance(data, bytes) else json.dumps(data).encode()
    return MagicMock(status_code=status, content=body, headers=headers or {})


def profile_key(handle):
    return PREFIX + ':profile:' + hashlib.sha256(handle.encode()).hexdigest()


@override_settings(
    SOLVED_AC_CLIENT_ID=CLIENT_ID, SOLVED_AC_CLIENT_SECRET=CLIENT_SECRET,
    CACHES={
        'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
        'solved_ac': {'BACKEND': 'api.cache.ProfileMemoryCache', 'LOCATION': 'badge-tests'},
    },
)
class BadgeTests(SimpleTestCase):
    def setUp(self):
        # Uses the configured backend so the suite also exercises real Redis.
        self.cache = caches['solved_ac']
        self.cache.clear()
        self.http = patch('api.solvedac.requests.get')
        self.get = self.http.start()
        self.addCleanup(self.http.stop)
        self.get.return_value = upstream()

    def text(self, response):
        return list(ElementTree.fromstring(response.content).itertext())

    def test_successful_badges_share_profile_cache(self):
        for path in PATHS:
            with self.subTest(path=path):
                response = self.client.get(path, {'handle': 'Test_01'})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response['Content-Type'], 'image/svg+xml')
                self.assertIn("default-src 'none'", response['Content-Security-Policy'])
                self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
                if '/mini/' in path:
                    self.assertIn('G2', self.text(response))
                    self.assertEqual(response['Cache-Control'], 'max-age=86400')
                else:
                    for expected in ('Test_01', '1,234', '4+', '33%'):
                        self.assertIn(expected, self.text(response))
                    self.assertEqual(response['Cache-Control'], 'max-age=3600')
        self.get.assert_called_once_with(
            USER_API + 'Test_01',
            headers={'x-client-id': CLIENT_ID, 'x-client-secret': CLIENT_SECRET},
            timeout=(2, 4), allow_redirects=False,
            curl_options={CurlOpt.MAXFILESIZE_LARGE: MAX_PROFILE_BYTES},
        )

    def test_legacy_parameter_default_and_explicit_handle_precedence(self):
        for query in ({}, {'boj': 'ccoco'}, {'boj': 'other', 'handle': 'ccoco'}):
            response = self.client.get(PATHS[0], query)
            self.assertIn('ccoco', self.text(response))
        self.get.assert_called_once()
        self.assertEqual(self.get.call_args.args[0], USER_API + 'ccoco')

    def test_handle_path_encoding_and_xml_escaping(self):
        for handle in ('a<&b', '한글.name', 'a/b?#x', 'a' * 64):
            with self.subTest(handle=handle):
                self.cache.clear()
                response = self.client.get(PATHS[1], {'handle': handle})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(self.get.call_args.args[0], USER_API + quote(handle, safe=''))
                expected = handle if len(handle) <= 15 else handle[:13] + '...'
                self.assertIn(expected, self.text(response))

    def test_invalid_handles_and_methods_skip_upstream(self):
        for path in PATHS:
            for handle in ('', 'two words', 'a' * 65, '..', '.', '\n', '\x00', '\uffff'):
                with self.subTest(path=path, handle=handle):
                    self.assertEqual(self.client.get(path, {'handle': handle}).status_code, 400)
            self.assertEqual(self.client.post(path).status_code, 405)
        self.get.assert_not_called()

    def test_official_tier_and_class_plus(self):
        for tier, rating in enumerate(TIER_RATES):
            with self.subTest(tier=tier):
                self.cache.clear()
                self.get.return_value = upstream({**PROFILE, 'tier': tier, 'rating': rating,
                                                 'classPlus': False})
                response = self.client.get(PATHS[0])
                self.assertEqual(response.status_code, 200)
                self.assertIn('4', self.text(response))
                self.assertNotIn('4+', self.text(response))
                self.assertIn('100%' if tier == 31 else '0%', self.text(response))

    def test_null_or_inconsistent_tier_omits_progress_without_losing_stats(self):
        for tier in (None, 0, 31):
            with self.subTest(tier=tier):
                self.cache.clear()
                self.get.return_value = upstream({**PROFILE, 'tier': tier})
                response = self.client.get(PATHS[0])
                texts = self.text(response)
                self.assertIn('1,234', texts)
                self.assertIn('1,300', texts)
                self.assertNotIn('33%', texts)
                self.assertEqual(response['Cache-Control'], 'max-age=3600')

    def test_upstream_failures_and_invalid_schema_render_unknown(self):
        invalid = [
            b'invalid json', b'{}', b'[]', b' ' * (MAX_PROFILE_BYTES + 1),
            {**PROFILE, 'class': 'four'}, {**PROFILE, 'class': 11},
            {**PROFILE, 'classPlus': 1}, {**PROFILE, 'tier': True},
            {**PROFILE, 'tier': 32}, {**PROFILE, 'rating': -1},
            {**PROFILE, 'solvedCount': False},
            {k: v for k, v in PROFILE.items() if k != 'tier'},
        ]
        for result in [Timeout('Request timed out'), upstream(status=302),
                       upstream(status=500), *map(upstream, invalid)]:
            with self.subTest(result=result):
                self.cache.clear()
                self.get.side_effect = [result]
                response = self.client.get(PATHS[0])
                self.assertIn('Unknown', self.text(response))
                self.assertEqual(response['Cache-Control'], 'no-store')

    def stale_record(self, handle='ccoco', age=FRESH_SECONDS + 1):
        self.cache.set(profile_key(handle),
                       {'profile': PROFILE, 'fetched_at': time.time() - age}, timeout=60)

    def test_temporary_failure_uses_bounded_stale_data(self):
        self.stale_record()
        self.get.side_effect = Timeout('Request timed out')
        for _ in range(2):
            response = self.client.get(PATHS[0])
            self.assertIn('1,234', self.text(response))
            self.assertEqual(response['Cache-Control'], 'no-store')
        self.get.assert_called_once()
        self.stale_record(age=STALE_SECONDS + 1)
        self.assertIn('Unknown', self.text(self.client.get(PATHS[0])))

    def test_client_cache_ttl_accounts_for_profile_age(self):
        self.stale_record(age=120)
        normal = self.client.get(PATHS[0])
        mini = self.client.get(PATHS[2])
        self.assertEqual(normal['Cache-Control'], 'max-age=3480')
        self.assertEqual(mini['Cache-Control'], 'max-age=86280')
        self.get.assert_not_called()

    def test_expired_profile_is_refreshed_once_and_caches_only_used_fields(self):
        self.stale_record()
        updated = {**PROFILE, 'solvedCount': 2000}
        self.get.return_value = upstream({**updated, 'bio': 'unused content'})
        for path in (PATHS[0], PATHS[1]):
            response = self.client.get(path)
            self.assertIn('2,000', self.text(response))
            self.assertEqual(response['Cache-Control'], 'max-age=3600')
        self.get.assert_called_once()
        self.assertEqual(self.cache.get(profile_key('ccoco'))['profile'], updated)

    def test_404_invalidates_stale_data_and_negative_caches(self):
        self.stale_record()
        self.get.return_value = upstream(status=404)
        for _ in range(2):
            self.assertIn('Unknown', self.text(self.client.get(PATHS[0])))
        self.get.assert_called_once()
        self.assertIsNone(self.cache.get(profile_key('ccoco')))

    def test_authentication_and_rate_errors_pause_other_handles(self):
        for status in (401, 403, 429):
            with self.subTest(status=status):
                self.cache.clear()
                self.get.reset_mock()
                self.get.return_value = upstream(status=status, headers={'Retry-After': '120'})
                self.client.get(PATHS[0], {'handle': 'one'})
                response = self.client.get(PATHS[1], {'handle': 'two'})
                self.assertEqual(response['Cache-Control'], 'no-store')
                self.get.assert_called_once()

    def test_retry_after_formats_and_cooldown_extension(self):
        self.assertEqual(retry_seconds('120'), 120)
        self.assertEqual(retry_seconds('garbage'), 60)
        with patch('api.solvedac.time.time', return_value=100000):
            self.assertEqual(retry_seconds(formatdate(100120, usegmt=True)), 120)
        self.cache.extend_cooldown(PREFIX + ':cooldown', 120)
        self.cache.extend_cooldown(PREFIX + ':cooldown', 1)
        # Short auth failures must not shorten an earlier Retry-After.
        with patch('time.time', return_value=time.time() + 2):
            self.assertTrue(self.cache.get(PREFIX + ':cooldown'))

    def test_cold_requests_are_rate_limited_and_fresh_cache_still_works(self):
        with patch('api.solvedac.REQUEST_BUDGET', 2):
            fetch_profile('one')
            fetch_profile('two')
            with self.assertRaises(ProfileUnavailable):
                fetch_profile('three')
            self.assertFalse(fetch_profile('one').stale)
        self.assertEqual(self.get.call_count, 2)

    def test_concurrent_refresh_only_calls_upstream_once(self):
        started = threading.Event()
        finish = threading.Event()

        def delayed_response(*args, **kwargs):
            started.set()
            self.assertTrue(finish.wait(5))
            return upstream()

        self.get.side_effect = delayed_response
        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(fetch_profile, 'one')
            try:
                self.assertTrue(started.wait(5))
                with self.assertRaises(ProfileUnavailable):
                    fetch_profile('one')
            finally:
                finish.set()
            self.assertEqual(first.result(timeout=5).data, PROFILE)
        self.get.assert_called_once()

    def test_shared_budget_reserves_tokens_atomically(self):
        def reserve(_):
            return self.cache.take_token('concurrent-budget', capacity=2, refill_per_second=0.01)

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(reserve, range(24)))
        self.assertEqual(sum(results), 2)

    def test_budget_refills(self):
        self.assertTrue(self.cache.take_token('refill-budget', capacity=1, refill_per_second=50))
        time.sleep(0.03)
        self.assertTrue(self.cache.take_token('refill-budget', capacity=1, refill_per_second=50))

    def test_missing_credentials_and_cache_outage_skip_upstream(self):
        with override_settings(SOLVED_AC_CLIENT_SECRET=''):
            self.assertIn('Unknown', self.text(self.client.get(PATHS[0])))
        with patch.object(self.cache, 'get', side_effect=RedisConnectionError()):
            self.assertIn('Unknown', self.text(self.client.get(PATHS[0])))
        self.get.assert_not_called()

    def test_key_rotation_clears_authentication_cooldown(self):
        self.get.return_value = upstream(status=401)
        self.client.get(PATHS[0])
        self.get.return_value = upstream()
        with override_settings(SOLVED_AC_CLIENT_SECRET='rotated-test-secret'):
            self.assertIn('1,234', self.text(self.client.get(PATHS[0])))
        self.assertEqual(self.get.call_count, 2)
