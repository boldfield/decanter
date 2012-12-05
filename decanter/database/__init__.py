from decanter.database.base import Database

db = Database()


def init_app(app):
    db.init_connection(app.config)


from decanter.database.models import *
