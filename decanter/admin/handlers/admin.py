from flask import abort, redirect, Blueprint, render_template
from flask.ext.login import current_user
from flask.ext.login import login_required

from decanter.api.interface import post


plan = Blueprint('admin', __name__)


@plan.route('/', methods=['GET'])
@login_required
def index():
    return render_template('decanter/admin/index.html')


@plan.route('/users', methods=['GET'])
@login_required
def users_get():
    return render_template('decanter/admin/users.html')


@plan.route('/groups', methods=['GET'])
@login_required
def group_get():
    return render_template('decanter/admin/groups.html')


@plan.route('/posts', methods=['GET'])
@login_required
def posts_get():
    return render_template('decanter/admin/posts.html')


@plan.route('/posts/create', methods=['GET'])
@login_required
def post_create_get():
    return render_template('decanter/admin/post_create.html')


@plan.route('/posts/edit', methods=['GET'])
@login_required
def post_edit_root_get():
    return redirect('/admin/posts/', 302)


@plan.route('/posts/edit/<int:post_id>', methods=['GET'])
@login_required
def post_edit_get(post_id):
    p = post.get_by_id(post_id)
    if p is None:
        return abort(404)

    usr = current_user._get_current_object()
    if p.author.id != usr.id:
        return abort(401)

    return render_template('decanter/admin/post_edit.html', post_id=post_id)
