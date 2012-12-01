from uuid import uuid4

from flask.ext.script import Manager
from werkzeug.serving import run_simple

from decanter.api.models import (app, db, User, Role)
from decanter import application

manager = Manager(app)

DUMMY_CONTENT = u'Cras mattis consectetur purus sit amet fermentum. Vivamus sagittis lacus vel augue laoreet rutrum faucibus dolor auctor. Integer posuere erat a ante venenatis dapibus posuere velit aliquet. Aenean lacinia bibendum nulla sed consectetur. Sed posuere consectetur est at lobortis.'


@manager.command
def initdb():
    """Creates all database tables."""
    db.create_all()


@manager.command
def create_roles():
    with app.test_request_context():
        r1 = Role(name='admin', description='Administrative user.')
        r2 = Role(name='user', description='General system user.')
        db.session.add(r1)
        db.session.add(r2)
        db.session.commit()


@manager.command
def create_users():
    with app.test_request_context():
        u1 = User(username='admin',
                  email='admin@optionminder.com',
                  password='admin',
                  roles=['user','admin'])

        u2 = User(username='testuser',
                  email='testuser@optionminder.com',
                  password='test',
                  roles=['user'])

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()


@manager.command
def create_posts():
    from decanter.api.models import Post, User
    user = User.query.all()[0]
    post_one = Post(author=user.id,
                    title=u'Test Post One',
                    slug=u'test-post-one')
    post_one.content = DUMMY_CONTENT
    db.session.add(post_one)
    post_two = Post(author=user.id,
                    title=u'Test Post Two',
                    slug=u'test-post-two')
    post_two.content = DUMMY_CONTENT
    db.session.add(post_two)
    db.session.commit()


@manager.command
def dropdb():
    """Drops all database tables."""
    db.drop_all()


@manager.command
def runtestserver():
    """Runs a test server on port 80"""
    run_simple('127.0.0.1',
               80,
               application,
               use_reloader=True,
               use_debugger=True,
               use_evalex=True)

    application.run(port=80)

if __name__ == '__main__':
    manager.run()
