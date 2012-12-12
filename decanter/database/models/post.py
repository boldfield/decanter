from datetime import datetime

from decanter.database import db
from decanter.database.models.base import DecanterBaseModel
from decanter.database.types import DateTimeTZ


post_tag = db.Table('post_tag',
                    DecanterBaseModel.metadata,
                    db.Column('post_id', db.BigInteger, db.ForeignKey('post.id')),
                    db.Column('tag_id', db.BigInteger, db.ForeignKey('tag.id')),
                    db.Column('created', DateTimeTZ, default=datetime.utcnow))


comment_tag = db.Table('comment_tag',
                       DecanterBaseModel.metadata,
                       db.Column('comment_id', db.BigInteger, db.ForeignKey('comment.id')),
                       db.Column('tag_id', db.BigInteger, db.ForeignKey('tag.id')),
                       db.Column('created', DateTimeTZ, default=datetime.utcnow))


# NOTE ::  It really feels like Post and Comment are two flavors of the same
# NOTE ::  object type.  Perhaps they should be normalized together.
class Post(DecanterBaseModel):
    __tablename__ = 'post'

    parent_id = db.Column(db.BigInteger, db.ForeignKey('post.id'), nullable=True)
    parent = db.relationship('Post',
                             uselist=False,
                             backref=db.backref('children', remote_side="Post.id"))

    author_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    author = db.relationship('User', backref='posts')

    active = db.Column(db.Boolean(), default=False)
    published = db.Column(DateTimeTZ, nullable=True)
    pending_update = db.Column(db.Boolean(), default=True)

    title = db.Column(db.Unicode(255), nullable=False)
    subtitle = db.Column(db.Unicode(255), nullable=False)
    slug = db.Column(db.Unicode(255), nullable=False, index=True, unique=True)
    format = db.Column(db.Enum('txt', 'html', name='post_content_format_enum'))

    domain = db.Column(db.Unicode(255), nullable=False, index=True)

    location = db.Column(db.Unicode(255), nullable=False, unique=True)
    draft = db.Column(db.Unicode(255), nullable=False, unique=True)

    score = db.Column(db.BigInteger)
    tags = db.relationship('Tag',
                           secondary=post_tag,
                           backref=db.backref('posts', lazy='dynamic'))

    _exposed_fields = ('id', 'parent_id', 'author_id', 'active', 'title', 'subtitle', 'slug', 'domain', 'published', 'format', 'location')


class Comment(DecanterBaseModel):
    __tablename__ = 'comment'

    post_id = db.Column(db.BigInteger, db.ForeignKey('post.id'), index=True)
    post = db.relationship('Post', backref='comments')

    parent_id = db.Column(db.BigInteger, db.ForeignKey('comment.id'), nullable=True)
    parent = db.relationship('Comment',
                             uselist=False,
                             backref=db.backref('comments', remote_side="Comment.id"))

    author_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    author = db.relationship('User', backref='comments')

    content = db.Column(db.Text)
    score = db.Column(db.BigInteger)
    tags = db.relationship('Tag',
                           secondary=comment_tag,
                           backref=db.backref('comments', lazy='dynamic'))


class CommentRating(DecanterBaseModel):
    __tablename__ = 'comment_rating'

    rater_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    rater = db.relationship('User', backref='comment_rating')

    rating = db.Column(db.BigInteger, nullable=False)

    comment_id = db.Column(db.BigInteger, db.ForeignKey('comment.id'), index=True)
    comment = db.relationship('Comment', backref='ratings')


class PostRating(DecanterBaseModel):
    __tablename__ = 'post_rating'

    rater_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    rater = db.relationship('User', backref='post_rating')

    rating = db.Column(db.BigInteger, nullable=False)

    post_id = db.Column(db.BigInteger, db.ForeignKey('post.id'), index=True)
    post = db.relationship('Post', backref='ratings')


class Tag(DecanterBaseModel):
    __tablename__ = 'tag'

    slug = db.Column(db.Unicode(255), nullable=False, unique=True, index=True)
