from decanter.api.models import db, Post
from decanter.exceptions import (ObjectNotFoundError,
                                 UnauthorizedObjectAccessError)

__all__ = ('get', 'create', 'update', 'delete')


def get(id=None, tags=None, user=None):
    query = Post.query
    if id is not None:
        query = query.filter_by(id=id)

    if user is not None:
        # Post status filtering will go here (ie pre-posts to admin only...)
        pass

    if tags is not None:
        # Post tag filtering will go here (ie pre-posts to admin only...)
        pass

    posts = query.order_by(Post.id).all()

    return posts


def create(user, slug, title, content, tags=None):
    from decanter.api.interface import tag as TagInterface
    p = Post(author=user.id,
             title=title,
             slug=slug,
             content=content)
    db.session.add(p)

    if tags is not None:
        for tag in tags:
            TagInterface.add(p, tag)

    db.session.commit()
    return p


def update(pid, user, slug, title=None, content=None, tags=None):
    from decanter.api.interface import tag as TagInterface
    p = Post.query.get(pid)
    if not p:
        raise ObjectNotFoundError()

    if not p.author == user:
        # This should really be a group perms check.
        raise UnauthorizedObjectAccessError()

    p.title = title if (title is not None) else p.title
    p.content = content if (content is not None) else p.content
    if tags is not None:
        for tag in tags:
            if tag not in p.tags:
                TagInterface.add(p, tag)

    fields = (title, content, tags)
    changed = any([f is not None for f in fields])
    if changed:
        db.session.commit()
    return p


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
