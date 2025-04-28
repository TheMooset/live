from config import config
from data.connections.base_postgres import Database,Postgres


class PostgresCore(Postgres):
    database = Database(user=config.postgres_user, password=config.postgres_pass, host=config.postgres_host,
                        port=config.postgres_port, database=config.postgres_database, conn_name="core")


class PostgresLive(Postgres):
    database = Database(user=config.postgres_live_user, password=config.postgres_live_pass,
                        host=config.postgres_live_host, port=config.postgres_live_port,
                        database=config.postgres_live_database, conn_name="live")
