from decanter.api.models import db, Tag
from decanter.exceptions import ObjectNotFoundError

__all__ = ('get', 'get_or_create', 'add')


def get(slug=None):
    if slug is not None:
        t.filter_by(slug=slug)
        if not t:
            raise ObjectNotFoundError()
    else:
        t = Tag.query.all()

    return t


def get_or_create(slug):
    t = Tag.query.get(slug=slug)
    if not t:
        t = Tag(slug=slug)
        db.session.add(t)
        db.session.commit()
    return t


def add(obj, tag_slug):
    t = get_or_create(tag_slug)
    obj.add(t)

