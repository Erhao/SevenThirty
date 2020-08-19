# -*- encoding: utf-8 -*-

""" User表数据库操作 """

from utils.db.connector import get_cursor


async def test():
    pool, conn, cur = await get_cursor()
    sql = """
        SELECT * FROM user where openid = %s;
    """
    users = []
    await cur.execute(sql, "oGhRu5dXuJHs-01JTwYUFQqZD0_1")
    # 返回为二维元组
    users = await cur.fetchall()
    await pool.release(conn)
    print('--------------users', users)
    return users


async def wx_register_openid(openid):
    pool, conn, cur = await get_cursor()
    get_user_with_openid_sql = """
        SELECT openid FROM user WHERE openid = %s;
    """
    await cur.execute(get_user_with_openid_sql, openid)
    is_exist = await cur.fetchone()
    if not is_exist:
        insert_sql = """
            INSERT INTO user(openid) VALUES (%s);
        """
        await cur.execute(insert_sql, openid)
    await pool.release(conn)
    return
