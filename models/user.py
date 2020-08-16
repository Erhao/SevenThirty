# -*- encoding: utf-8 -*-

""" User表数据库操作 """

from utils.db.connector import get_cursor


async def test():
    pool, conn, cur = await get_cursor()
    sql = """
        SELECT * FROM user;
    """
    try:
        await cur.execute(sql)
        # 返回为二维元组
        users = await cur.fetchall()
    finally:
        await pool.release(conn)
    return users
