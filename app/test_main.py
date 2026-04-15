import json
import os
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer

from main import Handler


def _start_server() -> tuple[HTTPServer, int]:
    server = HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, port


class TestHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.port = _start_server()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def _get(self, path: str) -> tuple[int, str, bytes]:
        url = f"http://127.0.0.1:{self.port}{path}"
        with urllib.request.urlopen(url) as resp:
            return resp.status, resp.headers.get("Content-Type", ""), resp.read()

    def test_healthz_returns_200(self):
        status, _, body = self._get("/healthz")
        self.assertEqual(status, 200)
        self.assertEqual(body.strip(), b"ok")

    def test_root_returns_json(self):
        status, ct, body = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn("application/json", ct)
        data = json.loads(body)
        self.assertIsInstance(data, dict)

    def test_root_contains_env_vars(self):
        os.environ["TEST_VAR"] = "hello"
        _, _, body = self._get("/")
        data = json.loads(body)
        self.assertEqual(data["TEST_VAR"], "hello")

    def test_unknown_path_returns_404(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._get("/does-not-exist")
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
