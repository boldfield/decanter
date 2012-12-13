from flask import (Blueprint, request, render_template,
                   redirect, url_for, abort)

__all__ = ('base_handler',)


base_handler = Blueprint('base_handler', __name__)


@base_handler.route('/', methods=["GET"])
def base_read():
    return render_template("index.html")
