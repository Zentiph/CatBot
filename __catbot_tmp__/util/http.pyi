from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final, Literal

__author__: Final[str]
__license__: Final[str]

STATUS_OK: Literal[200]

class ApiError(RuntimeError): ...

@dataclass(frozen=True)
class ApiJsonResponse:
    status_code: int
    json: Any
    url: str

async def http_get_json(
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, Any] | None = None,
    timeout: float = 10.0,
) -> ApiJsonResponse: ...
async def http_get_bytes(
    url: str, *, headers: Mapping[str, str] | None = None, timeout: float = 10.0
) -> bytes: ...
