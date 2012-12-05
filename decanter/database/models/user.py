from datetime import datetime
from uuid import uuid4 as uuid
from hashlib import sha256 as sha

from decanter.database import db
from decanter.database.types import DateTimeTZ
from decanter.database.models.base import DecanterBaseModel


# User/Group data modles
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')),
                       db.Column('created', DateTimeTZ, default=datetime.utcnow))


class Role(DecanterBaseModel):
    __tablename__ = 'role'

    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    _exposed_fields = ('id', 'name', 'description')


class User(DecanterBaseModel):
    __tablename__ = 'user'

    username = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    _password = db.Column('password', db.String(120), nullable=False)
    salt = db.Column(db.Unicode(32), nullable=False)  # This shouldn't be here
    active = db.Column(db.Boolean(), default=True)

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    _exposed_fields = ('id', 'username', 'email', 'roles', 'active')

    def __init__(self, **kwargs):
        if 'roles' not in kwargs:
            kwargs['roles'] = []
        else:
            roles = list()
            for role in kwargs['roles']:
                r = Role.query.filter_by(name=role).first()
                roles.append(r)
            kwargs['roles'] = roles
        self.salt = uuid().hex
        super(User, self).__init__(**kwargs)

    @property
    def role_names(self):
        return ', '.join([r.name for r in self.roles])

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        crypt_str = self._encrypt(self.salt, password)
        self._password = self._encrypt(self.salt, crypt_str)

    def _encrypt(self, salt, message):
        crypt_str = salt + message
        return sha(crypt_str).hexdigest()

    def verify_password(self, password):
        crypt_pass = self._encrypt(self.salt, password)
        crypt_pass = self._encrypt(self.salt, crypt_pass)

        valid = all([c == crypt_pass[i] for (i, c) in enumerate(self.password)])
        return valid
