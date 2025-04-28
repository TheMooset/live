from typing import List, Any
import orjson as json
from psycopg2.extensions import AsIs


class QueryFilter:
    def __init__(self, key: str, value: Any, operation="="):
        self.key = key
        self.value = value
        self.operation = operation.strip()


class QueryBuilder:
    def __init__(self, table_name, schema_name=None):
        self.table_name = f'"{table_name}"' if schema_name is None else f'"{schema_name}"."{table_name}"'
        self.query = None
        self.params = []
        self.return_values = None
        self.param_count = 0

    def _clear_params(self):
        self.param_count = 0
        self.params = []
        self.return_values = None

    def _add_param(self, param):
        self.params.append(param)
        self.param_count = self.param_count + 1
        return f"%s"

    def _set_data(self, return_values=None):
        self._clear_params()
        self.return_values = return_values

    def _get_result(self):
        if self.return_values is not None:
            self.query = self.query + f" RETURNING {self.return_values}"
        params = tuple(json.dumps(v).decode("utf-8")
                       if isinstance(v, dict) or (isinstance(v, list) and any(isinstance(a, dict) for a in v))
                       else v for v in self.params)
        return dict(query=self.query, params=params)

    def _generate_where_clause(self, query_filters):
        result = " where 1=1"
        for qf in query_filters:
            result = result + f" and \"{str(qf.key)}\" {qf.operation} {self._add_param(qf.value)}"
        return result

    def _generate_order_by_clause(self, order_clause: str):
        order_items = order_clause.split(',')
        return f" order by {','.join([self._add_param(AsIs(a)) for a in order_items])}"

    def get_insert_query(self, data: dict, return_values=None):
        self._set_data(return_values)
        self.query = f'''insert into {self.table_name} 
        ({",".join([f'"{a}"' for a in data])}) values ({",".join([self._add_param(a) for a in data.values()])})'''
        return self._get_result()

    def get_select_query(self, query_filters: List[QueryFilter], returning_items="*", order_by=None, order_type=None,
                         limit=None, offset=None):
        self._clear_params()
        self.query = f"""select {returning_items} from {self.table_name}  
        {self._generate_where_clause(query_filters)}"""
        if order_by:
            self.query = self.query + self._generate_order_by_clause(order_by)
        if order_type:
            self.query = self.query + f' {order_type}'
        if limit:
            if not isinstance(limit, int):
                raise Exception("limit must be int")
            self.query = self.query + f' limit {limit}'
        if offset:
            if not isinstance(offset, int):
                raise Exception("offset must be int")
            self.query = self.query + f' offset {offset}'
        return self._get_result()

    def get_count_query(self, query_filters: List[QueryFilter]):
        self._clear_params()
        self.query = f"""select count(*) from {self.table_name}  
                {self._generate_where_clause(query_filters)}"""
        return self._get_result()

    def get_update_query(self, entity_id, data: dict, return_values=None):
        self._set_data(return_values)
        self.query = f"""update {self.table_name} 
        set {','.join([f'{k} = {self._add_param(v)}' for k, v in data.items()])}
         where id = {self._add_param(entity_id)}"""
        return self._get_result()

    def get_update_query_by_query_filter(self, query_filters: List[QueryFilter], data, return_values=None):
        self._set_data(return_values)
        self.query = f"""update {self.table_name} set {','.join([f'{k} = {self._add_param(v)}' for k, v in data.items()])}
         {self._generate_where_clause(query_filters)}"""
        return self._get_result()

    def get_field_bulk_update_query(self, field_name, id_value_tuples: List[tuple], field_type=None):
        """
        :param field_type: type of field
        :param field_name: database field name for bulk update
        :param id_value_tuples: list of id,value tuples [(1,"val1"), (2,"val2")]. first tuple element must be table id
        :return:
        """

        def get_values(values):
            assert len(values) == 2, "each value must have only id and field_value data"

            updated_field_value = values[1]
            if not isinstance(updated_field_value, int):
                updated_field_value = f"'{values[1]}'" + (f"::{field_type}" if field_type else "")
            return f"({values[0]}, {updated_field_value})"

        values_str = ",".join(map(get_values, id_value_tuples))
        self.query = f"""update {self.table_name} set {field_name}=tmp.{field_name} from
        (values {values_str}) as tmp (id, {field_name})
        where {self.table_name}.id = tmp.id"""
        return dict(query=self.query, params=self.params)
