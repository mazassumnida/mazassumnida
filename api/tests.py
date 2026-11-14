import json
from unittest.mock import MagicMock, patch
from xml.etree import ElementTree

from curl_cffi import CurlOpt
from curl_cffi.requests.exceptions import Timeout
from django.test import SimpleTestCase

from .views import MAX_PROFILE_BYTES, USER_API


PATHS = (
    '/api/generate_badge', '/api/v2/generate_badge',
    '/api/mini/generate_badge', '/api/pastel/generate_badge',
)
PROFILE = {'rating': 1300, 'solvedCount': 1234, 'class': 4, 'classDecoration': 'gold'}


def upstream(body, status=200):
    response = MagicMock()
    response.status_code = status
    response.content = body
    return response


class BadgeTests(SimpleTestCase):
    @patch('api.views.requests.get')
    def test_successful_badges(self, get):
        get.return_value = upstream(json.dumps(PROFILE).encode())
        for path in PATHS:
            with self.subTest(path=path):
                response = self.client.get(path, {'boj': 'Test_01'})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response['Content-Type'], 'image/svg+xml')
                root = ElementTree.fromstring(response.content)
                self.assertIn("default-src 'none'", response['Content-Security-Policy'])
                self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
                if '/mini/' in path:
                    self.assertIn('G2', list(root.itertext()))
                    self.assertEqual(response['Cache-Control'], 'max-age=86400')
                else:
                    for expected in ('Test_01', '1,234', '4++'):
                        self.assertIn(expected, list(root.itertext()))
                    self.assertEqual(response['Cache-Control'], 'max-age=3600')
                get.assert_called_with(
                    USER_API, params={'handle': 'Test_01'}, impersonate='chrome110',
                    timeout=(2, 4), allow_redirects=False,
                    curl_options={CurlOpt.MAXFILESIZE_LARGE: MAX_PROFILE_BYTES},
                )

    @patch('api.views.requests.get')
    def test_invalid_handles_and_methods_skip_upstream(self, get):
        for path in PATHS:
            for handle in ('', 'two words', 'a&b', 'a' * 21):
                with self.subTest(path=path, handle=handle):
                    self.assertEqual(self.client.get(path, {'boj': handle}).status_code, 400)
            self.assertEqual(self.client.post(path).status_code, 405)
        get.assert_not_called()

    @patch('api.views.requests.get')
    def test_unknown_badge_on_upstream_failure(self, get):
        for result in (
            Timeout('Request timed out'), upstream(b'', 302), upstream(b'', 404),
            upstream(b'invalid json'), upstream(b'{}'),
            upstream(json.dumps({**PROFILE, 'class': 'four'}).encode()),
            upstream(b' ' * (MAX_PROFILE_BYTES + 1)),
        ):
            with self.subTest(result=result):
                get.side_effect = [result]
                response = self.client.get(PATHS[0])
                self.assertEqual(response.status_code, 200)
                self.assertIn('Unknown', list(ElementTree.fromstring(response.content).itertext()))
                self.assertEqual(response['Cache-Control'], 'no-store')
