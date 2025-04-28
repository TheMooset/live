import json
import time

from data.repositories.postgres.room import RoomRepository
from data.utils.query_utils import QueryFilter
from services.base_service import BaseService
from services.room_service import RoomManagementService
from utils.time_utils import DateTimeUtils


class DeleteRoomService(BaseService):
    def __init__(self, room_id: int, user_id: int, set_delay: bool = True):
        super().__init__()
        self.room_id = room_id
        self.user_id = user_id
        self.set_delay = set_delay
        self.room = None

        self.room_repository = RoomRepository()
        self.room_service = RoomManagementService()

    def validate(self):
        self.room = self.room_repository.get_by_query_filters(query_filters=[
            QueryFilter(key="id", value=self.room_id)
        ])

        if not self.room:
            self.add_error('چنین پخش زنده ای وجود ندارد')
            return

        self.room = self.room[0]
        if self.room['owner_id'] != self.user_id:
            self.add_error('این پخش زنده متعلق به شما نیست')

    def process(self):
        metadata = self.room['metadata']
        metadata['isEnded'] = True
        metadata = json.dumps(metadata, default=str)

        try:
            self.room_service.update_room_metadata(self.room['name'], metadata)
            delete_room = True
        except Exception as e:
            delete_room = False
            print(e)

        self.room_repository.transaction.begin()
        self.room_repository.transaction.update_entity(self.room_id, {'end_time': DateTimeUtils.get_time(True),
                                                                      'metadata': metadata})
        self.room_repository.transaction.save_changes()

        if delete_room:
            # add delay to show end live message to users
            if self.set_delay:
                time.sleep(2.5)

            self.room_service.delete_room(self.room['name'])

        return {'result': True}
