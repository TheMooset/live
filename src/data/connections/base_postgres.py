from config import config
import psycopg2
from psycopg2 import extras
import psycopg2.extensions
from data.utils.query_utils import QueryBuilder, QueryFilter
from typing import List
from utils.time_utils import DateTimeUtils

DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    'DEC2FLOAT',
    lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)


class Database:
    def __init__(self, user, password, host, port, database, conn_name):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.conn_name = conn_name


class PostgresConnection:
    _connections = {}

    @classmethod
    def get_connection(cls, database: Database):
        conn_name = database.conn_name
        if conn_name not in cls._connections or cls._connections[conn_name].closed:
            cls._connections[conn_name] = cls.get_new_connection(database)
            cls._connections[conn_name].autocommit = True
        return cls._connections[conn_name]

    @classmethod
    def get_new_connection(cls, database: Database):
        return psycopg2.connect(user=database.user,
                                password=database.password,
                                host=database.host,
                                port=database.port,
                                database=database.database,
                                cursor_factory=extras.RealDictCursor,
                                application_name=config.app_title
                                )


class PostgresTransaction:
    def __init__(self, database: Database, master_repo, query_builder: QueryBuilder = None):
        self.query_builder = query_builder
        self.database = database
        if master_repo:
            if not hasattr(master_repo.transaction, 'cursor'):
                raise Exception("master entity does not have cursor object, call begin() on master entity transaction")
            self.cursor = master_repo.transaction.cursor
            self.conn = master_repo.transaction.conn
            self.is_master_repo = False
        else:
            self.is_master_repo = True  # only master repository can save changes

    def begin(self):
        if not self.is_master_repo:
            raise Exception("only master entity can begin transaction")
        self.conn = PostgresConnection.get_new_connection(self.database)
        self.cursor = self.conn.cursor()

    def execute(self, query, params=None):
        self.cursor.execute(query, params)

    def fetch_results(self):
        return self.cursor.fetchall()

    def save_changes(self):
        if self.is_master_repo:
            self.conn.commit()
            self.end()

    def end(self):
        self.cursor.close()
        self.conn.close()

    def rollback(self):
        if hasattr(self, "conn") and self.conn and self.is_master_repo:
            self.conn.rollback()
            self.conn.close()

    def add_entity(self, data: dict):
        self.execute(**self.query_builder.get_insert_query(data, return_values='id'))

    # todo add bulk insert
    def add_entities(self, data_list: List[dict]):
        for data in data_list:
            self.add_entity(data)

    def update_entity(self, entity_id: int, data: dict, return_values=None):
        self.execute(**self.query_builder.get_update_query(entity_id, data, return_values))

    def update_entity_by_query_filter(self, query_filters: List[QueryFilter], data: dict, return_values=None):
        self.execute(**self.query_builder.get_update_query_by_query_filter(query_filters, data, return_values))

    def soft_delete_by_query_filter(self, query_filters: List[QueryFilter], delete_time=None):
        if not delete_time:
            delete_time = DateTimeUtils.get_time(string_format=True)
        self.update_entity_by_query_filter(query_filters=query_filters, data=dict(deleted_at=delete_time))

    def bulk_insert(self, insert_query, value_list, page_size=100):
        psycopg2.extras.execute_values(self.cursor, insert_query, value_list, template=None, page_size=page_size)


class BasePostgres:
    database = None

    def __init__(self, master_repo=None, query_builder: QueryBuilder = None):
        self.get_from_master_db = True
        self.query_builder = query_builder
        self.master_repo = master_repo
        self._transaction = None
        self.cached_value = None
        self.validate_params()

    def validate_params(self):
        raise NotImplemented


class Postgres(BasePostgres):
    def __init__(self, master_repo=None, query_builder: QueryBuilder = None):
        super().__init__(master_repo, query_builder)

    def validate_params(self):
        if self.query_builder:
            assert isinstance(self.query_builder, QueryBuilder)

    @property
    def transaction(self):
        if not self._transaction:
            self._transaction = PostgresTransaction(database=self.database, master_repo=self.master_repo,
                                                    query_builder=self.query_builder)
        return self._transaction

    @classmethod
    def get_connection(cls, get_master_connection=True):
        return PostgresConnection.get_connection(cls.database)

    @classmethod
    def select(cls, query, params=None, get_from_master=True):
        conn = cls.get_connection(get_master_connection=True)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        # cursor.close()
        return result

    # execute SQL queries without transaction
    @classmethod
    def execute(cls, query, params=None, fetch_result=False):
        result = None
        conn = cls.get_connection(get_master_connection=True)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        if fetch_result:
            result = cursor.fetchone()
        return result

    @classmethod
    def exist_entity(cls, query, params=None, get_from_master=True):
        conn = cls.get_connection(get_master_connection=True)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.rowcount
        return result > 0

    def get_by_query_filters(self, query_filters: List[QueryFilter], returning_items="*", get_from_master=False,
                             order_by=None, order_type=None, limit=None, offset=None):
        return self.select(
            **self.query_builder.get_select_query(query_filters, returning_items, order_by, order_type, limit, offset),
            get_from_master=get_from_master or self.get_from_master_db)

    def get_count_by_query_filters(self, query_filters: List[QueryFilter]):
        return self.select(**self.query_builder.get_count_query(query_filters), get_from_master=True)[0]['count']

    def exist_entity_by_query_filters(self, query_filters: List[QueryFilter], returning_items="id",
                                      get_from_master=False):
        return self.exist_entity(**self.query_builder.get_select_query(query_filters, returning_items),
                                 get_from_master=get_from_master or self.get_from_master_db)
