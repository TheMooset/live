from data.connections.postgres import PostgresLive
from data.utils.query_utils import QueryBuilder


class RoomParticipantRepository(PostgresLive):
    def __init__(self, **kwargs):
        super().__init__(query_builder=QueryBuilder(table_name="room_participants", schema_name="live_shopping"),
                         **kwargs)

    def get_participant_data(self, room_id: int, identity: str):
        query = f"""
        with cte as (
        select *
        from live_shopping.room_participants
        where room_id = %(room_id)s
        and (device_id = %(identity)s or user_id::text = %(identity)s)
        order by id desc
        limit 1
        )
        select cte.*, rb.id as ban_id, rb."type" as ban_type
        from cte
        left join live_shopping.room_bans rb on cte.room_id = rb.room_id and rb.deleted_at isnull 
            and (cte.device_id = rb.device_id or (cte.user_id notnull and cte.user_id = rb.user_id))
        """

        return self.select(query=query, params={'room_id': room_id, 'identity': identity})
