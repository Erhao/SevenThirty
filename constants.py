# -*- encoding: utf-8 -*-

""" 存储常量 """

from dataclasses import dataclass

@dataclass
class Constants():
    """ 常量 """

    # 最近5张照片的名称
    REDIS_LATEST_TIME_POINTER = 'latest_time_pointer'
    # 最近的环境温湿度, 需要配合plant_id使用
    REDIS_LATEST_HUMI_PREFIX = 'latest_humi_'
    REDIS_LATEST_TEMP_PREFIX = 'latest_temp_'
    # 最近的土壤湿度
    REDIS_LATEST_SOIL_MOISTURE_PREFIX = 'latest_soil_moisture_'
    # 最近一次浇水信息
    REDIS_LATEST_WATERING_INFO_PREFIX = 'latest_watering_info_'

    # 照片链接的前缀和后缀
    PLANT_IMG_CDN_PREFIX = 'http://seven-thirty-mini.xinyu1997.tech/'
    PLANT_IMG_CDN_SUFFIX = '.jpg'

    # 植株类型映射
    PLANT_TYPE = {
        1: '满天星',
    }

    WATERING_REQ_STATUS = {
        "success": "success",
        "rejected": "rejected",
    }

    SOIL_MOISTURE = {
        "WET": '1',
        "DRY": '0',
    }


constants = Constants()
