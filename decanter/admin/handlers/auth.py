from flask import (Blueprint, request, render_template, redirect, flash)
from flask.ext.security import LoginForm
from flask.ext.login import login_user, logout_user

from decanter.api.interface import user as UserInterface

__all__ = ('auth',)


plan = Blueprint('auth', __name__)


@plan.route('/login', methods=["GET"])
def login_read():
    form = LoginForm(request.form)
    return render_template("decanter/admin/login.html", form=form)


@plan.route('/login', methods=["POST"])
def login_write():
    form = LoginForm(request.form)
    user = UserInterface.get_by_username(form.username.data)
    if not user:
        user = UserInterface.get_by_email(form.username.data)
    if not user:
        flash('Unknown username/password combination.')
        return render_template("decanter/admin/login.html", form=form)

    if not user.verify_password(form.password.data):
        flash('Unknown username/password combination.')
        return render_template("decanter/admin/login.html", form=form)
    login_user(user, remember=True)
    return redirect(request.args.get('next') or '/')


@plan.route('/logout', methods=["GET"])
def logout_read():
    logout_user()
    return redirect('/')
