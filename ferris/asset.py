from __future__ import annotations

# Some of the code here are shamelessly robbed from dpy.

from os import PathLike
from typing import AnyStr, Union, TYPE_CHECKING, Any
from io import BufferedIOBase


__all__ = ('Asset',)

if TYPE_CHECKING:
    from .connection import Connection


class Asset:
    def __init__(self, connection: Connection, url: str) -> None:
        self._connection = connection

        self._url: str = url

    async def read(self) -> bytes:
        """|coro|
        Retrives the content of this asset as a :class:`bytes` object.

        Raises
        ------
        HTTPException
            An HTTP error occurred while fetching the content.

        Returns
        -------
        :class:`bytes`
        """
        return await self._connection._http.get_asset(self._url)

    async def save(
        self, fp: Union[AnyStr, PathLike, BufferedIOBase], *, seek_begin: bool = True
    ) -> int:
        """|coro|
        Saves the asset to a file-like object.

        Parameters
        ----------
        fp: Union[AnyStr, PathLike, BufferedIOBase]
            The file-like object to save the asset to.

        seek_begin: bool
            Whether to seek to the beginning of the file after saving.
            Defaults to ``True``.
        """
        data = await self.read()

        if isinstance(fp, BufferedIOBase):
            written = await self._connection.to_thread(fp.write, data)
            if seek_begin:
                fp.seek(0)

            return written

        with open(fp, 'wb+') as f:
            return await self._connection.to_thread(f.write, data)

    def __str__(self) -> str:
        return self._url

    def __repr__(self) -> str:
        return f'<Asset url={self._url!r}>'

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Asset) and self._url == other._url

    def __len__(self) -> int:
        return len(self._url)

    def __hash__(self) -> int:
        return hash(self._url)
