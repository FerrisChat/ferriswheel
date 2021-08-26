from typing import TypedDict

__all__ = ('AuthResponse',)


class AuthResponse(TypedDict):
    token: str
