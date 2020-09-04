# -*- encoding: utf-8 -*-

from utils.db.connector import get_cursor
from constants import constants
from utils.db.redis_conn import redis_cli
from err_codes import SevenThirtyException, error_codes


async def get_plant(plant_id):
    """ 
        获取plant信息
    """
    pool, conn, cur = await get_cursor()
    get_plant_sql = """
        SELECT * FROM plant WHERE id = %s
    """
    await cur.execute(get_plant_sql, plant_id)
    plant = await cur.fetchone()
    await pool.release(conn)
    return plant


async def get_plant_imgs_with_same_time_pointer(plant_id):
    """
        获取plant的照片信息
    """
    redis_latest_time_pointer = redis_cli.get(constants.REDIS_LATEST_TIME_POINTER)
    if not redis_latest_time_pointer:
        raise SevenThirtyException(**error_codes.GET_LATEST_TIME_POINTER_FAIL)
    latest_time_pointer = int(redis_latest_time_pointer)
    pool, conn, cur = await get_cursor()
    get_plant_imgs_sql = """
        SELECT * FROM plant_img WHERE plant_id = %s and time_pointer = %s ORDER BY id DESC LIMIT 5
    """
    await cur.execute(get_plant_imgs_sql, (plant_id, latest_time_pointer))
    plant_imgs = await cur.fetchall()
    await pool.release(conn)
    return plant_imgs
