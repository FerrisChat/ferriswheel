.. currentmodule:: ferris

FerrisWheel API Reference
=========================


Create User
-----------

.. autofunction:: ferris.create_user

Client
------

.. attributetable:: Client

.. autoclass:: Client
    :members:

Base
----

.. autoclass:: SnowflakeObject
    :members:

.. autoclass:: BaseObject
    :members:
    :inherited-members:

.. autoclass:: Object
    :members:
    :inherited-members:

Channnel
--------

.. attributetable:: Channel

.. autoclass:: Channel
    :members:
    :inherited-members:

Event Reference
----------------

This section outlines all the events listeners can subscribe to.

For more details on listening to events, see :class:`client`.

All listeners must be a |coroutine_link|.

.. function:: on_login()

    Called when the client logs in.

.. function:: on_connect()

    Called when the client connects to the FerrisChat's websocket.

    .. warning::
        This does not mean the client is ready to use.

.. function on_ready()

    Called when the client is ready to use.

    .. warning::
        We do not guarantee that this will only be called once.
        Since the library implemented reconnect logic, this may
        cause this to be called multiple times.

.. function:: on_close()

    Called when the client is closing.
    This can be used as resource cleanup / release.

.. function:: on_message(message)

    Called when a message is sent in a channel.

.. function:: on_message_edit(old, new)

    Called when a message is edited.

    :param old: The old :class:`~Message`.
    :param new: The new :class:`~message`.

.. function on_message_delete(message)

    Called when a message is deleted.

    :param message: The :class:`~Message` that was deleted.

.. function on_channel_create(channel)

    Called when a channel is created.

    :param channel: The :class:`~Channel` that was created.

.. function on_channel_edit(old, new)

    Called when a channel is edited.

    :param old: The old :class:`~Channel`.
    :param new: The new :class:`~Channel`.

.. function on_channel_delete(channel)

    Called when a channel is deleted.

    :param channel: The :class:`~Channel` that was deleted.

.. function on_member_join(member)

    Called when a member joins a channel.

    :param member: The :class:`~Member` that joined.

.. function on_member_edit(old, new)

    Called when a member is edited.

    :param old: The old :class:`~Member`.
    :param new: The new :class:`~Member`.

.. function on_member_leave(member)

    Called when a member leaves a guild.

    :param member: The :class:`~Member` that left.

.. function on_user_create(user)

    Called when a user is created.

    :param user: The :class:`~User` that was created.



Guild
-----

.. attributetable:: Guild

.. autoclass:: Guild
    :members:
    :inherited-members:

Invite
------

.. attributetable:: Invite

.. autoclass:: Invite
    :members:

Member
------

.. attributetable:: Member

.. autoclass:: Member
    :members:
    :inherited-members:

Message
-------

.. attributetable:: Message

.. autoclass:: Message
    :members:
    :inherited-members:

Users
-----

.. attributetable:: User

.. autoclass:: User
    :members:
    :inherited-members:

.. attributetable:: PartialUser

.. autoclass:: PartialUser
    :members:
    :inherited-members:

Utility Functions
-----------------

.. autofunction:: get_snowflake_creation_date

.. autofunction:: find

Enumerations
------------

.. class:: ModelType
    Specifics a model's type.

    .. attribute:: Guild
        A guild model

    .. attribute:: User
        A user model

    .. attribute:: Channel
        A channel model

    .. attribute:: Member
        A member model


Exceptions
----------

.. automodule:: ferris.errors
    :members:



Exception Hierarchy
-------------------

- :exc:`Exception`
    - :exc:`FerrisException`
        - :exc:`HTTPException`
            - :exc:`BadRequest`
            - :exc:`Unauthorized`
            - :exc:`Forbidden`
            - :exc:`NotFound`
            - :exc:`FerrisUnavailable`