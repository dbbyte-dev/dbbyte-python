# dbbyte

Official DBByte SDK for Python. A thin, typed wrapper over the DBByte v1 REST API. Standard library only - no dependencies.

## Status

Covers object storage: upload, list, download, delete, versioning, and signed URLs. There is no bucket management, CDN cache control, or analytics API yet - those aren't part of the v1 REST API, so they aren't in the SDK.

## Installation

```bash
pip install dbbyte
```

Requires Python 3.9+.

## Usage

```python
import os
from dbbyte import DBByte

db = DBByte(api_key=os.environ["DBBYTE_API_KEY"])
```

| Argument | Type | Description |
| --- | --- | --- |
| `api_key` | `str` | Your DBByte API key. Required. |
| `base_url` | `str` | Override the API base URL. Defaults to `https://api.dbbyte.com`. |
| `timeout` | `float` | Request timeout in seconds. Defaults to `30.0`. |

### Health check

```python
status = db.health()
```

### Upload

```python
with open("logo.png", "rb") as f:
    body = f.read()

obj = db.objects.upload(
    "my-bucket",
    key="images/logo.png",
    body=body,
    content_type="image/png",
)

# Re-uploading the same name fails with 409 unless you opt in:
db.objects.upload("my-bucket", key="images/logo.png", body=body, overwrite=True)
```

### List

```python
result = db.objects.list("my-bucket")
files = result["files"]

# Paginate:
next_page = db.objects.list("my-bucket", cursor=result["nextCursor"])
```

### Download

```python
result = db.objects.download("my-bucket", "images/logo.png")
data = result["data"]  # bytes

# A specific historical version:
db.objects.download("my-bucket", "images/logo.png", version="some-version-key")

# Every version, zipped:
zip_result = db.objects.download_all_versions("my-bucket", "images/logo.png")
```

### Versions

```python
result = db.objects.versions("my-bucket", "images/logo.png")
```

### Signed URLs

```python
result = db.objects.sign("my-bucket", "images/logo.png", expires_in=3600)  # max 604800 (7 days)
url = result["url"]
```

### Delete

```python
db.objects.delete("my-bucket", "images/logo.png")

# A specific version only:
db.objects.delete("my-bucket", "images/logo.png", version="some-version-key")

# Every version, permanently:
db.objects.delete_all_versions("my-bucket", "images/logo.png")
```

## Error handling

All SDK methods raise a `DBByteError` on API errors.

```python
from dbbyte import DBByte, DBByteError

db = DBByte(api_key=os.environ["DBBYTE_API_KEY"])

try:
    db.objects.download("my-bucket", "does-not-exist.png")
except DBByteError as e:
    print(e.status)   # e.g. 404
    print(e.message)  # e.g. "File not found"
    print(e.hint)     # present on some errors, e.g. upload conflicts
```

### Rate limits vs quota limits

A `429` can mean two different things, and only one is worth retrying:

- **Burst rate limit** - `e.retry_after` is set (seconds until you can retry). Transient, safe to retry after that delay.
- **Plan API request quota exceeded** - `e.retry_after` is `None`. Retrying immediately won't help; you're out of quota until your billing period resets or you upgrade.

```python
except DBByteError as e:
    if e.status == 429:
        if e.retry_after is not None:
            # wait e.retry_after seconds, then retry
            pass
        else:
            # plan quota exceeded, don't retry blindly
            pass
```

## Known limitations

- **Upload allowed types**: the server enforces a fixed MIME type whitelist (common image, video, audio, PDF, Word, and plain-text formats). Uploading anything else returns a `400` from the server - the SDK doesn't pre-validate this client-side.
- **50MB max file size**, enforced server-side.
- **Synchronous only.** No async client yet.

## License

MIT
