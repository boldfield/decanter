from flask import Blueprint, abort
from flask.ext.login import login_required

from decanter.response import json_response
from decanter.restrict import crossdomain
from decanter.database.models import Role


plan = Blueprint('role', __name__, url_prefix='/role')


#############################
#       Read Handlers       #
#############################
@plan.route('/', methods=['GET'])
@crossdomain(origin='*')
@login_required
def role_read():
    roles = Role.query.order_by(Role.id).all()
    return json_response([r.serialize() for r in roles], 200)


@plan.route('/<int:role_id>', methods=['GET'])
@crossdomain(origin='*')
@login_required
def role_read_instance(role_id):
    r = Role.query.filter_by(id=role_id).first()
    if not r:
        return abort(404)

    return json_response(r.serialize(), 200)
