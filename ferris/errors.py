from aiohttp import ClientResponse

__all__ = ('FerrisException', 'HTTPException', 'Unauthorized', 'NotFound', 'FerrisUnavailable')

class FerrisException(Exception):
    pass

class HTTPException(FerrisException):
    pass

class Unauthorized(HTTPException):
    def __init__(self, resp: ClientResponse, content: str):
        self.status_code = resp.status_code
        self.resp = resp
        super().__init__(content)

class Forbidden(HTTPException):
    def __init__(self, resp: ClientResponse, content: str):
        self.status_code = resp.status_code
        self.resp = resp
        super().__init__(content)

class NotFound(HTTPException):
    def __init__(self, resp: ClientResponse, content: str):
        self.status_code = resp.status_code
        self.resp = resp
        super().__init__(content)

class FerrisUnavailable(HTTPException):
    def __init__(self, resp: ClientResponse, content: str):
        self.status_code = resp.status_code
        self.resp = resp
        super().__init__(content)

