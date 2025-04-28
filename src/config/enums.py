from enum import Enum
from collections import namedtuple

name_tuple = namedtuple("tuple", ['value', 'description'])


class BaseEnum(Enum):
    @classmethod
    def get_value_list(cls):
        return list(map(lambda x: x.value, cls))

    @classmethod
    def get_value_dict(cls):
        return dict(zip(list(a.value for a in cls), list(a.description for a in cls)))

    @property
    def description(self):
        return self._value_.description

    @property
    def value(self):
        return self._value_.value


class ErrorCodeEnums(BaseEnum):
    default = name_tuple(0, "پیش فرض")
    room_not_found = name_tuple(1, "چنین پخش زنده ای وجود ندارد")
    user_is_ban = name_tuple(2, "کاربر بن شده است")
    room_ended = name_tuple(3, "پخش زنده تمام شده است")


class BanTypeEnums(Enum):
    join_room = 'join_room'
    add_comment = 'add_comment'
    remove_from_room = 'remove_from_room'


class RoomTypeEnums(Enum):
    meet = 'meet'
    live_shopping = 'live_shopping'


class VendorVerificationStatusEnums(BaseEnum):
    group_id = name_tuple(5048, "وضعیت احراز هویت غرفه")
    accepted = name_tuple(5049, "تایید شده")
    rejected = name_tuple(5050, "رد شده")
    pending = name_tuple(5051, "درحال بررسی")


class UserVerificationStatusEnums(BaseEnum):
    group_id = name_tuple(5511, "وضعیت احراز هویت کاربر")
    accepted = name_tuple(5513, "تایید شده")
    rejected = name_tuple(5512, "رد شده")
    pending = name_tuple(5514, "درحال بررسی")