from flask import Blueprint, abort
from flask_security import current_user

from decanter.api.interface import post
from decanter.response import json_response
from decanter.exceptions import (ObjectNotFoundError,
                                 UnauthorizedObjectAccessError)

__all__ = ('post_handler',)

post_handler = Blueprint('post_handler', __name__)

#############################
#       Read Handlers       #
#############################
@post_handler.route('/post', methods=['GET'])
def post_read():
    if not current_user.is_authenticated():
        pass
        #return abort(403)
    c = post.get()
    # TODO :: This is dirty, there needs to be a generic limiting function to pass to
    c = sorted(c, key=lambda x: x.id, reverse=True)
    return json_response([i.serialize() for i in c], 200)

@post_handler.route('/post/<int:company_id>', methods=['GET'])
def post_read_instance(company_id):
    if not current_user.is_authenticated():
        return abort(403)
    c = company.get(current_user, company_id=company_id)
    if not c:
        abort(404)
    return json_response([i.serialize() for i in c], 200)

##############################
#      Create Handlers       #
##############################
@post_handler.route('/post', methods=['POST'])
def post_create():
    #if not current_user.is_authenticated():
    #    return abort(403)

    name, symbol, public, valuations, grants = _attributes_from_request(request.POST)
    c = post.create(current_user, name=name, symbol=symbol, public=public,
                       valuations=valuations, grants=grants)
    return json_response([c.serialize()], 201)

##############################
#      Update Handlers       #
##############################
@post_handler.route('/company/<int:company_id>', methods=['PUT'])
def company_update(company_id):
    if not current_user.is_authenticated():
        return abort(403)
    name, symbol, public, valuations, grants = _attributes_from_request(request.GET)

    try:
        c = company.create(current_user, company_id, name=name, symbol=symbol,
                           public=public, valuations=valuations, grants=grants)
    except (ObjectNotFoundError, UnauthorizedObjectAccessError):
        # In either instance, return a not found response
        return abort(404)

    return json_response([c.serialize()], 200)

##############################
#       Delete Handlers      #
##############################
@post_handler.route('/company/<int:company_id>', methods=['DELETE'])
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
