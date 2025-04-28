import json
import livekit

from api.schemas.join_room import JoinRoom
from config import config
from config.constants import admin_participants
from config.enums import BanTypeEnums, ErrorCodeEnums
from data.repositories.postgres.room import RoomRepository
from data.repositories.postgres.room_participant import RoomParticipantRepository
from data.repositories.postgres.room_ban import RoomBanRepository
from services.base_service import BaseService
from services.microservices.core import CoreService


class JoinRoomService(BaseService):
    def __init__(self, model: JoinRoom, user_id: int = None):
        super().__init__()
        self.model = model
        self.user_id = user_id
        self.room = None

        self.room_repository = RoomRepository()
        self.core_service = CoreService()
        self.room_ban_repository = RoomBanRepository()
        self.room_participant_repository = RoomParticipantRepository(master_repo=self.room_repository)

    def validate(self):
        self.room = self.room_repository.get_room_data(self.model.room_id)

        if not self.room:
            self.add_error('چنین پخش زنده ای وجود ندارد', error_code=ErrorCodeEnums.room_not_found.value)
            return

        self.room = self.room[0]
        if self.room['end_time'] is not None:
            self.add_error('این پخش زنده به پایان رسیده است', error_code=ErrorCodeEnums.room_ended.value)
            return

        if self.room_ban_repository.check_user_is_ban(self.model.room_id, self.model.device_id,
                                                      [BanTypeEnums.join_room.value], self.user_id):
            self.add_error(message='شما امکان ورود مجدد به این پخش زنده را ندارید',
                           error_code=ErrorCodeEnums.user_is_ban.value)

    def process(self):
        user = self.core_service.get_user_data(self.user_id)

        user_metadata = dict()
        for key in ['hash_id', 'avatar']:
            user_metadata[key] = user[key]

        self.room_repository.transaction.begin()
        self.room_participant_repository.transaction.add_entity(
            {
                'room_id': self.room['id'],
                'user_id': self.user_id,
                'device_id': self.model.device_id,
                'metadata': json.dumps({'user': user_metadata}),
            }
        )
        self.room_repository.transaction.update_entity(self.room['id'], {
            'active_participants': self.room['active_participants'] + 1
        })
        self.room_repository.transaction.save_changes()

        kwargs = {'room': self.room['name']}
        kwargs.update(self.room['participant_permissions'])
        if self.user_id == self.room['owner_id']:
            kwargs.update(admin_participants)

        identity = user['id'] if user['id'] else self.model.device_id
        grant = livekit.VideoGrant(**kwargs)
        access_token = livekit.AccessToken(api_key=config.LIVEKIT_API_KEY, api_secret=config.LIVEKIT_API_SECRET,
                                           grant=grant, identity=str(identity), name=user['name'],
                                           metadata=json.dumps({'user': user_metadata}))
        token = access_token.to_jwt()

        return {'is_admin': self.user_id == self.room['owner_id'], 'token': token}
