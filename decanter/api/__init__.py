from flask import Flask

from decanter import settings, restrict, content
from decanter import database


def create_app():
    app = Flask(__name__)
    settings.init_app(app)
    database.init_app(app)
    restrict.init_app(app)
    content.init_app(app)

    register_blueprints(app)

    return app


def register_blueprints(app):
    from decanter.api.handlers import post, user, role

    app.register_blueprint(post.plan)
    app.register_blueprint(user.plan)
    app.register_blueprint(role.plan)
