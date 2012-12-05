from werkzeug.exceptions import Forbidden


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
