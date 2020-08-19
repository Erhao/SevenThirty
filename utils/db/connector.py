# -*- encoding: utf-8 -*-

""" 数据库连接 """

import asyncio
import aiomysql

from config.conf_local import DATABASE
from err_codes import SevenThirtyException, error_codes


MYSQL_CONFIG = DATABASE['default']

async def register_conn_pool():
    """
        注册连接池
    """
    try:
        pool = await aiomysql.create_pool(host=MYSQL_CONFIG['HOST'], port=MYSQL_CONFIG['PORT'], user=MYSQL_CONFIG['USER'], password=MYSQL_CONFIG['PASSWORD'], db=MYSQL_CONFIG['DB_NAME'], charset=MYSQL_CONFIG['CHARSET'], autocommit=True)
        return pool
    except Exception as e:
        raise SevenThirtyException(**error_codes.CONN_POOL_INIT_FAIL)


async def get_cursor():
    """
        从连接池中获取连接
    """
    pool = await register_conn_pool()
    conn = await pool.acquire()
    cur = await conn.cursor()
    return pool, conn, cur


# async def db_manager(func):
#     async def run(*args, **kwargs):
#         await db.connect()
#         result = await func(*args, **kwargs)
#         await db.disconnect()
#         return result
#     return await run


