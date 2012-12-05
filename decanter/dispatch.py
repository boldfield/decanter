from threading import Lock

from werkzeug.wsgi import pop_path_info, peek_path_info

from decanter import settings
from decanter.util import LoginManagerMixin


class SubdomainDispatcher(object, LoginManagerMixin):

    def __init__(self, create_app, default_app):
        self.domain = settings.DOMAIN
        self.create_app = create_app
        self.default_app = default_app
        self.lock = Lock()
        self.instances = {}

    def get_application(self, host):
        host = host.split(':')[0]
        assert host.endswith(self.domain), 'Domain configuration error, unknown domain: %s' % host
        subdomain = host[:-len(self.domain)].rstrip('.')
        with self.lock:
            app = self.instances.get(subdomain)
            if app is None:
                app = self.create_app(subdomain)
                if app is None:
                    return None, subdomain
                self.setup_login_manager(app)
                self.cache_app(subdomain, app)
            return app, subdomain

    def cache_app(self, subdomain, app):
        self.instances[subdomain] = app

    def __call__(self, environ, start_response):
        app, subdomain = self.get_application(environ['HTTP_HOST'])
        return app(environ, start_response)


class PathDispatcher(object, LoginManagerMixin):

    def __init__(self, create_app, default_app):
        from decanter import STRIP_PATHS
        self.strip_paths = STRIP_PATHS
        self.create_app = create_app
        self.default_app = default_app
        self.lock = Lock()
        self.instances = {}

    def get_application(self, path):
        with self.lock:
            app = self.instances.get(path)
            if app is None:
                app = self.create_app(path)
                if app is None:
                    return None, path
                self.setup_login_manager(app)
                self.cache_app(path, app)
            return app, path

    def cache_app(self, path, app):
        self.instances[path] = app

    def __call__(self, environ, start_response):
        app, path = self.get_application(peek_path_info(environ))
        if app is not None:
            if path in self.strip_paths:
                pop_path_info(environ)
        else:
            app = self.default_app()
            self.setup_login_manager(app)
            self.cache_app(path, app)
        return app(environ, start_response)
