from decanter.base import App
from decanter.app.handlers import admin, auth


def create_app():
    app = Admin(__name__)
    return app


class Admin(App):
    url_strict_slashes = False

    def register_blueprints(self):
        self.register_blueprint(auth.plan)
        self.register_blueprint(admin.plan)
