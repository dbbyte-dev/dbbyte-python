import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from dbbyte import DBByte


def serve(reply):
    seen = {}

    class H(BaseHTTPRequestHandler):
        def _h(self):
            n = int(self.headers.get("Content-Length") or 0)
            seen.update(method=self.command, path=self.path, body=self.rfile.read(n).decode())
            out = json.dumps(reply).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

        do_GET = do_POST = do_PATCH = do_DELETE = _h

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, seen, DBByte(api_key="dbk_test", base_url=f"http://127.0.0.1:{srv.server_port}")


class ApiTests(unittest.TestCase):
    def run_with(self, reply, fn):
        srv, seen, db = serve(reply)
        try:
            fn(db, seen)
        finally:
            srv.shutdown()

    def test_buckets(self):
        def go(db, seen):
            db.buckets.create("Media", "us-east", is_public=True)
            self.assertEqual((seen["method"], seen["path"]), ("POST", "/buckets"))
            self.assertEqual(json.loads(seen["body"]), {"name": "Media", "region": "us-east", "isPublic": True})
            db.buckets.update("media", cdn=False)
            self.assertEqual((seen["method"], seen["path"], seen["body"]), ("PATCH", "/buckets/media", '{"cdn": false}'))
            db.buckets.delete("media")
            self.assertEqual(seen["method"], "DELETE")
            db.buckets.list()
            self.assertEqual(seen["path"], "/buckets")

        self.run_with({"bucket": {}}, go)

    def test_purge(self):
        def go(db, seen):
            db.cdn.purge("media", scope="file", path="a.png")
            self.assertEqual(seen["path"], "/purge")
            self.assertEqual(json.loads(seen["body"]), {"slug": "media", "scope": "file", "path": "a.png"})
            with self.assertRaises(ValueError):
                db.cdn.purge("media", scope="file")
            with self.assertRaises(ValueError):
                db.cdn.purge("media", scope="all")

        self.run_with({"success": True, "purged": 1, "failed": []}, go)

    def test_data(self):
        def go(db, seen):
            db.data.get("people", limit=5, fields=["a", "b"], filters={"city": "Oslo"})
            self.assertTrue(seen["path"].startswith("/v1/data/people?"))
            for part in ("city=Oslo", "limit=5", "fields=a%2Cb"):
                self.assertIn(part, seen["path"])
            db.data.append_text("notes", "hi")
            self.assertEqual(json.loads(seen["body"]), {"appendText": "hi"})
            db.data.update("people", "7", {"a": 1})
            self.assertEqual((seen["method"], seen["path"]), ("PATCH", "/v1/data/people/7"))
            db.data.create("people", {"a": 1})
            self.assertEqual(seen["method"], "POST")
            db.data.delete("people", "7")
            self.assertEqual(seen["method"], "DELETE")

        self.run_with({"data": []}, go)

    def test_upload_url(self):
        def go(db, seen):
            res = db.objects.upload_url("media", "a.png", content_type="image/png", size=10)
            self.assertEqual(res["method"], "PUT")
            self.assertEqual(seen["path"], "/storage/media/upload-url")
            self.assertEqual(json.loads(seen["body"]), {"name": "a.png", "contentType": "image/png", "size": 10})

        self.run_with({"url": "u", "method": "PUT", "headers": {}, "expiresIn": 900}, go)


if __name__ == "__main__":
    unittest.main()
