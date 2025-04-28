import json
from operator import itemgetter

from data.repositories.postgres.room import RoomRepository
from data.utils.query_utils import QueryFilter
from services.base_service import BaseService
from services.microservices.core import CoreService
from services.room_service import RoomManagementService


class GetRoomsService(BaseService):
    def __init__(self, limit: int = 10, offset: int = 0):
        super().__init__()
        self.limit = limit
        self.offset = offset

        self.room_repository = RoomRepository()
        self.room_service = RoomManagementService()
        self.core_service = CoreService()

    def validate(self):
        pass

    def process(self):
        all_rooms = {}
        rooms_list = self.room_service.list_rooms()
        for room in rooms_list:
            metadata = json.loads(room.metadata) if room.metadata else {}
            if metadata.get('isStarted', False) is False or metadata.get('isEnded', False) or \
                    self.check_owner_is_in_room(room.name) is False:
                continue

            all_rooms[room.name] = {
                'id': metadata.get('room_id'),
                'name': room.name,
                'participants_count': room.num_participants,
            }

        if not all_rooms:
            return {'rooms': []}

        rooms = self.room_repository.get_by_query_filters(query_filters=[
            QueryFilter(key="name", value=tuple([a for a in all_rooms.keys()]), operation='in')
        ], limit=self.limit, offset=self.offset, order_by='id asc')

        if not rooms:
            return {'rooms': []}

        result = []
        for room in rooms:
            item = all_rooms[room['name']]
            item.update({
                'id': room['id'],
                'description': room['metadata'].get('description'),
                'products': room['metadata'].get('products', []),
                'thumbnail': room['metadata'].get('thumbnail'),
                'link': f"https://basalam.com/live/{room['id']}"
            })

            owner = room['metadata'].get('vendor', {}).get('owner', self.core_service.get_user_data(room['owner_id']))
            item.update({'owner': owner})
            result.append(item)

        result.sort(key=itemgetter('participants_count'), reverse=True)
        return {'rooms': result}

    def check_owner_is_in_room(self, room_name):
        participants = self.room_service.list_participants(room_name)
        for participant in participants:
            if room_name.split('-')[0] == participant.identity:
                return True

        return False
