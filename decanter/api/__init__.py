from flask import Flask, Blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object('decanter.settings')
    # This seems... weird
    app.debug = app.config['DEBUG']
    return app

def register_blueprints(app):
    from decanter.api.handlers import post_handler
    #                                  comment_handler)

    app.register_blueprint(post_handler)
    #app.register_blueprint(comment_handler)
