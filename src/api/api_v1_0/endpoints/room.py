from typing import Union

from fastapi import APIRouter, Depends, Header

from api import middlewares
from api.schemas.create_room import CreateRoom
from api.schemas.join_room import JoinRoom
from api.schemas.ban_participant import BanParticipant
from api.schemas.update_room import UpdateRoom
from services.ban_service import BanService
from services.create_room_service import CreateRoomService
from services.delete_room_service import DeleteRoomService
from services.get_comments_service import GetCommentsService
from services.get_room_service import GetRoomService
from services.get_rooms_service import GetRoomsService
from services.join_room_service import JoinRoomService
from services.update_room_service import UpdateRoomService

router = APIRouter()


@router.post("")
def create_room(room: CreateRoom, Authorization: str = Header(...)):
    return CreateRoomService(model=room, token=Authorization).execute()


@router.get("/{room_identifier}")
def get_room(room_identifier: Union[int, str]):
    if isinstance(room_identifier, int):
        service = GetRoomService(room_id=room_identifier)
    else:
        service = GetRoomService(room_name=room_identifier)

    return service.execute()


@router.delete("/{room_id}")
def delete_room(room_id: int, user_id=Depends(middlewares.get_user_id_from_token)):
    return DeleteRoomService(room_id=room_id, user_id=user_id).execute()


@router.put("/{room_id}")
def update_room(room: UpdateRoom, user_id=Depends(middlewares.get_user_id_from_token)):
    return UpdateRoomService(model=room, user_id=user_id).execute()


@router.post("/join")
def join_room(room: JoinRoom, user_id=Depends(middlewares.get_user_if_from_token_if_exist)):
    return JoinRoomService(model=room, user_id=user_id).execute()


@router.get("/{room_id}/comments")
def get_room_comments(room_id: int, limit: int = 10, offset: int = 0):
    return GetCommentsService(room_id=room_id, limit=limit, offset=offset).execute()


@router.get("s")
def get_rooms(limit: int = 10, offset: int = 0):
    return GetRoomsService(limit=limit, offset=offset).execute()


@router.post("/participant/ban")
def ban_participant(model: BanParticipant, user_id=Depends(middlewares.get_user_id_from_token)):
    return BanService(model=model, user_id=user_id, action='ban').execute()


@router.post("/participant/unban")
def unban_participant(model: BanParticipant, user_id=Depends(middlewares.get_user_id_from_token)):
    return BanService(model=model, user_id=user_id, action='unban').execute()
