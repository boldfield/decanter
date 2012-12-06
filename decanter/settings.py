import os

database = os.environ.get('DATABASE_URL')
database = os.environ.get('DECANTER_DATABASE_URL', database)
database = database or 'postgresql://localhost/decanter'

whitelist = os.environ.get('DECANTER_WHITELIST', '')
whitelist = filter(lambda ip: ip, whitelist.split('|'))
blacklist = os.environ.get('DECANTER_BLACKLIST', '')
blacklist = filter(lambda ip: ip, blacklist.split('|'))


def init_app(app):
    os.environ.setdefault('DECANTER_SETTINGS', 'decanter.settings.dev')
    app.config.from_object(os.environ['DECANTER_SETTINGS'])

    if 'DECANTER_CONFIG' in os.environ:
        app.config.from_envvar('DECANTER_CONFIG')


class base(object):
    DEBUG = False
    TESTING = False
    DOMAIN = os.environ.get('DECANTER_DOMAIN', 'localhost')
    SQLALCHEMY_DATABASE_URI = database
    SECRET_KEY = os.environ.get('DECANTER_SECRET', 'development-key')
    SESSION_SALT = os.environ.get('DECANTER_SESSION_SALT', 'development-salt')
    WHITELIST = whitelist
    BLACKLIST = blacklist
    CSRF_COOKIE_NAME = 'decanter_csrf'
    CSRF_DISABLE = False
    GOOGLE_ANALYTICS_ID = os.environ.get('DECANTER_GOOGLE_ANALYTICS_ID')
    API_PATH = os.environ.get('DECANTER_API_PATH')
    API_HOST = os.environ.get('DECANTER_API_HOST')

    SESSION_COOKIE_DOMAIN = DOMAIN
    SESSION_COOKIE_NAME = 'decanter_session'

    REMEMBER_COOKIE_NAME = DOMAIN
    REMEMBER_COOKIE_DOMAIN = 'decanter_remember'


class dev(base):
    DEBUG = True


class test(base):
    TESTING = True
    DEBUG = True


class prod(base):
    pass
