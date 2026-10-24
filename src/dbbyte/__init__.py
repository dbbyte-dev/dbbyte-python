from __future__ import annotations

from typing import Optional

from .client import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DBByteClient
from .errors import DBByteError
from .buckets import BucketsResource
from .cdn import CdnResource
from .data import DataResource
from .objects import ObjectsResource
from .types import (
    AppendTextResponse,
    Bucket,
    BucketDeleteResponse,
    BucketListResponse,
    BucketResponse,
    DataDeleteResponse,
    DataPage,
    DataRecord,
    DataRecordResponse,
    PurgeResponse,
    UploadUrlResponse,
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
    "Bucket",
    "BucketListResponse",
    "BucketResponse",
    "BucketDeleteResponse",
    "PurgeResponse",
    "DataRecord",
    "DataPage",
    "DataRecordResponse",
    "AppendTextResponse",
    "DataDeleteResponse",
    "UploadUrlResponse",
]


class DBByte:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._client = DBByteClient(api_key, base_url, timeout)
        self.buckets = BucketsResource(self._client)
        self.cdn = CdnResource(self._client)
        self.data = DataResource(self._client)
        self.objects = ObjectsResource(self._client)

    def health(self) -> HealthResponse:
        result = self._client.request_json("GET", "/health")
        return result  # type: ignore[no-any-return]
