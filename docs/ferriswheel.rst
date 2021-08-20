FerrisWheel API Reference
=========================

Client
------
.. autoclass:: ferris.Client
    :members:

Base
----
.. autoclass:: ferris.Base
    :members:

Channnel
--------
.. autoclass:: ferris.Channel
    :members:
    :inherited-members:

Guild
-----
.. autoclass:: ferris.Guild
    :members:
    :inherited-members:

Member
------
.. autoclass:: ferris.Member
    :members:
    :inherited-members:

Message
-------
.. autoclass:: ferris.Message
    :members:
    :inherited-members:

User
----
.. autoclass:: ferris.User
    :members:
    :inherited-members:

Utility Functions
-----------------
.. autofunction:: ferris.get_snowflake_creation_date

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


Exception Hierarchy
-------------------
- :exc:`Exception`
    - :exc:`ferris.FerrisException`
        - :exc:`ferris.HTTPException`
            - :exc:`ferris.BadRequest`
            - :exc:`ferris.Unauthorized`
            - :exc:`ferris.Forbidden`
            - :exc:`ferris.NotFound`
            - :exc:`ferris.FerrisUnavailable`
