from typing import Union

from .auth import *
from .base import *
from .channel import *
from .guild import *
from .member import *
from .message import *
from .role import *
from .user import *
from .ws import *

Data = Union[
    AuthResponse,
    ChannelPayload,
    GuildPayload,
    MemberPayload,
    MessagePayload,
    UserPayload,
]
