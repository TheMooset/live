from services.base_service import BaseService
from data.connections.postgres import PostgresCore, PostgresLive


class ReadHealthCheckService(BaseService):
    def __init__(self):
        super().__init__()

    def validate(self):
        pass

    def process(self):
        result = True
        health_check_data = {"postgres_core": False, "postgres_live": False}
        try:
            conn = PostgresCore.get_connection()
            cursor = conn.cursor()
            cursor.execute("select 1")
            cursor.close()
            health_check_data.update({'postgres_core': True})
        except Exception:
            result = False

        try:
            conn = PostgresLive.get_connection(get_master_connection=True)
            cursor = conn.cursor()
            cursor.execute("select pg_is_in_recovery()")
            row = cursor.fetchone()
            if row['pg_is_in_recovery'] is False:
                health_check_data.update({'postgres_live': True})
            else:
                result = False
            cursor.close()
        except Exception:
            result = False

        return {"result": result, "data": health_check_data}
