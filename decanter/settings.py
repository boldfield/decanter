DEBUG = True
#SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/decanter.test.db'
SQLALCHEMY_DATABASE_URI = 'postgresql://decanter@localhost/decanter'
DOMAIN = 'decanter.com'
SECRET_KEY = 'development-key'

SECURITY_USER_DATASTORE = 'user_datastore'
