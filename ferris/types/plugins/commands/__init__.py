from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Tuple, Any, Dict

__all__ = ('ParserCallbackProto',)

if TYPE_CHECKING:
    from ferris.plugins.commands import Context


class ParserCallbackProto(Protocol):
    def __call__(self, ctx: Context, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
        ...
