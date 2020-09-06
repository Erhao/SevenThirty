# -*- encoding: utf-8 -*-

""" 持久化存储来自STPI的数据 """

import datetime

from utils.db.connector import get_cursor


async def save_img_url(img_url, dt, plant_id, camera_id, time_pointer):
    """
        保存照片的cdn链接
    """
    pool, conn, cur = await get_cursor()
    save_img_url_sql = """
        INSERT INTO plant_img(plant_id, img_url, capture_at, camera_id, time_pointer) VALUES(%s, %s, %s, %s, %s)
    """
    await cur.execute(save_img_url_sql, (plant_id, img_url, dt, camera_id, time_pointer))
    await pool.release(conn)
    return
