from decanter.database import db
from decanter.database.models import Tag
from decanter.exceptions import ObjectNotFoundError

__all__ = ('get', 'get_or_create', 'add')


def get(slug):
    if not slug:
        return None
    t = Tag.query.filter_by(slug=slug).first()
    if not t:
        raise ObjectNotFoundError()
    return t


def get_or_create(slug):
    t = Tag.query.filter_by(slug=slug).first()
    if not t:
        t = Tag(slug=slug)
        db.session.add(t)
        db.session.commit()
    return t


def add(obj, tag_slug):
    t = get_or_create(tag_slug)
    if t not in obj.tags:
        obj.tags.append(t)
        db.session.add(obj)
        db.session.commit()
