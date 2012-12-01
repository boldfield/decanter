from decanter.api.models import User


__all__ = ('get',)


def get(id=None):
    if id is not None:
        return User.query.get(id)
    users = User.query.order_by(Post.id).all()

    return users
