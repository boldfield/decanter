from datetime import datetime

from sqlalchemy.sql.expression import desc

from flask import current_app as app

from decanter.database import db
from decanter.database.models import Post
from decanter.exceptions import (ObjectNotFoundError,
                                 UnauthorizedObjectAccessError)

__all__ = ('get', 'create', 'update', 'delete')


def get(filter_inactive=True):
    posts = Post.query
    if filter_inactive:
        posts = posts.filter_by(active=True)
    posts = posts.order_by(Post.id).all()
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


def get_by_tags(tags):
    pass


def create(user, slug, title, content, format, subtitle=None, domain=None, tags=None):
    from decanter.api.interface import tag as TagInterface
    if domain is None:
        domain = app.config.get('DEFAULT_CONTENT_DOMAIN')

    version = 'draft'
    app.content.save(slug, version, format, content, domain)

    p = Post()
    p.author_id = user.id
    p.title = title
    p.slug = slug
    p.format = format
    p.version = version
    p.domain = domain
    p.location = app.content.url(slug, 'published', format, domain)
    p.draft = app.content.url(slug, version, format, domain)

    if subtitle is not None:
        p.subtitle = subtitle

    db.session.add(p)

    if tags is not None:
        for tag in tags:
            TagInterface.add(p, tag)

    db.session.commit()

    return p


def update(post, user, title=None, content=None, tags=None, active=None):
    from decanter.api.interface import tag as TagInterface

    if not post.author == user:
        # This should really be a group perms check.
        raise UnauthorizedObjectAccessError()

    post.title = title if (title is not None) else post.title

    if tags is not None:
        for tag in tags:
            if tag not in post.tags:
                TagInterface.add(post, tag)

    if content is not None:
        app.content.version_copy(post.slug, post.format,
                                 post.domain, 'draft', 'backup')
        app.content.save(post.slug, 'draft',
                         post.format, content, post.domain)
        post.pending_update = True

    fields = (title, tags, active, content)
    changed = any([f is not None for f in fields])
    if changed:
        db.session.add(post)
        db.session.commit()
    return post


def publish(post, user, is_active=False):
    if not is_active:
        return _unpublish(post)
    app.content.version_copy(post.slug, post.format, post.domain,
                             'draft', 'published', readable=True)
    post.active = True
    post.published = datetime.utcnow()
    db.session.add(post)
    db.session.commit()


def _unpublish(post):
    if not post.active:
        return
    app.content.delete(post.slug, 'published', post.format, post.domain)
    post.active = False
    db.session.add(post)
    db.session.commit()


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
