from data.connections.postgres import PostgresLive
from data.utils.query_utils import QueryBuilder


class RoomRepository(PostgresLive):
    def __init__(self, **kwargs):
        super().__init__(query_builder=QueryBuilder(table_name="rooms", schema_name="live_shopping"), **kwargs)

    def get_room_data(self, room_id):
        query = f"""
        select r.*, rt.participant_permissions
        from live_shopping.rooms r
        join live_shopping.room_types rt on rt.id = r.type_id
        where r.id = %(room_id)s
        """

        return self.select(query=query, params={'room_id': room_id})
