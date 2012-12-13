import os

from decanter import DIR
from decanter.base import App
from decanter.admin.handlers import admin, auth

TEMPLATE = os.path.join(DIR, 'templates')

def create_app():
    app = Admin(__name__,
                template_folder=TEMPLATE)
    return app


class Admin(App):
    url_strict_slashes = False

    def register_blueprints(self):
        self.register_blueprint(auth.plan)
        self.register_blueprint(admin.plan)
