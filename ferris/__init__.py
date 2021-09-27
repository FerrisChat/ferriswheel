__author__ = 'Cryptex & jay3332'
__version__ = '0.0.a2'
# 0.1.0 for the finished release


from .base import *
from .channel import *
from .client import *
from .connection import *
from .enums import *
from .errors import *
from .guild import *
from .http import *
from .member import *
from .message import *
from .user import *
from .utils import *


import urllib.request


def create_user(username: str, password: str, email: str) -> PartialUser:
    """
    Creates a new user.

    Parameters
    ----------
    username: str
        The user's username.
    password: str
        The user's password.
    email: str
        The user's email.

    Returns
    -------
    PartialUser
        The created user.
    """
    resp = urllib.request.urlopen(
        urllib.request.Request(
            f'{HTTPClient.API_BASE_URL}/users',
            data=to_json(
                {'email': email, 'password': password, 'username': username}
            ).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
    )
    content = resp.read().decode('utf-8')
    js = from_json(content)

    return PartialUser(js)
