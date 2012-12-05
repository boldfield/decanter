from decanter.database import db
from decanter.database.models import User


def create(username, email, password, roles, active=True):
    usr = User()
    usr.username = username
    usr.email = email
    usr.password = password
    usr.active = active

    roles = roles or []
    for role in roles:
        usr.roles.append(role)

    db.session.add(usr)
    db.session.commit()

    return usr


def get():
    return User.query.all()


def get_by_username(username):
    if not username:
        return None
    u = User.query.filter_by(username=username).first()
    return u


def get_by_email(email):
    if not email:
        return None
    u = User.query.filter_by(email=email).first()
    return u


def get_by_id(id):
    u = User.query.filter_by(id=id).first()
    return u
