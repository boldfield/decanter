import os

from webassets.loaders import YAMLLoader
from flask import Flask
from flask.ext.assets import Environment

from decanter import DIR
from decanter import settings, restrict
from decanter.app.handlers import admin, auth
from decanter import database


def create_app():
    app = Flask(__name__)
    settings.init_app(app)
    database.init_app(app)
    restrict.init_app(app)
    init_api_context(app)

    register_blueprints(app)
    register_assets(app)

    return app


def register_blueprints(app):
    app.register_blueprint(auth.plan)
    app.register_blueprint(admin.plan)


def init_api_context(app):
    def api_context():
        return dict(api_path=app.config.get('API_PATH'),
                    api_host=app.config.get('API_HOST'))
    app.context_processor(api_context)


def register_assets(app):
    app.assets = Environment(app)
    app.assets.auto_build = False
    app.assets.directory = os.path.join(DIR, 'assets')
    app.static_folder = os.path.join(DIR, 'static')
    app.assets.manifest = 'file'
    app.assets.url = '/static'

    manifest = YAMLLoader(os.path.join(DIR, 'assets', 'manifest.yaml'))
    manifest = manifest.load_bundles()
    [app.assets.register(n, manifest[n]) for n in manifest]
