import pytz
from datetime import datetime


class SerializationMixin:

    def serialize(self, add_fields=None):
        ret = dict()
        fields = list(self._exposed_fields)
        if add_fields is not None:
            if not isinstance(add_fields, (list, tuple)):
                add_fields = [add_fields]
            fields.extend(add_fields)
        for field in fields:
            value = getattr(self, field)
            ret[field] = self._serialize(value)
        return ret

    def _serialize(self, value):
        ret = value

        if isinstance(value, datetime):
            if value.tzinfo is None:
                dt = pytz.utc.localize(value)
            else:
                dt = value.astimezone(pytz.utc)
            ret = int(dt.strftime('%s'))

        elif isinstance(value, bool):
            ret = 1 if value else 0

        elif hasattr(value, 'serialize'):
            ret = value.serialize()

        elif isinstance(value, (list, tuple)):
            ret = list()
            for item in value:
                ret.append(self._serialize(item))

        return ret
