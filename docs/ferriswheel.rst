.. currentmodule:: ferris

FerrisWheel API Reference
=========================

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

Guild
-----

.. attributetable:: Guild

.. autoclass:: Guild
    :members:
    :inherited-members:

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

User
----

.. attributetable:: User

.. autoclass:: User
    :members:
    :inherited-members:

Utility Functions
-----------------

.. autofunction:: get_snowflake_creation_date

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

.. automodule:: errors
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
