# -*- encoding: utf-8 -*-

""" User表数据库操作 """

from utils.db.connector import get_cursor
from utils.qiniu_tool import upload_to_qiniu


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
    """
        保存openid
    """
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


async def wx_register_userinfo(openid, user_info):
    """
        保存用户基本信息
    """
    qiniu_avatarurl = await upload_to_qiniu(user_info['avatarUrl'])

    pool, conn, cur = await get_cursor()
    save_user_info_sql = """
        UPDATE user
        SET nickname = %s, gender = %s, language = %s, city = %s, province = %s, country = %s, avatarurl = %s
        WHERE openid = %s;
    """
    await cur.execute(
        save_user_info_sql,
        (user_info['nickName'], user_info['gender'], user_info['language'], user_info['city'], user_info['province'], user_info['country'], qiniu_avatarurl, openid)
    )
    await pool.release(conn)
    return


async def get_primary_plant_id(openid):
    """
        获取用户设置的首页展示植株id
    """
    pool, conn, cur = await get_cursor()
    get_primary_plant_id_sql = """
        SELECT plant_id from user_plant where user_id = %s and is_primary_plant = 1 and is_del = 0
    """
    await cur.execute(get_primary_plant_id_sql, openid)
    primary_plant_id = await cur.fetchone() or 1
    await pool.release(conn)
    return primary_plant_id