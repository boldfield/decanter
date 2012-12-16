from flask import request, abort, Blueprint, current_app as app
from flask_security import current_user
from flask.ext.login import login_required

from decanter import Decanter
from decanter.api.interface import image, post
from decanter.response import json_response
from decanter.restrict import crossdomain
from decanter.exceptions import (ObjectNotFoundError,
                                 UnauthorizedObjectAccessError)


plan = Blueprint('image', __name__, url_prefix='/image')


#############################
#       Read Handlers       #
#############################
@plan.route('/', methods=['GET', 'OPTIONS'])
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
def image_read():
    c = image.get()
    return json_response([i.serialize() for i in c], 200)


@plan.route('/<int:image_id>', methods=['GET', 'OPTIONS'])
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
def image_read_instance_by_id(image_id):
    p = image.get_by_id(image_id)
    if not p:
        return abort(404)

    return json_response(p.serialize(), 200)


@plan.route('/<string:image_name>', methods=['GET', 'OPTIONS'])
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
def image_read_instance_by_slug(image_name):
    p = image.get_by_name(image_name)
    if not p:
        return abort(404)
    return json_response(p.serialize(), 200)


##############################
#      Create Handlers       #
##############################
@plan.route('/', methods=['POST'])
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
@login_required
def image_create():
    image_file = request.files['image']
    data = request.form
    name = data.get('name')
    domain = data.get('domain', app.config.get('DEFAULT_CONTENT_DOMAIN'))
    post_slug = data.get('post-slug', None)
    if post_slug is not None:
        p = post.get_by_slug(post_slug)
    i = image.create(image_file,
                     name,
                     domain=domain,
                     post=p)
    return json_response(i.serialize(), 201)


##############################
#       Delete Handlers      #
##############################
@plan.route('/<int:image_id>', methods=['DELETE'])
def image_delete(image_id):
    if not current_user.is_authenticated():
        return abort(403)

    try:
        image.delete(image_id)
    except (ObjectNotFoundError, UnauthorizedObjectAccessError):
        # In either instance, return a not found response
        return abort(404)

    # TODO :: This response needs to make sense.
    return json_response([0], 204)
