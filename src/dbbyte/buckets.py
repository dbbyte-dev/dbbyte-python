from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import quote

from .client import DBByteClient
from .types import (
    BucketDeleteResponse,
    BucketListResponse,
    BucketResponse,
)


class BucketsResource:
    def __init__(self, client: DBByteClient) -> None:
        self._client = client

    def list(self) -> BucketListResponse:
        return self._client.request_json("GET", "/buckets")  # type: ignore[no-any-return]

    def get(self, slug: str) -> BucketResponse:
        return self._client.request_json(  # type: ignore[no-any-return]
            "GET", f"/buckets/{quote(slug, safe='')}"
        )

    def create(
        self,
        name: str,
        region: str,
        replica_count: Optional[int] = None,
        is_public: Optional[bool] = None,
        cdn: Optional[bool] = None,
    ) -> BucketResponse:
        body: Dict[str, Any] = {"name": name, "region": region}
        if replica_count is not None:
            body["replicaCount"] = replica_count
        if is_public is not None:
            body["isPublic"] = is_public
        if cdn is not None:
            body["cdn"] = cdn
        return self._client.request_json("POST", "/buckets", body=body)  # type: ignore[no-any-return]

    def update(
        self,
        slug: str,
        versioning_enabled: Optional[bool] = None,
        is_public: Optional[bool] = None,
        cdn: Optional[bool] = None,
    ) -> BucketResponse:
        body: Dict[str, Any] = {}
        if versioning_enabled is not None:
            body["versioningEnabled"] = versioning_enabled
        if is_public is not None:
            body["isPublic"] = is_public
        if cdn is not None:
            body["cdn"] = cdn
        return self._client.request_json(  # type: ignore[no-any-return]
            "PATCH", f"/buckets/{quote(slug, safe='')}", body=body
        )

    def delete(self, slug: str) -> BucketDeleteResponse:
        return self._client.request_json(  # type: ignore[no-any-return]
            "DELETE", f"/buckets/{quote(slug, safe='')}"
        )
