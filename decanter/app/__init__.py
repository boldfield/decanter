from flask import Flask
from flask.ext.admin import Admin

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

    admin = Admin(app, index_view=AdminIndexHandler())
    admin.add_view(PostAdminHandler(name='Posts', endpoint='posts'))
    admin.add_view(PostCreateHandler(name='Create Post', endpoint='posts/create'))
    admin.add_view(PostEditHandler(name='Edit Post', endpoint='posts/edit'))
    admin.add_view(LogoutHandler(name='Logout', endpoint='logout'))

    return app


def register_blueprints(app):
    from decanter.app.handlers import authentication_handler
    app.register_blueprint(base_handler)
    app.register_blueprint(authentication_handler)
