from decanter.app import App
from decanter.admin.handlers import admin, auth
from decanter import content


def create_app():
    app = Admin(__name__,
                template_folder='../templates')
    return app


class Admin(App):
    url_strict_slashes = False

    def configure(self):
        super(Admin, self).configure()
        content.init_app(self)

    def register_blueprints(self):
        self.register_blueprint(auth.plan)
        self.register_blueprint(admin.plan)
