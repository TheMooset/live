from pydantic import BaseModel


class UpdateRoom(BaseModel):
    room_id: int
    metadata: dict
