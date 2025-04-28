from datetime import datetime, timedelta


class DateTimeUtils:

    @classmethod
    def get_time(cls, string_format=False, **kwargs):
        date_time = datetime.now() + timedelta(**kwargs)
        if string_format:
            return cls.get_string_date(date_time)
        else:
            return date_time

    @staticmethod
    def get_string_date(date_time=None, format_date="%Y-%m-%d %H:%M:%S") -> str:
        if not date_time:
            date_time = datetime.now()
        return date_time.strftime(format_date)

    @staticmethod
    def string_to_date(date_string) -> datetime:
        date_string = date_string.replace("T", " ")
        return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

    @classmethod
    def get_floor_time(cls, date_time=None, minute=10):
        if not date_time:
            date_time = datetime.now()
        return date_time - timedelta(minutes=date_time.minute % minute, seconds=date_time.second,
                                     microseconds=date_time.microsecond)

    @classmethod
    def date_from_timestamp(cls, timestamp):
        return datetime.fromtimestamp(timestamp)

    @classmethod
    def validate_string_date(cls, date_time_string, format_date='%Y-%m-%d %H:%M:%S'):
        try:
            datetime.strptime(date_time_string, format_date)
            return True
        except ValueError:
            return False
