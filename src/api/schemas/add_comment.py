from pydantic import BaseModel


class AddComment(BaseModel):
    room_id: int
    comment: str
    device_id: str
