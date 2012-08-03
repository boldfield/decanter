from datetime import datetime

from sqlalchemy.ext.declarative import AbstractConcreteBase
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import UserMixin, RoleMixin

from decanter.mixins import SerializationMixin
from decanter.api import create_app

app = create_app()
db = SQLAlchemy(app)


class DecanterBaseModel(AbstractConcreteBase, db.Model, SerializationMixin):

    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)

    def __init__(self):
        now = datetime.utcnow()
        self.created = now
        self.modified = now

    def __str__(self):
        return '<%s, id:%d>' % (self.__class__.__name__, self.id)

    def __repr__(self):
        return self.__str__()


roles_users = db.Table('roles_users',
                       DecanterBaseModel.metadata,
                       db.Column('user_id', db.BigInteger, db.ForeignKey('user.id')),
                       db.Column('role_id', db.BigInteger, db.ForeignKey('role.id'))
              )


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


class Role(DecanterBaseModel, RoleMixin):
    __tablename__ = 'role'

    name = db.Column(db.Unicode(80), unique=True)
    description = db.Column(db.Unicode(255))

    def __init__(self, *args, **kwargs):
        super(Role, self).__init__()
        self.name = unicode(kwargs['name'])
        self.description = unicode(kwargs['description'])


class User(db.Model, UserMixin, SerializationMixin):
    __tablename__ = 'user'

    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.Unicode(255), nullable=False, unique=True, index=True)
    email = db.Column(db.Unicode(255), nullable=True, unique=True, index=True)
    password = db.Column(db.Unicode(32), nullable=False)
    active = db.Column(db.Boolean(), default=0)
    confirmation_token = db.Column(db.Unicode(255))
    confirmation_sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    roles = db.relationship('Role',
                            secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'),
            )

    def __init__(self, *args, **kwargs):
        super(User, self).__init__()
        self.username = unicode(kwargs['username'])
        self.email = unicode(kwargs['email'])
        self.password = unicode(kwargs['password'])
        self.active = kwargs['active'] if 'active' in kwargs else False
        self.roles = kwargs['roles'] if 'roles' in kwargs else []


# NOTE ::  It really feels like Post and Comment are two flavors of the same
# NOTE ::  object type.  Perhaps they should be normalized together.
class Post(DecanterBaseModel, RoleMixin):
    __tablename__ = 'post'

    parent = db.Column(db.BigInteger, db.ForeignKey('comment.id'), nullable=True)

    author = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    content = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Unicode(255), nullable=False, unique=True, index=True)
    score = db.Column(db.BigInteger)
    tags = db.relationship('Tag',
                           secondary=post_tag,
                           backref=db.backref('posts', lazy='dynamic')
           )


class Comment(DecanterBaseModel, RoleMixin):
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


class CommentRating(DecanterBaseModel, RoleMixin):
    __tablename__ = 'comment_rating'

    rater = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    rating = db.Column(db.BigInteger, nullable=False)
    comment_id = db.Column(db.BigInteger, db.ForeignKey('comment.id'), index=True)
    comment = db.relationship('Comment', backref='ratings')


class PostRating(DecanterBaseModel, RoleMixin):
    __tablename__ = 'post_rating'

    rater = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    rating = db.Column(db.BigInteger, nullable=False)
    post_id = db.Column(db.BigInteger, db.ForeignKey('post.id'), index=True)
    post = db.relationship('Post', backref='ratings')


class Tag(DecanterBaseModel, RoleMixin):
    __tablename__ = 'tag'

    slug = db.Column(db.Unicode(255), nullable=False, unique=True, index=True)
