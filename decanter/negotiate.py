from functools import wraps

from flask import request
from werkzeug.exceptions import UnsupportedMediaType, NotAcceptable


def wrap_support_types(fn, *mimetypes):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.mimetype not in mimetypes:
            raise UnsupportedMediaType()
        return fn(*args, **kwargs)
    return wrapper


def wrap_accept_types(fn, *mimetypes):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        best = request.accept_mimetypes.best_match(mimetypes)
        if best is None:
            raise NotAcceptable()
        request.best_mimetype = best
        return fn(*args, **kwargs)
    return wrapper


def supports(*mimetypes):
    def decorated(fn):
        return wrap_support_types(fn, *mimetypes)
    return decorated


def accepts(*mimetypes):
    def decorated(fn):
        return wrap_accept_types(fn, *mimetypes)
    return decorated
