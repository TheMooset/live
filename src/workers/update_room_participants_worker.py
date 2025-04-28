import time
from sentry_sdk import capture_exception
from data.repositories.postgres.room import RoomRepository
from data.utils.query_utils import QueryFilter
from services.room_service import RoomManagementService


def run_worker():
    try:
        room_repository = RoomRepository()
        room_service = RoomManagementService()
        while True:
            time.sleep(10)
            try:
                current_rooms = room_service.list_rooms()

                if not current_rooms:
                    continue

                rooms = room_repository.get_by_query_filters(query_filters=[
                    QueryFilter(key="name", value=tuple([a.name for a in current_rooms]), operation='in')
                ])

                if not rooms:
                    continue
                rooms = {a['name']: a for a in rooms}

                for current_room in current_rooms:
                    if current_room.name in rooms:
                        active_participants = current_room.num_participants
                        rooms[current_room.name].update({
                            'active_participants': active_participants,
                            'max_participants': max(active_participants, rooms[current_room.name]['max_participants'])
                        })

                room_repository.transaction.begin()
                for room in rooms.values():
                    room_repository.transaction.update_entity(room['id'], {
                        'active_participants': room['active_participants'],
                        'max_participants': room['max_participants'],
                    })
                room_repository.transaction.save_changes()

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
