from __future__ import annotations

from typing import Any, Dict, Optional

from .client import DBByteClient
from .types import (
    DeleteResponse,
    DownloadResult,
    ListObjectsResponse,
    ListVersionsResponse,
    SignedUrlResponse,
    UploadedObject,
)
from .utils import encode_key


class ObjectsResource:
    def __init__(self, client: DBByteClient) -> None:
        self._client = client

    def upload(
        self,
        bucket: str,
        key: str,
        body: bytes,
        content_type: Optional[str] = None,
        overwrite: bool = False,
    ) -> UploadedObject:
        result = self._client.request_form(
            "POST",
            f"/storage/{bucket}/upload",
            filename=key,
            file_bytes=body,
            content_type=content_type,
            query={"overwrite": "true" if overwrite else None},
        )
        return result  # type: ignore[no-any-return]

    def list(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> ListObjectsResponse:
        result = self._client.request_json(
            "GET",
            f"/storage/{bucket}/list",
            query={"prefix": prefix, "cursor": cursor, "limit": limit},
        )
        return result  # type: ignore[no-any-return]

    def download(
        self,
        bucket: str,
        key: str,
        version: Optional[str] = None,
    ) -> DownloadResult:
        result = self._client.request_binary(
            "GET",
            f"/storage/{bucket}/download/{encode_key(key)}",
            query={"version": version},
        )
        return result  # type: ignore[return-value]

    def download_all_versions(self, bucket: str, key: str) -> DownloadResult:
        """Returns a zip of every version of this key."""
        result = self._client.request_binary(
            "GET",
            f"/storage/{bucket}/download/{encode_key(key)}",
            query={"version": "all"},
        )
        return result  # type: ignore[return-value]

    def delete(
        self,
        bucket: str,
        key: str,
        version: Optional[str] = None,
    ) -> DeleteResponse:
        result = self._client.request_json(
            "DELETE",
            f"/storage/{bucket}/delete/{encode_key(key)}",
            query={"version": version},
        )
        return result  # type: ignore[no-any-return]

    def delete_all_versions(self, bucket: str, key: str) -> DeleteResponse:
        """Permanently deletes every version of this key."""
        result = self._client.request_json(
            "DELETE",
            f"/storage/{bucket}/delete/{encode_key(key)}",
            query={"version": "all"},
        )
        return result  # type: ignore[no-any-return]

    def sign(
        self,
        bucket: str,
        key: str,
        version: Optional[str] = None,
        expires_in: Optional[int] = None,
    ) -> SignedUrlResponse:
        body: Dict[str, Any] = {}
        if version is not None:
            body["version"] = version
        if expires_in is not None:
            body["expiresIn"] = expires_in
        result = self._client.request_json(
            "POST",
            f"/storage/{bucket}/sign/{encode_key(key)}",
            body=body,
        )
        return result  # type: ignore[no-any-return]

    def versions(
        self,
        bucket: str,
        key: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> ListVersionsResponse:
        result = self._client.request_json(
            "GET",
            f"/storage/{bucket}/versions/{encode_key(key)}",
            query={"limit": limit, "cursor": cursor},
        )
        return result  # type: ignore[no-any-return]
