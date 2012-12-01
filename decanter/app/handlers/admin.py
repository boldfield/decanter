from flask import request, abort, redirect, url_for
from flask.ext.admin import BaseView, AdminIndexView, expose
from flask.ext.security import User
from flask.ext.login import current_user
from flask.ext.login import login_required

from decanter.api.models import db, Post
from decanter.api.interface import (post as IPost,
                                    user as IUser)
from decanter.app.forms.createpost import CreatePostForm


class AdminIndexHandler(AdminIndexView):

    @expose('/', methods=['GET'])
    @login_required
    def index(self):
        return self.render('admin/index.html')

class LogoutHandler(BaseView):

    @expose('/', methods=['GET'])
    @login_required
    def index(self):
        return redirect('/logout', 301)

class PostAdminHandler(BaseView):

    @expose('/', methods=['GET'])
    @login_required
    def index(self):
        posts = IPost.get()
        for post in posts:
            if not isinstance(post.author, User):
                u = IUser.get(id=post.author)[0]
                post.author_name = u.username
        return self.render('admin/posts.html', posts=posts)

    @expose('/', methods=['POST'])
    @login_required
    def update_posts(self):
        pass


class PostCreateHandler(BaseView):

    @expose('/', methods=['GET'])
    @login_required
    def index(self):
        form = CreatePostForm(request.form)
        kwargs = dict(form=form, created=False)
        return self.render('admin/createpost.html', **kwargs)

    @expose('/', methods=['POST'])
    @login_required
    def create_posts_write(self):
        form = CreatePostForm(request.form)
        # TODO :: When flask-login is implemented, this should be the active user.
        kwargs = dict(form=form, created=False)
        slug = form.slug.data.replace(' ', '-')
        post = IPost.create(current_user, slug, form.title.data, form.content.data)
        return self.render('admin/createpost.html', **kwargs)


class PostEditHandler(BaseView):

    @expose('/')
    @login_required
    def index(self):
        return redirect('/admin/posts/', 302)

    @expose('/<int:post_id>', methods=['GET'])
    @login_required
    def update_post_read(self, post_id):
        post = IPost.get(id=post_id)
        if post is None:
            abort(404)
        post = post[0]

        if post.author != current_user.id:
            abort(401)

        form = CreatePostForm(request.form)
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        kwargs = dict(form=form, post=post, updated=False)
        return self.render('admin/editpost.html', **kwargs)

    @expose('/<int:post_id>', methods=['POST'])
    @login_required
    def update_post_write(self, post_id):
        post = IPost.get(id=post_id)
        form = CreatePostForm(request.form)
        # TODO :: This needs to use the post interface. Transition must
        # TODO :: wait until flask-login is implemented.
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        db.session.commit()
        kwargs = dict(form=form, post=post, updated=True)
        return self.render('admin/editpost.html', **kwargs)
