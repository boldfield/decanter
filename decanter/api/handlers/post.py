from flask import request, abort, Blueprint
from flask_security import current_user
from flask.ext.login import login_required

from decanter import Decanter
from decanter.negotiate import accepts
from decanter.api.interface import post
from decanter.response import json_response
from decanter.restrict import crossdomain
from decanter.exceptions import (ObjectNotFoundError,
                                 UnauthorizedObjectAccessError)


plan = Blueprint('post', __name__, url_prefix='/post')


#############################
#       Read Handlers       #
#############################
@plan.route('/', methods=['GET'])
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
def post_read():
    c = post.get()
    return json_response([i.serialize() for i in c], 200)


@plan.route('/<int:post_id>', methods=['GET'])
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
def post_read_instance_by_id(post_id):
    p = post.get_by_id(post_id)
    if not p:
        return abort(404)
    return json_response(p.serialize(), 200)


@plan.route('/<string:post_slug>', methods=['GET'])
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
def post_read_instance_by_slug(post_slug):
    p = post.get_by_slug(post_slug)
    if not p:
        return abort(404)
    return json_response(p.serialize(), 200)


##############################
#      Create Handlers       #
##############################
@plan.route('/', methods=['POST'])
@accepts('application/json')
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
@login_required
def post_create():
    usr = current_user._get_current_object()
    data = request.json
    subtitle = data.get('subtitle', None)
    tags = data.get('tags', None)
    tags = [t.strip() for t in tags.split(',')] if tags else None
    p = post.create(usr,
                    data.get('slug'),
                    data.get('title'),
                    data.get('content'),
                    subtitle=subtitle,
                    tags=tags)
    return json_response(p.serialize(), 201)


##############################
#      Update Handlers       #
##############################
@plan.route('/<int:post_id>', methods=['PUT'])
@accepts('application/json')
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
@login_required
def post_update_by_id(post_id):
    usr = current_user._get_current_object()
    data = request.json

    pid = data.get('id', None)
    if pid is None or pid != post_id:
        return abort(400)
    p = post.get_by_id(pid)

    if not p:
        msg = 'Unknown post id: %s' % pid
        raise ObjectNotFoundError(msg)

    return update(usr, p, data)


@plan.route('/<string:post_slug>', methods=['PUT'])
@accepts('application/json')
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
@login_required
def post_update_by_slug(post_slug):
    usr = current_user._get_current_object()
    data = request.json

    slug = data.get('id', None)
    if slug != post_slug:
        abort(400)
    p = post.get_by_slug(post_slug)
    if not p:
        msg = 'Unknown post slug: %s' % slug
        raise ObjectNotFoundError(msg)

    pid = data.get('id', None)
    if pid and p.id != pid:
        return abort(400)

    return update(usr, p, data)


def update(usr, p, data):
    if usr.id != p.author_id or p.author_id != data['author_id']:
        msg = 'You are not authorized to update post id: %s' % p.id
        raise UnauthorizedObjectAccessError(msg)

    if 'tags' in data:
        data['tags'] = [t.strip() for t in data['tags'].split(',')]

    kwargs = dict()
    for (k, v) in data.items():
        if k in ('slug', 'title', 'content', 'tags', 'active'):
            kwargs[k] = v
    post.update(p, usr, **kwargs)

    return json_response(p.serialize(), 200)


##############################
#       Delete Handlers      #
##############################
@plan.route('/<int:company_id>', methods=['DELETE'])
def company_delete(company_id):
    if not current_user.is_authenticated():
        return abort(403)

    try:
        company.delete(current_user, company_id)
    except (ObjectNotFoundError, UnauthorizedObjectAccessError):
        # In either instance, return a not found response
        return abort(404)

    # TODO :: This response needs to make sense.
    return json_response([0], 204)


def _attributes_from_request():
    pass
