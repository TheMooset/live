from pydantic import BaseModel
from typing import Optional, List

from config.enums import RoomTypeEnums


class CreateRoom(BaseModel):
    subject: str
    description: str
    product_ids: Optional[List[int]]
    type: Optional[RoomTypeEnums] = RoomTypeEnums.live_shopping
