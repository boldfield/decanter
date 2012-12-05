import os
from threading import Lock

DIR = os.path.abspath(__file__)
DIR = os.path.dirname(DIR)

from werkzeug.wsgi import pop_path_info, peek_path_info

from decanter.app import create_app as create_web_app
from decanter.api import create_app as create_api_app
from decanter.util import LoginManagerMixin

STRIP_PATHS = ('api', 'admin')


class Decanter(object, LoginManagerMixin):
    _strip_paths = STRIP_PATHS

    def __init__(self,
                 default_app,
                 admin_subdomain=None,
                 admin_prefix=None,
                 api_subdomain=None,
                 api_prefix=None):

        self.lock = Lock()
        self.default_app = default_app
        self.path_instances = dict()
        self.subdomain_instances = dict()
        self.default_instances = dict()

        self.subdomains = dict()
        self.paths = dict()

        self.strip_paths = list()
        for path in self._strip_paths:
            self.strip_paths.append(path)

        if admin_subdomain:
            self.subdomains[admin_subdomain] = create_web_app
        if api_subdomain:
            self.subdomains[admin_subdomain] = create_api_app

        self.paths[admin_prefix or 'admin'] = create_web_app
        self.paths[api_prefix or 'api'] = create_api_app

    def __call__(self, environ, start_response):
        host = environ['HTTP_HOST']
        subdomain = self._subdomain(host)
        path = peek_path_info(environ)

        if subdomain in self.subdomains:
            app = self.get_application_by_subdomain(subdomain)
        else:
            app = self.get_application_by_path(path)

        if app is None:
            app = self.default_instances.get(subdomain)
            if app is None:
                app = self.default_app()
                self.setup_login_manager(app)
                self.default_instances[subdomain] = app

        if path in self.strip_paths:
            pop_path_info(environ)

        return app(environ, start_response)

    def register_app(self, create_app, subdomain=None, path=None, strip_path=False):
        if subdomain:
            self.subdomains[subdomain] = create_app
        if path:
            self.paths[path] = create_app
        if strip_path:
            self.strip_paths.append(path)

    def get_application_by_path(self, path):
        with self.lock:
            app = self.path_instances.get(path)
            if app is None:
                create_app = self.paths.get(path)
                if create_app is None:
                    return None
                app = create_app()
                self.setup_login_manager(app)
                self.path_instances[path] = app
            return app

    def get_application_by_subdomain(self, subdomain):
        with self.lock:
            app = self.instances.get(subdomain)
            if app is None:
                create_app = self.subdomains.get(subdomain)
                if create_app is None:
                    return None
                app = create_app()
                self.setup_login_manager(app)
                self.subdomain_instances[subdomain] = app
            return app

    def _subdomain(self, host):
        host = host.split(':')[0]
        parts = host.split('.')
        if len(parts) < 3:
            return ''

        subdomain = parts[0]
        return subdomain if subdomain != 'stage' else parts[1]


app = Decanter(create_web_app)
