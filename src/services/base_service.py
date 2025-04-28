from abc import abstractmethod, ABC
from typing import List

from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_401_UNAUTHORIZED

from config import config
from config.enums import ErrorCodeEnums


class ServiceValidationError(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.http_error_code = HTTP_422_UNPROCESSABLE_ENTITY
        self.errors = errors if errors is not None else []

    def to_json(self):
        return {
            'http_status': self.http_error_code,
            'messages': self.errors
        }


class UnauthorizedError(Exception):
    def __init__(self, message='invalid authorization header'):
        super().__init__(message)
        self.http_error_code = HTTP_401_UNAUTHORIZED
        self.errors = [{
            "message": message,
            "code": 0,
            "fields": []
        }]

    def to_json(self):
        return {
            'http_status': self.http_error_code,
            'messages': self.errors
        }


class BaseService(ABC):
    def __init__(self, ):
        self.validation_errors = []
        self.process_time = None
        self.cached_entity = None

    def add_error(self, message: str, error_code: int = ErrorCodeEnums.default.value, fields: List = None):
        self.validation_errors.append({"message": message,
                                       "code": error_code,
                                       "fields": fields if fields is not None else []})

    @abstractmethod
    def validate(self):
        pass

    def check_validations(self):
        if len(self.validation_errors) > 0:
            raise ServiceValidationError("service validation errors", self.validation_errors)

    def pre_process(self):
        pass

    @abstractmethod
    def process(self):
        pass

    def rollback_connections(self):
        if hasattr(self, "repository"):
            self.repository.transaction.rollback()

    def execute(self):
        try:
            self.validate()
            self.check_validations()
            self.pre_process()
            return self.process()
        except Exception as ex:
            if not config.debug:
                self.rollback_connections()
            raise ex

