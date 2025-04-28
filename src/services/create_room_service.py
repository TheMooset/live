import json
import time
from pydantic import BaseModel

from api.schemas.create_room import CreateRoom
from config.enums import UserVerificationStatusEnums
from data.repositories.postgres.room import RoomRepository
from data.repositories.postgres.room_type import RoomTypeRepository
from data.utils.query_utils import QueryFilter
from services.base_service import BaseService
from services.delete_room_service import DeleteRoomService
from services.microservices.core import CoreService, User
from services.room_service import RoomManagementService


class Vendor(BaseModel):
    id: int
    title: str
    identifier: str
    owner: User


class Product(BaseModel):
    id: int
    title: str
    price: str
    photo: str
    has_variation: bool

    def __init__(self, **data):
        if data['photo'] is not None:
            data['photo'] = data['photo']['small']

        super().__init__(**data)


class CreateRoomService(BaseService):
    def __init__(self, model: CreateRoom, token: str):
        super().__init__()
        self.model = model
        self.token = token

        self.user = None

        self.room_service = RoomManagementService()
        self.room_repository = RoomRepository()
        self.core_service = CoreService()

    def validate(self):
        self.user = self.core_service.current_user_data(token=self.token)

        if self.user['vendor'] is None:
            self.add_error('شما غرفه ای ندارید!')
            return

        if self.user['info_verification_status']['id'] != UserVerificationStatusEnums.accepted.value \
                and self.user['id'] not in [430, 4936634]:
            self.add_error('هویت شما هنوز احراز نشده است!')

    def process(self):
        self.remove_user_old_rooms()
        room_name = str(self.user['id']) + '-' + str(int(time.time()))[-6:]
        vendor = Vendor(**{**self.user['vendor'], 'owner': self.user}).dict()
        products = [Product(**a).dict() for a in self.core_service.products_by_ids(self.model.product_ids)]
        metadata = {'description': self.model.description, 'vendor': vendor, 'products': products}

        self.room_repository.transaction.begin()
        self.room_repository.transaction.add_entity({
            'name': room_name,
            'owner_id': self.user['id'],
            'subject': self.model.subject,
            'description': self.model.description,
            'metadata': json.dumps(metadata),
            'type_id': RoomTypeRepository().get_by_title(self.model.type.value)['id']
        })
        room_id = self.room_repository.transaction.fetch_results()[0]['id']
        self.room_repository.transaction.save_changes()

        metadata['room_id'] = room_id
        metadata = json.dumps(metadata)
        self.room_repository.transaction.begin()
        self.room_repository.transaction.update_entity(room_id, {'metadata': metadata})
        self.room_repository.transaction.save_changes()

        room = self.room_service.create_custom_room(name=room_name, metadata=metadata)

        return {'room': {'id': room_id, 'name': room.name, 'creation_time': room.creation_time}}

    def remove_user_old_rooms(self):
        rooms = self.room_repository.get_by_query_filters(query_filters=[
            QueryFilter(key="owner_id", value=self.user['id']),
            QueryFilter(key="end_time", value=None, operation='is')
        ])

        for room in rooms:
            try:
                service = DeleteRoomService(room_id=room['id'], user_id=self.user['id'], set_delay=False)
                service.room = room
                service.process()
            except Exception as e:
                print(e)
