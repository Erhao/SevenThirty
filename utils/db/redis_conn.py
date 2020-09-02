# -*- encoding: utf-8 -*-

import redis

from err_codes import SevenThirtyException, error_codes
from config.conf_local import local_conf
from config.wx_conf import config as wx_config


def gen_redis_cli():
    """
        生成redis客户端
    """
    try:
        rds = redis.StrictRedis(host=local_conf.redis['HOST'], port=local_conf.redis['PORT'], db=local_conf.redis['DB'], password=local_conf.redis['PASSWORD'])
    except:
        raise SevenThirtyException(**error_codes.REDIS_CONNECTION_FAIL)
    return rds

redis_cli = gen_redis_cli()