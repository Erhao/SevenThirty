# -*- encoding: utf-8 -*-

""" 计算积分 """

from utils.db.connector import get_cursor


async def get_user_all_points(openid):
    """
        获取用户所有积分
    """
    pool, conn, cur = await get_cursor()
    get_user_all_points_sql = """
        SELECT SUM(point) FROM user_plant WHERE user_id = %s
    """
    await cur.execute(get_user_all_points_sql, openid)
    user_all_points_res = await cur.fetchone()
    await pool.release(conn)
    return user_all_points_res[0]


async def update_point_and_rank():
    """
        更新user表的point和rank字段
    """
    # user_plant表中用户所有养护过的花株的point值求和
    pool, conn, cur = await get_cursor()
    # 获取所有已授权用户的openid
    get_all_authorized_openids_sql = """
        SELECT `openid` FROM user WHERE serial >= %s AND is_del = %s
    """
    await cur.execute(get_all_authorized_openids_sql, (0, 0))
    all_authorized_openids_res = await cur.fetchall()
    all_authorized_openids = [ item[0] for item in all_authorized_openids_res ]
    if not all_authorized_openids:
        return
    # 获取每个用户所有养护花株的积分
    openid_points = []
    for openid in all_authorized_openids:
        points_sum = await get_user_all_points(openid)
        openid_points.append({
            "openid": openid,
            "points_sum": points_sum,
        })
    stride = int(100 / len(openid_points))
    # 按照points_sum排序
    sorted_openid_points = sorted(openid_points, key=lambda item: item['points_sum'], reverse=True)
    # 计算rank
    for index, openid_point in enumerate(sorted_openid_points):
        openid_point['rank'] = stride + stride * index
    # 更新user表的point和rank字段
    update_point_and_rank_sql = """
        UPDATE user
        SET `point` = %s, `rank` = %s
        WHERE openid = %s
    """
    for openid_point in sorted_openid_points:
        await cur.execute(update_point_and_rank_sql, (openid_point['points_sum'], openid_point['rank'], openid_point['openid']))
    await pool.release(conn)
    return