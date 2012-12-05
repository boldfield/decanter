from os import environ
from flask.ext.login import LoginManager

from decanter.api.interface import user as UserInterface


def to_bool(value):
    if isinstance(value, basestring):
        return value.lower() == 'false'
    return bool(value)


class LoginManagerMixin:
    _login_manager = LoginManager()

    def setup_login_manager(self, app):
        self._app = app
        self._login_manager.setup_app(app)
        self._login_manager.login_view = "/admin/login"

        @self._login_manager.user_loader
        def load_user(userid):
            if isinstance(userid, int):
                user = UserInterface.get_by_id(userid)
            else:
                user = UserInterface.get_by_username(userid)
            return user


class Config(object):

    def __getitem__(self, item):
        return self.__getattribute__(item)
        #try:
        #    return self.__getattribute__(item)
        #except AttributeError:
        #    raise KeyError("KeyError: %s" % item)

    def __setitem__(self, item, value):
        self.__setattr__(item, value)

    def __getattribute__(self, attr):
        try:
            value = object.__getattribute__(self, attr)
        except AttributeError:
            value = environ.get(attr)
        #if value is None:
        #    msg = "AttributeError: '%s' has no attribute '%s'"
        #    msg %= (self.__class__.__name__, attr)
        #    raise AttributeError(msg)
        return value

    def __setattr__(self, attr, value):
        object.__setattr__(self, attr, value)
