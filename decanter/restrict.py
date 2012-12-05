from datetime import timedelta
from functools import update_wrapper

from werkzeug.exceptions import Forbidden
from flask import make_response, request, current_app


def init_app(app):
    whitelist = app.config.get('WHITELIST')
    blacklist = app.config.get('BLACKLIST')

    if not whitelist and not blacklist:
        return

    app.wsgi_app = RestrictMiddleware(app.wsgi_app,
                                      whitelist=whitelist,
                                      blacklist=blacklist)


class RestrictMiddleware(object):

    def __init__(self, app, whitelist=None, blacklist=None):
        self.app = app
        self.whitelist = whitelist or []
        self.blacklist = blacklist or []

    def __call__(self, environ, start_response):
        if not self.whitelist and not self.blacklist:
            return self.app(environ, start_response)

        environ = environ or dict()
        ips = environ.get('HTTP_X_FORWARDED_FOR', '').split(',')
        ip = None

        if ips:
            ip = ips[0].strip()

        if not ip:
            ip = environ.get('REMOTE_ADDR') or None

        allowed = self.is_whitelisted(ip)
        allowed = allowed and not self.is_blacklisted(ip)

        if not allowed:
            return Forbidden()(environ, start_response)

        return self.app(environ, start_response)

    def is_whitelisted(self, ip):
        if not self.whitelist:
            return True

        if not ip:
            return False

        return ip in self.whitelist

    def is_blacklisted(self, ip):
        if not self.blacklist:
            return False

        if not ip:
            return False

        return ip in self.blacklist


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator
