# -*- encoding: utf-8 -*-

import time

from .client import MqttClient
from config.conf_local import local_conf


def sub_soil_moisture():
    # 启动mqtt监听
    # 在多进程中使用mqtt需要重新init client
    print('sub_soil_moisture start listening...')
    mqtt_cli = MqttClient('stp-sub_soil_moisture')
    mqtt_cli.mqtt_connect()
    mqtt_cli.mqtt_subscribe(local_conf.mqtt_broker['SUB_SOIL_MOISTURE_TOPIC'])


def sub_temp_humi():
    # 启动mqtt监听
    # 在多进程中使用mqtt需要重新init client
    print('sub_temp_humi start listening...')
    mqtt_cli = MqttClient('stp-sub_temp_humi')
    mqtt_cli.mqtt_connect()
    mqtt_cli.mqtt_subscribe(local_conf.mqtt_broker['SUB_TEMP_HUMI_TOPIC'])


def pub_watering_cmd(req, sign_data):
    print('pub_watering_cmd published.', req.plant_id, sign_data['openid'])
    mqtt_cli = MqttClient('stp-pub_watering_cmd')
    mqtt_cli.mqtt_connect()
    time_stamp = int(time.time())
    print('[EMQTT-pub]:', local_conf.mqtt_broker['PUB_TOPIC_PREFIX'] + str(req.plant_id) + '/' + sign_data['openid'] + '/' + str(time_stamp))
    mqtt_cli.mqtt_publish(
        local_conf.mqtt_broker['PUB_TOPIC_PREFIX'] + str(req.plant_id) + '/' + sign_data['openid'] + '/' + str(time_stamp),
        local_conf.mqtt_payload['WATERING'],
        qos=2
    )
    return
