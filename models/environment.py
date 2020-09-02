# -*- encoding: utf-8 -*-

from utils.db.redis_conn import redis_cli
from constants import constants
from err_codes import SevenThirtyException, error_codes


async def get_latest_humi_and_temp(plant_id):
    """
        获取最近的温湿度
    """
    latest_humi = await redis_cli.get(constants.REDIS_LATEST_HUMI_PREFIX + plant_id)
    latest_temp = await redis_cli.get(constants.REDIS_LATEST_TEMP_PREFIX + plant_id)
    if not latest_humi or not latest_temp:
        raise SevenThirtyException(**error_codes.GET_LATEST_HUMI_OR_TEMP_FAIL)
    return latest_humi, latest_temp
