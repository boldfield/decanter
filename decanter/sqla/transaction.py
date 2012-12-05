"""
decanter.sqlalchemy.transaction
===============================

.. currentmodule:: decanter.sqlalchemy.transaction

"""
from contextlib import contextmanager


@contextmanager
def transaction_session(session=None, auto_commit=False):
    """Context manager to facilitate atomic transactions. If any exception occurs
    over the course of the contained transaction, ``session.rollback()`` will
    be called.

    :param session: Session in which to execute transaction.
    :type session: :class:`decanter.database.db.session` instance or `None`.
    :param auto_commit: Whether or not to call ``session.commit()``
                        automatically when the context exits.
    :type auto_commit: boolean, defaults to `False`.
    """
    from decanter.database import db
    session = session or db.session
    try:
        yield session
    # Catch any and every exception and execute a rollback
    except Exception, e:
        session.rollback()
        # Now re-raise the exception to let it continue to bubble up
        raise e
    if auto_commit:
        session.commit()
