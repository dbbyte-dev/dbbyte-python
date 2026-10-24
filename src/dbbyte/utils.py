from __future__ import annotations

from urllib.parse import quote


def encode_key(key: str) -> str:
    """Object keys can contain slashes (e.g. "images/logo.png"). The
    API's catch-all routes expect each path segment encoded
    individually, then rejoined with "/" - encoding the whole key would
    also encode the slashes themselves."""
    return "/".join(quote(segment, safe="") for segment in key.split("/"))
