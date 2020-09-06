# -*- encoding: utf-8 -*-

""" 存储常量 """

from dataclasses import dataclass

@dataclass
class Constants():
    """ 常量 """

    # 最近5张照片的名称
    REDIS_LATEST_TIME_POINTER = 'latest_time_pointer'
    # 最近的环境温湿度, 需要配合plant_id使用
    REDIS_LATEST_HUMI_PREFIX = 'latest_humi'
    REDIS_LATEST_TEMP_PREFIX = 'latest_temp'

    # 照片链接的前缀和后缀
    PLANT_IMG_CDN_PREFIX = 'http://seven-thirty-mini.xinyu1997.tech/'
    PLANT_IMG_CDN_SUFFIX = '.jpg'

    # 植株类型映射
    INDEX_TYPE = {
        1: '满天星'
    }


constants = Constants()
