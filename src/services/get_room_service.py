from api.schemas.update_room import UpdateRoom
from data.repositories.postgres.room import RoomRepository
from data.utils.query_utils import QueryFilter
from services.base_service import BaseService
from services.microservices.core import CoreService
from services.room_service import RoomManagementService
from services.update_room_service import UpdateRoomService


class GetRoomService(BaseService):
    def __init__(self, room_id: int = None, room_name: str = None):
        super().__init__()
        self.room_id = room_id
        self.room_name = room_name

        self.room_repository = RoomRepository()
        self.room_service = RoomManagementService()
        self.core_service = CoreService()

    def validate(self):
        if self.room_id is None and self.room_name is None:
            self.add_error('یکی از فیلد های آیدی و یا نام پخش زنده اجباری است')

    def process(self):
        query_filters = []
        if self.room_id:
            query_filters.append(QueryFilter(key="id", value=self.room_id))
        elif self.room_name:
            query_filters.append(QueryFilter(key="name", value=self.room_name))
        room = self.room_repository.get_by_query_filters(query_filters=query_filters)

        if not room:
            return {'data': {'room': None}}
        room = room[0]
        all_rooms = self.room_service.list_rooms()
        for item in all_rooms:
            if room['name'] == item.name:
                if not item.metadata:
                    room['metadata'].update({'room_id': room['id']})
                    UpdateRoomService(model=UpdateRoom(room_id=room['id'], metadata=room['metadata']),
                                      user_id=room['owner_id']).execute()

        owner = room['metadata'].get('vendor', {}).get('owner', self.core_service.get_user_data(room['owner_id']))
        room.update({'owner': owner})

        return {'data': {'room': room}}
