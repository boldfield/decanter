from decanter.database.base import Database

db = Database()


def init_app(app):
    db.init_connection(app.config)
    app.teardown_appcontext(lambda r: db.session.remove())


from decanter.database.models import *
