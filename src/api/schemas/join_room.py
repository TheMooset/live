from pydantic import BaseModel


class JoinRoom(BaseModel):
    room_id: int
    device_id: str
