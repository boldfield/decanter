from decanter.api.models import User

#def get(id=None, username=None, email=None):
def get(**kwargs):
    query = User.query
#    if id is not None:
#        query = query.filter_by(id=id)
#    elif username is not None:
#        query = query.filter_by(username=username)
#    elif email is not None:
#        query = query.filter_by(email=username)
    if kwargs:
        query = query.filter_by(**kwargs)

    users = query.all()
    return users
