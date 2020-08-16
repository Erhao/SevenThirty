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

    WX_BAD_CODE = {
        "code": 10001,
        "message": "invalid code"
    }

    WX_REGISTER_FAIL = {
        "code": 10001,
        "message": "can not get openid with code"
    }


error_codes = ErrorCodes()
