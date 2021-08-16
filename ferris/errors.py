from aiohttp import ClientResponse

__all__ = (
    'FerrisException',
    'HTTPException',
    'BadRequest',
    'Unauthorized',
    'NotFound',
    'FerrisUnavailable',
)


class FerrisException(Exception):
    pass


class HTTPException(FerrisException):
    def __init__(self, resp: ClientResponse, content: str = None):
        content = content or resp.reason
        self.status_code = resp.status
        self.resp = resp
        super().__init__(content)


class BadRequest(HTTPException):
    pass


class Unauthorized(HTTPException):
    pass


class Forbidden(HTTPException):
    pass


class NotFound(HTTPException):
    pass


class FerrisUnavailable(HTTPException):
    pass
