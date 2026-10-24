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
