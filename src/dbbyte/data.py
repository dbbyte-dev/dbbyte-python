from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import quote

from .client import DBByteClient
from .types import (
    AppendTextResponse,
    DataDeleteResponse,
    DataPage,
    DataRecord,
    DataRecordResponse,
)


def _seg(value: str) -> str:
    return quote(value, safe="")


class DataResource:
    """Serve data APIs published from CSV, JSON, or Google Docs."""

    def __init__(self, client: DBByteClient) -> None:
        self._client = client

    def get(
        self,
        slug: str,
        fields: Optional[List[str]] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        filters: Optional[Dict[str, str]] = None,
    ) -> DataPage:
        query: Dict[str, Any] = dict(filters or {})
        if fields:
            query["fields"] = ",".join(fields)
        query["cursor"] = cursor
        query["limit"] = limit
        return self._client.request_json(  # type: ignore[no-any-return]
            "GET", f"/v1/data/{_seg(slug)}", query=query
        )

    def create(self, slug: str, record: DataRecord) -> DataRecordResponse:
        return self._client.request_json(  # type: ignore[no-any-return]
            "POST", f"/v1/data/{_seg(slug)}", body=record
        )

    def append_text(self, slug: str, text: str) -> AppendTextResponse:
        return self._client.request_json(  # type: ignore[no-any-return]
            "POST", f"/v1/data/{_seg(slug)}", body={"appendText": text}
        )

    def update(
        self, slug: str, record_id: str, patch: DataRecord
    ) -> DataRecordResponse:
        return self._client.request_json(  # type: ignore[no-any-return]
            "PATCH", f"/v1/data/{_seg(slug)}/{_seg(record_id)}", body=patch
        )

    def delete(self, slug: str, record_id: str) -> DataDeleteResponse:
        return self._client.request_json(  # type: ignore[no-any-return]
            "DELETE", f"/v1/data/{_seg(slug)}/{_seg(record_id)}"
        )
