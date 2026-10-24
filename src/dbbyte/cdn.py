from __future__ import annotations

from typing import Any, Dict, Optional

from .client import DBByteClient
from .types import PurgeResponse


class CdnResource:
    def __init__(self, client: DBByteClient) -> None:
        self._client = client

    def purge(
        self, slug: str, scope: str = "bucket", path: Optional[str] = None
    ) -> PurgeResponse:
        """Purge one public file (scope="file", with path) or every public
        file in a bucket (scope="bucket"). The API key needs write
        permission."""
        if scope not in ("file", "bucket"):
            raise ValueError('scope must be "file" or "bucket"')
        if scope == "file" and not path:
            raise ValueError('path is required when scope is "file"')
        body: Dict[str, Any] = {"slug": slug, "scope": scope}
        if path:
            body["path"] = path
        return self._client.request_json("POST", "/purge", body=body)  # type: ignore[no-any-return]
