from __future__ import annotations

from typing import Optional


class DBByteError(Exception):
    """Raised on any DBByte API error.

    The API returns {"error": str, "hint"?: str} on failure. There is no
    "code" field - do not rely on one.

    A 429 can mean two different things and only one is retryable:
      - Burst rate limit: retry_after is set (seconds until you can
        retry). Transient, safe to retry after that delay.
      - Plan API request quota exceeded: retry_after is None. Retrying
        immediately won't help until the billing period resets or the
        plan is upgraded.
    """

    def __init__(
        self,
        message: str,
        status: int,
        hint: Optional[str] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
        self.hint = hint
        self.retry_after = retry_after

    def __repr__(self) -> str:
        return (
            f"DBByteError(status={self.status!r}, message={self.message!r}, "
            f"hint={self.hint!r}, retry_after={self.retry_after!r})"
        )
