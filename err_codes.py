# -*- encoding: utf-8 -*-

""" 响应错误码 """

from dataclasses import dataclass


class SevenThirtyException(Exception):
    """ 基础错误类 """

    def __init__(self, code, message) -> None:
        super().__init__(self)
        self.code = code
        self.message = message

    def __str__(self):
        return "[{}] {}".format(str(self.code), self.message)


@dataclass
class ErrorCodes():
    """ 错误码及错误信息映射 """

    CONN_POOL_INIT_FAIL = {
        "code": 5001,
        "message": "mysql connection pool init fail"
    }
    REDIS_CONNECTION_FAIL = {
        "code": 5002,
        "message": "redis connection or auth fail"
    }
    GET_LATEST_TIME_POINTER_FAIL = {
        "code": 5003,
        "message": "get latest time pointer from redis failed"
    }
    GET_LATEST_HUMI_OR_TEMP_FAIL = {
        "code": 5004,
        "message": "get latest humidity or tempature failed"
    }
    INVALID_TOKEN = {
        "code": 7001,
        "message": "invalid token"
    }
    WX_INVALID_CODE = {
        "code": 10001,
        "message": "invalid code"
    }
    WX_REGISTER_FAIL = {
        "code": 10002,
        "message": "can not get openid with code"
    }
    WX_INVALID_ENCRYPTED_DATA = {
        "code": 10003,
        "message": "invalid encrypted data"
    }


error_codes = ErrorCodes()
