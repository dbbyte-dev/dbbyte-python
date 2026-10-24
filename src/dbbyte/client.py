from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Any, Dict, NoReturn, Optional

from .errors import DBByteError

DEFAULT_BASE_URL = "https://api.dbbyte.com"
DEFAULT_TIMEOUT = 30.0
USER_AGENT = "dbbyte-python/0.1.0"


class DBByteClient:
    """Thin HTTP wrapper. Paths passed to request_* do NOT include /v1 -
    in production the Cloudflare Worker gateway in front of
    api.dbbyte.com inserts /api/v1 itself. If you point base_url at a
    Next.js dev server directly (bypassing the Worker), include /api/v1
    in base_url instead."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        if not api_key:
            raise ValueError("DBByte: api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _build_url(self, path: str, query: Optional[Dict[str, Any]] = None) -> str:
        url = f"{self.base_url}{path}"
        if query:
            filtered = {k: v for k, v in query.items() if v is not None}
            if filtered:
                url += "?" + urllib.parse.urlencode(filtered)
        return url

    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": USER_AGENT,
        }
        if extra:
            headers.update(extra)
        return headers

    def _raise_for_error(self, e: urllib.error.HTTPError) -> NoReturn:
        raw = e.read()
        retry_after = None
        ra_header = e.headers.get("Retry-After") if e.headers else None
        if ra_header is not None:
            try:
                retry_after = int(ra_header)
            except ValueError:
                retry_after = None
        message = e.reason
        hint = None
        try:
            body = json.loads(raw.decode("utf-8"))
            message = body.get("error", message)
            hint = body.get("hint")
        except (ValueError, UnicodeDecodeError):
            # Non-JSON body: this didn't come from the DBByte API itself
            # (which always returns {"error": ...}) - likely blocked
            # upstream, e.g. by Cloudflare's edge/WAF before reaching
            # the app.
            hint = "Response was not JSON - request may have been blocked before reaching the API"
        raise DBByteError(message, e.code, hint, retry_after) from None

    def request_json(
        self,
        method: str,
        path: str,
        query: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = self._build_url(path, query)
        data = None
        headers = self._headers()
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                raw = res.read()
                return json.loads(raw.decode("utf-8")) if raw else None
        except urllib.error.HTTPError as e:
            self._raise_for_error(e)
        except urllib.error.URLError as e:
            raise DBByteError(f"Request failed: {e.reason}", 0) from None

    def request_form(
        self,
        method: str,
        path: str,
        filename: str,
        file_bytes: bytes,
        content_type: Optional[str],
        query: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = self._build_url(path, query)
        boundary = uuid.uuid4().hex
        ct = content_type or "application/octet-stream"
        # Filename is only escaped for embedded quotes, matching the
        # Node SDK's simplicity - the server is the source of truth for
        # what filenames it accepts.
        safe_filename = filename.replace('"', '\\"')
        parts = [
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="file"; '
                f'filename="{safe_filename}"\r\n'
                f"Content-Type: {ct}\r\n\r\n"
            ).encode(),
            file_bytes,
            f"\r\n--{boundary}--\r\n".encode(),
        ]
        data = b"".join(parts)

        headers = self._headers(
            {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        )
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                raw = res.read()
                return json.loads(raw.decode("utf-8")) if raw else None
        except urllib.error.HTTPError as e:
            self._raise_for_error(e)
        except urllib.error.URLError as e:
            raise DBByteError(f"Request failed: {e.reason}", 0) from None

    def request_binary(
        self,
        method: str,
        path: str,
        query: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = self._build_url(path, query)
        req = urllib.request.Request(url, headers=self._headers(), method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                data = res.read()
                content_type = res.headers.get(
                    "Content-Type", "application/octet-stream"
                )
                disposition = res.headers.get("Content-Disposition")
                filename = None
                if disposition and "filename=" in disposition:
                    filename = disposition.split("filename=", 1)[1].strip('"')
                result: Dict[str, Any] = {"data": data, "content_type": content_type}
                if filename:
                    result["filename"] = filename
                return result
        except urllib.error.HTTPError as e:
            self._raise_for_error(e)
        except urllib.error.URLError as e:
            raise DBByteError(f"Request failed: {e.reason}", 0) from None
