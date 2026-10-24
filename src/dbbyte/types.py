from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class HealthChecks(TypedDict):
    api: Dict[str, Any]
    database: Dict[str, Any]


class HealthResponse(TypedDict):
    status: str  # "ok" | "degraded"
    timestamp: str
    uptimeSeconds: int
    checks: HealthChecks
    responseTimeMs: int


class UploadedObject(TypedDict):
    """Returned on a successful upload. Matches the storage server's
    real response shape exactly - not inferred."""

    success: bool
    key: str  # server-generated storage key, not the name you passed
    name: str  # the name you uploaded it as
    size: int
    mimeType: str
    fileId: str


class FileVersionPreview(TypedDict):
    key: str
    size: int
    mimeType: str
    isLatest: bool
    createdAt: str
    updatedAt: str


class FileListItem(TypedDict):
    key: str
    name: str
    size: int
    isPublic: bool
    createdAt: str
    updatedAt: str
    versionCount: int
    versions: List[FileVersionPreview]
    hasMoreVersions: bool


class ListObjectsResponse(TypedDict):
    files: List[FileListItem]
    nextCursor: Optional[str]
    hasMore: bool


class SignedUrlResponse(TypedDict):
    url: str
    expiresIn: int


class VersionEntry(TypedDict):
    versionKey: str
    size: int
    mimeType: str
    isLatest: bool
    isDeleted: bool
    createdAt: str
    updatedAt: str


class ListVersionsResponse(TypedDict):
    versions: List[VersionEntry]
    nextCursor: Optional[str]
    hasMore: bool


class _DeleteResponseOptional(TypedDict, total=False):
    # Only present when deleting every version at once.
    deletedVersions: int


class DeleteResponse(_DeleteResponseOptional):
    success: bool


class _DownloadResultOptional(TypedDict, total=False):
    filename: str


class DownloadResult(_DownloadResultOptional):
    data: bytes
    content_type: str


class Bucket(TypedDict):
    id: str
    name: str
    slug: str
    region: str
    replicaCount: int
    isPublic: bool
    cdn: bool
    versioningEnabled: bool
    fileCount: int
    size: int
    isDefault: bool
    createdAt: str
    updatedAt: str


class BucketListResponse(TypedDict):
    buckets: List[Bucket]


class BucketResponse(TypedDict, total=False):
    success: bool
    bucket: Bucket


class BucketDeleteResponse(TypedDict):
    success: bool


class PurgeResponse(TypedDict):
    success: bool
    purged: int
    failed: List[str]


DataRecord = Dict[str, Any]


class DataPage(TypedDict):
    data: List[DataRecord]
    next_cursor: Optional[str]


class DataRecordResponse(TypedDict):
    data: DataRecord


class AppendTextResponse(TypedDict):
    success: bool
    appendedCharacters: int


class DataDeleteResponse(TypedDict):
    success: bool


class UploadUrlResponse(TypedDict):
    """A short-lived direct-upload link. Send a request with `method` to
    `url`, adding `headers`, with the file bytes as the body."""

    url: str
    method: str
    headers: Dict[str, str]
    expiresIn: int
