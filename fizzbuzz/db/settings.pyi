from typing import Any, Final, Literal, TypeAlias

import aiosqlite

__author__: Final[str]
__license__: Final[str]

SettingsScope: TypeAlias = Literal["guild", "user", "global"]

class SettingsManager:
    def __init__(self) -> None: ...
    async def connect(self) -> aiosqlite.Connection: ...
    async def set_value(
        self,
        scope: SettingsScope,
        scope_id: int | str,
        key: str,
        value: object,
    ) -> None: ...
    async def get_value(
        self,
        scope: SettingsScope,
        scope_id: int | str,
        key: str,
    ) -> object | None: ...
    async def get_all(
        self, scope: SettingsScope, scope_id: int | str
    ) -> dict[str, Any]: ...
    async def delete_value(
        self, scope: SettingsScope, scope_id: int | str, key: str
    ) -> None: ...
    async def delete_scope(self, scope: SettingsScope, scope_id: int | str) -> None: ...

settings_manager: Final[SettingsManager]
