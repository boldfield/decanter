from flask import current_app as app

from decanter.database import db
from decanter.database.models import Image
from decanter.exceptions import ObjectNotFoundError

class DuplicateImageNameError(Exception):
    pass


def get(filter_inactive=True):
    images = Image.query
    images = images.order_by(Image.id).all()
    return images


def get_by_id(id):
    p = Image.query.filter_by(id=id).first()
    return p


def get_by_name(name):
    p = Image.query.filter_by(name=name).first()
    return p


def create(image, name, domain=None, post=None):
    if domain is None:
        domain = app.config.get('DEFAULT_CONTENT_DOMAIN')

    if get_by_name(name) is not None:
        msg = "An image with the name %s has already been created." % name
        raise DuplicateImageNameError(msg)

    app.image_content.save(image, name, domain, post=post)

    i = Image()
    i.name = name
    i.domain = domain
    i.location = app.image_content.url(image, name, domain, post=post)
    i.thumbnail = None
    if post is not None:
        i.post_id = post.id

    db.session.add(i)
    db.session.commit()

    return i


def delete(pid, user):
    i = Image.query.get(pid)
    if not i:
        raise ObjectNotFoundError()
    return None
