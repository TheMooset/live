import time
from sentry_sdk import capture_exception
from data.repositories.postgres.room import RoomRepository
from data.utils.query_utils import QueryFilter
from services.delete_room_service import DeleteRoomService
from services.get_rooms_service import GetRoomsService
from services.room_service import RoomManagementService

SLEEP_TIME_SECONDS = 60
REMOVE_WAIT_TIME_MINUTES = 5


def run_worker():
    _rooms = {}
    try:
        room_repository = RoomRepository()
        room_service = RoomManagementService()
        rooms_service = GetRoomsService()
        while True:
            print(_rooms)
            time.sleep(SLEEP_TIME_SECONDS)
            try:
                all_rooms = room_service.list_rooms()
                active_rooms = [a.name for a in all_rooms]
                for room in _rooms:
                    if room not in active_rooms:
                        del _rooms[room]

                for active_room in active_rooms:
                    inactive_time = _rooms.get(active_room, 0)
                    if rooms_service.check_owner_is_in_room(active_room):
                        _rooms.update({active_room: inactive_time})
                    else:
                        _rooms.update({active_room: inactive_time + 1})

                inactive_room_names = [a for a in _rooms if _rooms[a] >= REMOVE_WAIT_TIME_MINUTES]
                if len(inactive_room_names) == 0:
                    continue

                inactive_rooms = room_repository.get_by_query_filters(query_filters=[
                    QueryFilter(key="name", value=tuple(inactive_room_names), operation='in')
                ])

                for inactive_room in inactive_rooms:
                    try:
                        service = DeleteRoomService(room_id=inactive_room['id'], user_id=inactive_room['owner_id'])
                        service.room = inactive_room
                        service.process()
                    except Exception as e:
                        print(inactive_room['id'], inactive_room['name'], e)

            except Exception as ex:
                print(str(ex))
                capture_exception(ex)

    except KeyboardInterrupt:
        print('Aborted by user')
    except Exception as ex:
        print(str(ex))
        capture_exception(ex)


if __name__ == '__main__':
    run_worker()
