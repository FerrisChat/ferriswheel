from typing import Optional

from aiohttp import ClientResponse

__all__ = (
    'FerrisException',
    'HTTPException',
    'BadRequest',
    'Unauthorized',
    'Forbidden',
    'NotFound',
    'FerrisServerError',
    'FerrisUnavailable',
    'WebsocketException',
    'MissingImplementation',
    'Reconnect',
)


class FerrisException(Exception):
    """Base class for all ferriswheel-originated exceptions.
    Theoretically, you could use this exception to catch all ferris exceptions.
    """

    pass


class HTTPException(FerrisException):
    """
    Base class for all ferris HTTP exceptions.

    Attributes
    ----------
    status: int
        The status code of the response.
    resp: :class:`aiohttp.ClientResponse`
        The aiohttp response object.
    """

    def __init__(self, resp: ClientResponse, content: Optional[str] = None):
        content = content or resp.reason
        self.status = resp.status
        self.resp = resp
        super().__init__(content)


class BadRequest(HTTPException):
    """The request was invalid or cannot be otherwise served."""

    pass


class Unauthorized(HTTPException):
    """The request requires user authentication."""

    pass


class Forbidden(HTTPException):
    """The request was a valid request,
    but the server is refusing to respond to it, as you don't have enough permissions to do that.
    """

    pass


class NotFound(HTTPException):
    """The server cannot find what you requesed for."""

    pass


class MissingImplementation(HTTPException):
    """You just discovered Ferris at work! Don't tell anybody, but this is planned for the future!"""

    pass


class FerrisServerError(HTTPException):
    """Ferris is currently unavailable. Looks like a JS rabbit got into the server."""

    pass


class FerrisUnavailable(HTTPException):
    """SSHHH! Ferris is sleeping, and can't answer the request right now.
    Try again later.
    """

    pass


class WebsocketException(FerrisException):
    """Base class for all websocket exceptions."""

    pass


class Reconnect(WebsocketException):
    """Signal to reconnect to the websocket."""

    pass
