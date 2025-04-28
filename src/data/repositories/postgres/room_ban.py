from typing import List

from data.connections.postgres import PostgresLive
from data.utils.query_utils import QueryBuilder


class RoomBanRepository(PostgresLive):
    def __init__(self, **kwargs):
        super().__init__(query_builder=QueryBuilder(table_name="room_bans", schema_name="live_shopping"),
                         **kwargs)

    def check_user_is_ban(self, room_id: int, device_id: str, ban_type: List[str], user_id: int = None):
        query = f"""
        select *
        from live_shopping.room_bans
        where room_id = %(room_id)s
        and type in %(ban_type)s
        and (device_id = %(device_id)s or (user_id notnull and user_id = %(user_id)s))
        and deleted_at isnull
        """

        return self.select(query=query, params={'room_id': room_id, 'ban_type': tuple(ban_type),
                                                'device_id': device_id, 'user_id': user_id})
