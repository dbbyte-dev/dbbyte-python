from __future__ import annotations

from typing import Optional

from .client import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DBByteClient
from .errors import DBByteError
from .objects import ObjectsResource
from .types import (
    DeleteResponse,
    DownloadResult,
    FileListItem,
    FileVersionPreview,
    HealthResponse,
    ListObjectsResponse,
    ListVersionsResponse,
    SignedUrlResponse,
    UploadedObject,
    VersionEntry,
)

__all__ = [
    "DBByte",
    "DBByteError",
    "HealthResponse",
    "UploadedObject",
    "ListObjectsResponse",
    "FileListItem",
    "FileVersionPreview",
    "SignedUrlResponse",
    "ListVersionsResponse",
    "VersionEntry",
    "DeleteResponse",
    "DownloadResult",
]


class DBByte:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._client = DBByteClient(api_key, base_url, timeout)
        self.objects = ObjectsResource(self._client)

    def health(self) -> HealthResponse:
        result = self._client.request_json("GET", "/health")
        return result  # type: ignore[no-any-return]
