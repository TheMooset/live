from data.connections.postgres import PostgresLive
from data.utils.query_utils import QueryBuilder


class CommentRepository(PostgresLive):
    def __init__(self, **kwargs):
        super().__init__(query_builder=QueryBuilder(table_name="comments", schema_name="live_shopping"), **kwargs)

    def get_room_comments(self, room_id: id, limit: int, offset: int):
        query = f"""
        select id, room_id, user_id, comment, created_at
        from live_shopping.comments
        where room_id = %(room_id)s
        and deleted_at isnull
        order by id desc
        limit %(limit)s
        offset %(offset)s
        """

        return self.select(query=query, params={'room_id': room_id, 'limit': limit, 'offset': offset})
