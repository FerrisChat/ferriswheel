from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .base import BaseObject


if TYPE_CHECKING:
    from typing_extensions import Self
    from .connection import Connection
    from .types import Data, Snowflake
    from .types.role import RolePayload
    from .guild import Guild


__all__ = ("Role",)


class Role(BaseObject):
    """Represents a role object in FerrisChat."""

    __all__ = ('_guild_id', '_name', '_color', '_position', '_permissions')

    def __init__(self, connection: Connection, data: Optional[RolePayload], /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Optional[RolePayload], /) -> None:
        if not data:
            data: dict = {}

        self._store_snowflake(data.get('id'))

        self._guild_id: Snowflake = data.get('guild_id')
        self._name: str = data.get('name')
        self._color: int = data.get('color')
        self._position: int = data.get('position')
        # TODO: self.permissions

    @property
    def guild(self) -> Optional[Guild]:
        """The guild the role is in."""
        return self._connection.get_guild(self.guild_id)

    @property
    def guild_id(self) -> Snowflake:
        """The ID of the guild the role is in."""
        return self._guild_id

    @property
    def name(self) -> str:
        """The name of the role."""
        return self._name

    @property
    def color(self) -> int:
        """The color of the role."""
        return self._color

    @property
    def position(self) -> int:
        """The position of the role."""
        return self._position

    @property
    def permissions(self) -> int:
        """The permissions of the role."""
        return self._permissions

    async def edit(
        self,
        *,
        name: str = None,
        color: int = None,
        position: int = None,
        permissions: int = None,
    ) -> Self:
        """Edits the role.

        Parameters
        ----------
        name: str
            The new name of the role.
        color: int
            The new color of the role.
        position: int
            The new position of the role.
        permissions: int
            The new permissions of the role.


        Returns
        -------
        :class:`~Role`
        """
        payload = {
            'name': name,
            'color': color,
            'position': position,
            'permissions': permissions,
        }
        r = (
            await self._connection.api.guilds(self.guild_id)
            .roles(self.id)
            .patch(json=payload)
        )
        self._process_data(r)

        return self

    async def delete(self) -> None:
        """Deletes the role."""
        await self._connection.api.guilds(self.guild_id).roles(self.id).delete()
