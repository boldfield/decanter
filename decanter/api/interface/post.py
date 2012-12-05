import pytz
from datetime import datetime

from decanter.database import db
from decanter.database.models import Post, User
from decanter.exceptions import (ObjectNotFoundError,
                                 UnauthorizedObjectAccessError)

__all__ = ('get', 'create', 'update', 'delete')


def get():
    posts = Post.query.order_by(Post.id).all()
    return posts


def get_by_id(id):
    p = Post.query.filter_by(id=id).first()
    return p


def get_by_slug(slug):
    p = Post.query.filter_by(slug=slug).first()
    return p


def get_by_user(user):
    q = Post.query.filter_by(author_id=user.id)
    return q.all()


def get_gy_tags(tags):
    pass


def create(user, slug, title, content, subtitle=None, tags=None):
    from decanter.api.interface import tag as TagInterface
    p = Post()
    p.author_id = user.id
    p.title = title
    p.slug = slug
    p.content = content

    if subtitle is not None:
        p.subtitle = subtitle

    db.session.add(p)

    if tags is not None:
        for tag in tags:
            TagInterface.add(p, tag)

    db.session.commit()
    return p


def update(post, user, slug=None, title=None, content=None, tags=None, active=None):
    from decanter.api.interface import tag as TagInterface

    if not post.author == user:
        # This should really be a group perms check.
        raise UnauthorizedObjectAccessError()

    post.title = title if (title is not None) else post.title
    post.slug = slug if (slug is not None) else post.slug
    post.content = content if (content is not None) else post.content
    if tags is not None:
        for tag in tags:
            if tag not in post.tags:
                TagInterface.add(post, tag)
    if active is not None:
        if active:
            post.published = datetime.utcnow()
        post.active = active

    fields = (title, content, tags, slug, active)
    changed = any([f is not None for f in fields])
    if changed:
        db.session.add(post)
        db.session.commit()
    return post


def delete(pid, user):
    p = Post.query.get(pid)
    if not p:
        raise ObjectNotFoundError()

    if not p.author == user:
        # This should really be a group perms check.
        raise UnauthorizedObjectAccessError()
    p.active = False
    db.session.commit()
    return None
