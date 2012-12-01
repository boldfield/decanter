import os

from webassets.loaders import YAMLLoader
from flask import Flask
from flask.ext.admin import Admin
from flask.ext.assets import Environment

from decanter import DIR
from decanter.app.handlers import base_handler
from decanter.app.handlers.admin import (AdminIndexHandler,
                                         PostAdminHandler,
                                         PostCreateHandler,
                                         PostEditHandler,
                                         LogoutHandler)


def create_app():
    app = Flask(__name__)
    app.config.from_object('decanter.settings')
    # This seems... weird
    app.debug = app.config['DEBUG']

    register_admin(app)
    register_assets(app)
    return app


def register_blueprints(app):
    from decanter.app.handlers import authentication_handler
    app.register_blueprint(base_handler)
    app.register_blueprint(authentication_handler)


def register_admin(app):
    admin = Admin(app, index_view=AdminIndexHandler())
    admin.add_view(PostAdminHandler(name='Posts', endpoint='posts'))
    admin.add_view(PostCreateHandler(name='Create Post', endpoint='posts/create'))
    admin.add_view(PostEditHandler(name='Edit Post', endpoint='posts/edit'))
    admin.add_view(LogoutHandler(name='Logout', endpoint='logout'))


def register_assets(app):
    app.assets = Environment(app)
    app.assets.auto_build = False
    app.assets.directory = os.path.join(DIR, 'assets')
    app.assets.manifest = 'file'
    app.assets.url = '/static'

    manifest = YAMLLoader(os.path.join(DIR, 'assets', 'manifest.yaml'))
    manifest = manifest.load_bundles()
    [app.assets.register(n, manifest[n]) for n in manifest]
