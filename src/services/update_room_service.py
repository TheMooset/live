import json

from api.schemas.update_room import UpdateRoom
from data.repositories.postgres.room import RoomRepository
from data.utils.query_utils import QueryFilter
from services.base_service import BaseService
from services.room_service import RoomManagementService


class UpdateRoomService(BaseService):
    def __init__(self, model: UpdateRoom, user_id: int):
        super().__init__()
        self.model = model
        self.user_id = user_id
        self.room = None

        self.room_service = RoomManagementService()
        self.room_repository = RoomRepository()

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

        if self.room['end_time'] is not None:
            self.add_error('این پخش زنده تمام شده است')

    def process(self):
        metadata = json.dumps(self.model.metadata, default=str)
        self.room_service.update_room_metadata(self.room['name'], metadata)

        self.room_repository.transaction.begin()
        self.room_repository.transaction.update_entity(self.model.room_id, {'metadata': metadata})
        self.room_repository.transaction.save_changes()

        return {'result': True}
