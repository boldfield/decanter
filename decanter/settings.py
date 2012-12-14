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

    DEFAULT_CONTENT_DOMAIN = os.environ.get('DECANTER_DEFAULT_CONTENT_DOMAIN') or 'default'
    S3_BUCKET = os.environ.get('DECANTER_S3_BUCKET')
    S3_URL = os.environ.get('DECANTER_S3_URL')

    SESSION_COOKIE_DOMAIN = os.environ.get('DECANTER_COOKIE_DOMAIN')
    SESSION_COOKIE_NAME = 'decanter_session'

    REMEMBER_COOKIE_NAME = 'decanter_remember'
    REMEMBER_COOKIE_DOMAIN = os.environ.get('DECANTER_COOKIE_DOMAIN')

    SQLALCHEMY_DATABASE_URI = database
    SECRET_KEY = os.environ.get('DECANTER_SECRET', 'development-key')
    SESSION_SALT = os.environ.get('DECANTER_SESSION_SALT', 'development-salt')

    WHITELIST = whitelist
    BLACKLIST = blacklist

    CSRF_COOKIE_NAME = 'decanter_csrf'
    CSRF_DISABLE = False

    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')
    GOOGLE_ANALYTICS_DOMAIN = os.environ.get('GOOGLE_ANALYTICS_DOMAIN')

    API_PATH = os.environ.get('DECANTER_API_PATH')
    API_HOST = os.environ.get('DECANTER_API_HOST')


class dev(base):
    DEBUG = True


class test(base):
    TESTING = True
    DEBUG = True


class prod(base):
    pass
