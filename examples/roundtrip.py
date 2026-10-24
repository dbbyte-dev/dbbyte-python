"""Round-trip test against a real DBByte server. Exercises every SDK
method against actual HTTP endpoints.

Usage:
    DBBYTE_API_KEY=dbk_xxx DBBYTE_BUCKET=my-test-bucket python roundtrip.py

Env vars:
    DBBYTE_API_KEY   required. Needs read+write+delete on the bucket.
    DBBYTE_BUCKET    required. An existing bucket slug to test against.
    DBBYTE_BASE_URL  optional. If unset, uses the SDK's own default
                     (https://api.dbbyte.com) - the real production
                     Worker gateway. To test against a local Next.js
                     dev server instead (bypassing the Worker), set
                     this explicitly, e.g. http://localhost:3000/api/v1.
                     Deliberately NOT defaulted to localhost here - a
                     silent local fallback previously masked a test
                     run against the Node SDK actually hitting
                     production. Don't repeat that mistake.
"""

from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dbbyte import DBByte, DBByteError  # noqa: E402
from dbbyte.client import DEFAULT_BASE_URL  # noqa: E402

api_key = os.environ.get("DBBYTE_API_KEY")
bucket = os.environ.get("DBBYTE_BUCKET")
base_url = os.environ.get("DBBYTE_BASE_URL")

if not api_key or not bucket:
    print("Set DBBYTE_API_KEY and DBBYTE_BUCKET before running.")
    sys.exit(1)

print(f"Testing against: {base_url or f'{DEFAULT_BASE_URL} (SDK default)'}")

db = DBByte(api_key=api_key, base_url=base_url or DEFAULT_BASE_URL)

test_key = f"sdk-roundtrip-{int(time.time() * 1000)}.txt"
test_content = b"dbbyte python sdk roundtrip test"

failures = 0


def step(name, fn):
    global failures
    print(f"{name}... ", end="")
    try:
        fn()
        print("ok")
    except DBByteError as e:
        failures += 1
        print("FAILED")
        print(f"  {e.status} {e.message}" + (f" ({e.hint})" if e.hint else ""))
        if e.retry_after is not None:
            print(f"  retry_after: {e.retry_after}s")
    except Exception as e:
        failures += 1
        print("FAILED")
        print(f"  {e}")


def check_health():
    res = db.health()
    if res["status"] not in ("ok", "degraded"):
        raise AssertionError(f"unexpected status: {res['status']}")


def check_upload():
    result = db.objects.upload(
        bucket, key=test_key, body=test_content, content_type="text/plain"
    )
    if not result.get("success"):
        raise AssertionError("upload did not report success")
    if result["name"] != test_key:
        raise AssertionError(f'expected name "{test_key}", got "{result["name"]}"')


def check_list():
    result = db.objects.list(bucket)
    found = next((f for f in result["files"] if f["name"] == test_key), None)
    if not found:
        raise AssertionError("uploaded file not found in list")


def check_download():
    result = db.objects.download(bucket, test_key)
    if result["data"] != test_content:
        raise AssertionError(f'content mismatch: got {result["data"]!r}')


def check_versions():
    result = db.objects.versions(bucket, test_key)
    if len(result["versions"]) < 1:
        raise AssertionError("expected at least one version")


signed_url = None


def check_sign():
    global signed_url
    result = db.objects.sign(bucket, test_key, expires_in=300)
    if not result.get("url"):
        raise AssertionError("no url returned")
    signed_url = result["url"]


def check_signed_url_fetchable():
    import urllib.request

    from dbbyte.client import USER_AGENT

    req = urllib.request.Request(signed_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as res:
        content = res.read()
        if content != test_content:
            raise AssertionError(f"content mismatch via signed url: got {content!r}")


def check_delete():
    result = db.objects.delete(bucket, test_key)
    if not result.get("success"):
        raise AssertionError("delete did not report success")


def check_download_after_delete():
    try:
        db.objects.download(bucket, test_key)
        raise AssertionError("expected download to fail after delete")
    except DBByteError as e:
        if e.status != 404:
            raise


step("health", check_health)
step("objects.upload", check_upload)
step("objects.list", check_list)
step("objects.download", check_download)
step("objects.versions", check_versions)
step("objects.sign", check_sign)
step("signed url is fetchable", check_signed_url_fetchable)
step("objects.delete", check_delete)
step("objects.download after delete returns 404", check_download_after_delete)

print("\nAll checks passed." if failures == 0 else f"\n{failures} check(s) failed.")
sys.exit(0 if failures == 0 else 1)
