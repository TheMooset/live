from data.connections.postgres import PostgresLive
from data.utils.query_utils import QueryBuilder


class RoomTypeRepository(PostgresLive):
    def __init__(self, **kwargs):
        super().__init__(query_builder=QueryBuilder(table_name="room_types", schema_name="live_shopping"), **kwargs)

    def get_all(self):
        types = self.get_by_query_filters(query_filters=[])
        return [dict(a) for a in types]

    def get_all_dict(self):
        return {a['title']: a for a in self.get_all()}

    def get_by_title(self, title):
        return self.get_all_dict().get(title)
