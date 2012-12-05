from flask import Blueprint, abort
from flask.ext.login import login_required

from decanter import Decanter
from decanter.response import json_response
from decanter.restrict import crossdomain
from decanter.database.models import User


__all__ = ('get',)

plan = Blueprint('user', __name__, url_prefix='/user')


#############################
#       Read Handlers       #
#############################
@plan.route('/', methods=['GET', 'OPTIONS'])
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
@login_required
def user_read():
    users = User.query.order_by(User.id).all()

    return json_response([u.serialize() for u in users], 200)


@plan.route('/<int:user_id>', methods=['GET', 'OPTIONS'])
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
@login_required
def user_read_instance_by_id(user_id):
    u = User.query.filter_by(id=user_id).first()
    if not u:
        return abort(404)

    return json_response(u.serialize(), 200)


@plan.route('/<string:username>', methods=['GET', 'OPTIONS'])
@crossdomain(origin=Decanter.xhr_allow_origin, headers='Content-Type')
@login_required
def user_read_instance_by_username(username):
    u = User.query.filter_by(username=username).first()
    if not u:
        return abort(404)

    return json_response(u.serialize(), 200)
