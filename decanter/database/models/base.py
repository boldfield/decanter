from datetime import datetime

from sqlalchemy.ext.declarative import AbstractConcreteBase

from decanter.mixins import SerializationMixin
from decanter.database import db
from decanter.database.types import DateTimeTZ


class DecanterBaseModel(AbstractConcreteBase, db.Model, SerializationMixin):

    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(DateTimeTZ, default=datetime.utcnow)
    modified = db.Column(DateTimeTZ, default=datetime.utcnow)

    def __str__(self):
        return '<%s, id:%d>' % (self.__class__.__name__, self.id)

    def __repr__(self):
        return self.__str__()
