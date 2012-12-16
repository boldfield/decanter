from decanter.app import App
from decanter import content


def create_app():
    app = API(__name__)
    return app


class API(App):
    url_strict_slashes = False

    def configure(self):
        super(API, self).configure()
        content.init_app(self)

    def register_blueprints(self):
        from decanter.api.handlers import post, image, user, role
        self.register_blueprint(post.plan)
        self.register_blueprint(image.plan)
        self.register_blueprint(user.plan)
        self.register_blueprint(role.plan)
