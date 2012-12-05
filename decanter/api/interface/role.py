from decanter.database import db
from decanter.database.models import Role


def create(name, description):
    r = Role()
    r.name = name
    r.description = description

    db.session.add(r)
    db.session.commit()
    return r


def get_by_name(name):
    r = Role.query.filter_by(name=name).first()
    return r
