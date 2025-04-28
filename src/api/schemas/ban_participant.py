from pydantic import BaseModel

from config.enums import BanTypeEnums


class BanParticipant(BaseModel):
    room_id: int
    identity: str
    ban_type: BanTypeEnums
