from aiohttp import ClientResponse

__all__ = (
    'FerrisException',
    'HTTPException',
    'Unauthorized',
    'NotFound',
    'FerrisUnavailable',
)


class FerrisException(Exception):
    def __init__(self, content: str):
        self.content = content


class HTTPException(FerrisException):
    def __init__(self, resp: ClientResponse, content: str):
        self.status_code = resp.status
        self.resp = resp
        super().__init__(content)


class Unauthorized(HTTPException):
    pass


class Forbidden(HTTPException):
    pass


class NotFound(HTTPException):
    pass


class FerrisUnavailable(HTTPException):
    pass
