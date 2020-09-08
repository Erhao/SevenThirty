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
        存储openid
    """
    pool, conn, cur = await get_cursor()
    get_user_with_openid_sql = """
        SELECT openid FROM user WHERE openid = %s;
    """
    await cur.execute(get_user_with_openid_sql, openid)
    is_exist = await cur.fetchone()
    if not is_exist:
        # 新注册未授权用户的serial都为数据库设置的默认值-1
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
    # 如果是之前授过权的老用户则不需要更新serial
    check_is_old_authoried_user_sql = """
        SELECT serial FROM user WHERE openid = %s AND serial >= 0
    """
    await cur.execute(check_is_old_authoried_user_sql)
    is_old_authoried_user = await cur.fetchone()

    new_serial = -1
    if not is_old_authoried_user:
        # 先获取最大的serial
        get_max_serial_sql = """
            SELECT MAX(serial) FROM user;
        """
        await cur.execute(get_max_serial_sql)
        max_serial = await cur.fetchone()
        new_serial = max_serial[0] + 1
    else:
        new_serial = is_old_authoried_user[0]
    save_user_info_sql = """
        UPDATE user
        SET serial = %s, nickname = %s, gender = %s, language = %s, city = %s, province = %s, country = %s, avatarurl = %s
        WHERE openid = %s;
    """
    await cur.execute(
        save_user_info_sql,
        (new_serial, user_info['nickName'], user_info['gender'], user_info['language'], user_info['city'], user_info['province'], user_info['country'], qiniu_avatarurl, openid)
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
    primary_plant = await cur.fetchone()
    primary_plant_id = primary_plant[0] or 1
    await pool.release(conn)
    return primary_plant_id


async def get_user(openid):
    """
        获取用户的详细信息
    """
    pool, conn, cur = await get_cursor()
    get_user_sql = """
        SELECT * FROM user WHERE openid = %s
    """
    await cur.execute(get_user_sql, openid)
    user = await cur.fetchone()
    await pool.release(conn)
    return user


async def get_users(openids):
    """
        批量获取用户的详细信息
    """
    pool, conn, cur = await get_cursor()
    get_users_sql = """
        SELECT * FROM user WHERE openid IN ({})
    """.format(','.join(["'" + openid + "'" for openid in openids]))
    await cur.execute(get_users_sql)
    users = await cur.fetchall()
    await pool.release(conn)
    return users


async def get_user_plants(openid):
    """
        获取用户所有的养护花株
    """
    pool, conn, cur = await get_cursor()
    get_user_plants_sql = """
        SELECT plant_id, is_primary_plant, watering_times FROM user_plant WHERE user_id = %s
    """
    await cur.execute(get_user_plants_sql, openid)
    user_plants = await cur.fetchall()
    plant_ids = [ user_plant[0] for user_plant in user_plants ]
    get_plants_sql = """
        SELECT * FROM plant WHERE id IN ({})
    """.format(','.join([str(plant_id) for plant_id in plant_ids]))
    await cur.execute(get_plants_sql)
    plants = await cur.fetchall()
    await pool.release(conn)
    return user_plants, plants


async def get_rank_list(plant_id):
    """
        获取植株的养护排名
    """
    pool, conn, cur = await get_cursor()
    get_rank_list_sql = """
        SELECT user_id, plant_id, is_primary_plant, watering_times FROM user_plant WHERE plant_id = %s AND watering_times > %s ORDER BY watering_times DESC LIMIT 10
    """
    await cur.execute(get_rank_list_sql, (plant_id, 0))
    user_plants = await cur.fetchall()
    user_ids = [ user_plant[0] for user_plant in user_plants ]
    users = await get_users(user_ids)
    await pool.release(conn)
    return user_plants, users
