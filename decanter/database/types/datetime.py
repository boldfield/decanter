import pytz

from sqlalchemy.types import TypeDecorator, DateTime


class DateTimeTZ(TypeDecorator):
    impl = DateTime

    def __init__(self, tzinfo=pytz.UTC, *args, **kwargs):
        kwargs['timezone'] = True
        super(DateTimeTZ, self).__init__(*args, **kwargs)
        self.tz = tzinfo

    def process_bind_param(self, value, dialect):
        if not value:
            return value
        if value.tzinfo is None:
            value = self.tz.localize(value)
        elif value.tzname() != self.tz.zone:
            value = value.astimezone(self.tz)
        return value

    def process_result_value(self, value, dialect):
        if value:
            if value.tzinfo is None:
                value = self.tz.localize(value)
            elif value.tzname() != self.tz.zone:
                value = value.astimezone(self.tz)
        return value

    def compare_values(self, x, y):
        x = self.process_bind_param(x, None)
        y = self.process_bind_param(y, None)
        return x == y
