from livekit._proto.livekit_models_pb2 import ParticipantPermission

from api.schemas.ban_participant import BanParticipant
from config.enums import BanTypeEnums
from data.repositories.postgres.room import RoomRepository
from data.repositories.postgres.room_participant import RoomParticipantRepository
from data.repositories.postgres.room_ban import RoomBanRepository
from data.utils.query_utils import QueryFilter
from services.base_service import BaseService
from services.room_service import RoomManagementService


class BanService(BaseService):
    def __init__(self, model: BanParticipant, user_id: int, action: str = 'ban'):
        super().__init__()
        self.model = model
        self.user_id = user_id
        self.action = action
        self.room = None
        self.participant = None

        self.room_service = RoomManagementService()
        self.room_repository = RoomRepository()
        self.room_ban_repository = RoomBanRepository()
        self.room_participant_repository = RoomParticipantRepository()

    def validate(self):
        self.room = self.room_repository.get_by_query_filters(query_filters=[
            QueryFilter(key="id", value=self.model.room_id)
        ])

        if not self.room:
            self.add_error('چنین پخش زنده ای وجود ندارد')
            return

        self.room = self.room[0]
        if self.room['owner_id'] != self.user_id:
            self.add_error('این پخش زنده متعلق به شما نیست')
            return

        self.participant = self.room_participant_repository.get_participant_data(self.model.room_id, self.model.identity)
        if not self.participant:
            self.add_error('چنین عضوی در پخش زنده وجود ندارد')
            return

        self.participant = self.participant[0]
        if self.action == 'ban' and self.participant['ban_type'] == self.model.ban_type.value:
            self.add_error('این کاربر قبلا بن شده است')
            return

        if self.action == 'unban' and self.participant['ban_id'] is None:
            self.add_error('این کاربر قبلا بن نشده است')

    def process(self):
        new_permissions = None
        self.room_ban_repository.transaction.begin()
        if self.action == 'ban':
            if self.model.ban_type == BanTypeEnums.join_room:
                # change permissions before removing participant
                self.room_service.update_participant(room=self.room['name'], identity=self.model.identity,
                                                     permission=ParticipantPermission(can_subscribe=False))
                self.room_service.remove_participant(self.room['name'], self.model.identity)

            elif self.model.ban_type == BanTypeEnums.add_comment:
                new_permissions = ParticipantPermission(can_subscribe=True, can_publish_data=False)

            elif self.model.ban_type == BanTypeEnums.remove_from_room:
                self.room_service.remove_participant(self.room['name'], self.model.identity)

            self.room_ban_repository.transaction.add_entity({
                'room_id': self.model.room_id,
                'user_id': self.participant['user_id'],
                'device_id': self.participant['device_id'],
                'type': self.model.ban_type.value,
            })
        else:
            if self.model.ban_type == BanTypeEnums.add_comment:
                new_permissions = ParticipantPermission(can_subscribe=True, can_publish_data=True)

            self.room_ban_repository.transaction.soft_delete_by_query_filter(query_filters=[
                QueryFilter(key="id", value=self.participant['ban_id'])
            ])

        if new_permissions:
            self.room_service.update_participant(room=self.room['name'], identity=self.model.identity,
                                                 permission=new_permissions)

        self.room_ban_repository.transaction.save_changes()

        return {'result': True}
