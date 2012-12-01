from datetime import datetime
from hashlib import sha256 as sha
from uuid import uuid4

from sqlalchemy.ext.declarative import AbstractConcreteBase
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security.datastore.sqlalchemy import SQLAlchemyUserDatastore

from decanter.mixins import SerializationMixin
from decanter.api import create_app

app = create_app()
db = SQLAlchemy(app)


class DecanterBaseModel(AbstractConcreteBase, db.Model, SerializationMixin):

    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)

    def __init__(self, *args, **kwargs):
        super(DecanterBaseModel, self).__init__(*args, **kwargs)
        now = datetime.utcnow()
        self.created = now
        self.modified = now

    def __str__(self):
        return '<%s, id:%d>' % (self.__class__.__name__, self.id)

    def __repr__(self):
        return self.__str__()


# User/Group data modles
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('role.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('user.id')))


class Role(DecanterBaseModel):
    __tablename__ = 'role'

    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(DecanterBaseModel):
    __tablename__ = 'user'

    username = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(120))
    salt = db.Column(db.Unicode(32), nullable=False)  # This shouldn't be here 
    active = db.Column(db.Boolean(), default=True)

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, **kwargs):
        if 'roles' not in kwargs:
            kwargs['roles'] = []
        else:
            roles = list()
            for role in kwargs['roles']:
                r = Role.query.filter_by(name=role).first()
                roles.append(r)
            kwargs['roles'] = roles
        super(User, self).__init__(**kwargs)
        self.salt = uuid4().hex
        self.password = self.encrypt(self.password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def encrypt(self, password):
        crypt_str = self._encrypt(self.salt, password)
        return self._encrypt(self.salt, crypt_str)

    def _encrypt(self, salt, message):
        crypt_str = salt + message
        return sha(crypt_str).hexdigest()


post_tag = db.Table('post_tag',
                    DecanterBaseModel.metadata,
                    db.Column('post_id', db.BigInteger, db.ForeignKey('post.id')),
                    db.Column('tag_id', db.BigInteger, db.ForeignKey('tag.id'))
           )


comment_tag = db.Table('comment_tag',
                       DecanterBaseModel.metadata,
                       db.Column('comment_id', db.BigInteger, db.ForeignKey('comment.id')),
                       db.Column('tag_id', db.BigInteger, db.ForeignKey('tag.id'))
              )


# NOTE ::  It really feels like Post and Comment are two flavors of the same
# NOTE ::  object type.  Perhaps they should be normalized together.
class Post(DecanterBaseModel):
    __tablename__ = 'post'

    parent = db.Column(db.BigInteger, db.ForeignKey('post.id'), nullable=True)

    author = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    active = db.Column(db.Boolean(), default=False)
    title = db.Column(db.Unicode(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Unicode(255), nullable=False, unique=True, index=True)
    published = db.Column(db.DateTime)

    score = db.Column(db.BigInteger)
    tags = db.relationship('Tag',
                           secondary=post_tag,
                           backref=db.backref('posts', lazy='dynamic')
           )


class Comment(DecanterBaseModel):
    __tablename__ = 'comment'

    post = db.Column(db.BigInteger, db.ForeignKey('post.id'), index=True)
    parent = db.Column(db.BigInteger, db.ForeignKey('comment.id'), nullable=True)

    author = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    content = db.Column(db.Text)
    score = db.Column(db.BigInteger)
    tags = db.relationship('Tag',
                           secondary=comment_tag,
                           backref=db.backref('comments', lazy='dynamic')
           )


class CommentRating(DecanterBaseModel):
    __tablename__ = 'comment_rating'

    rater = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    rating = db.Column(db.BigInteger, nullable=False)
    comment_id = db.Column(db.BigInteger, db.ForeignKey('comment.id'), index=True)
    comment = db.relationship('Comment', backref='ratings')


class PostRating(DecanterBaseModel):
    __tablename__ = 'post_rating'

    rater = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    rating = db.Column(db.BigInteger, nullable=False)
    post_id = db.Column(db.BigInteger, db.ForeignKey('post.id'), index=True)
    post = db.relationship('Post', backref='ratings')


class Tag(DecanterBaseModel):
    __tablename__ = 'tag'

    slug = db.Column(db.Unicode(255), nullable=False, unique=True, index=True)
