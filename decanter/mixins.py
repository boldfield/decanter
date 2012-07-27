import pytz
from datetime import datetime

class SerializationMixin:

    def serialize(self):
        ret = dict()
        for field in self._exposed_fields:
            value = getattr(self, field)
            ret[field] = value
            if isinstance(value, datetime):
                dt = value.replace(tzinfo=pytz.utc)
                ret[field] = int(dt.strftime('%s'))
            if isinstance(value, bool):
                ret[field] = 1 if value else 0
        return ret

