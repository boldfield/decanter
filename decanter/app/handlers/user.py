from flask import (Blueprint, request, render_template,
                   redirect, url_for, abort, flash)
from flask.ext.security import user_datastore, LoginForm
from flask.ext.login import login_user, logout_user

from decanter.app.forms.auth import RegistrationForm
from decanter.api.interface import user as IUser

__all__ = ('authentication_handler',)


authentication_handler = Blueprint('authentication_handler', __name__)


@authentication_handler.route('/login', methods=["GET"])
def login_read():
    form = LoginForm(request.form)
    return render_template("login.html", form=form)


@authentication_handler.route('/login', methods=["POST"])
def login_write():
    form = LoginForm(request.form)
    user = IUser.get(username=form.username.data)
    if not user:
        user = IUser.get(email=form.username.data)
    if not user:
        flash('Unknown username/password combination.')
        return render_template("login.html", form=form)
    user = user[0]
    password = user.encrypt(form.password.data)
    valid = all([c == password[i] for (i, c) in enumerate(user.password)])
    if not valid:
        flash('Unknown username/password combination.')
        return render_template("login.html", form=form)
    login_user(user, remember=True)
    return redirect(request.args.get('next') or '/admin')


@authentication_handler.route('/logout', methods=["GET"])
def logout_read():
    logout_user()
    return redirect('/')
