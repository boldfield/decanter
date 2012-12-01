from flask.ext.login import LoginManager

from decanter.api.interface import user as IUser


class LoginManagerMixin:
    _login_manager = LoginManager()

    def setup_login_manager(self, app):
        self._app = app
        self._login_manager.setup_app(app)
        self._login_manager.login_view = "/login"

        @self._login_manager.user_loader
        def load_user(userid):
            if isinstance(userid, int):
                user = IUser.get(id=userid)
            else:
                user = IUser.get(username=userid)
            if isinstance(user, list): user = user[0]
            return user
