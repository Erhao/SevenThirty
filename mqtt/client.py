from threading import local
import paho.mqtt.client as mqtt
import time

import redis

from config.conf_local import local_conf
from utils.db.redis_conn import redis_cli
from constants import constants


class MqttClient():

    def __init__(self, client_id):
        self.client = mqtt.Client(client_id)
        self.client.on_message = self.on_message

    # 消息处理函数
    def on_message(self, client, user_data, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        if topic.startswith(local_conf.mqtt_broker['SUB_SOIL_MOISTURE_TOPIC_PREFIX']):
            self.handle_soil_moisture_msg(topic, payload)
        elif topic.startswith(local_conf.mqtt_broker['SUB_TEMP_HUMI_TOPIC_PREFIX']):
            self.handle_temp_humi_msg(topic, payload)
        return

    def mqtt_connect(self):
        self.client.connect(local_conf.mqtt_broker['HOST'], local_conf.mqtt_broker['PORT'], 60)

    def mqtt_publish(self, topic, payload, qos=2):
        self.client.publish(topic=topic, payload=payload, qos=qos)

    def mqtt_subscribe(self, topic, qos=2):
        self.client.subscribe(topic=topic, qos=qos)
        self.client.loop_forever()

    def handle_soil_moisture_msg(self, topic, payload):
        plant_id = int(topic.split('/')[2])
        if payload == '0' or payload == '1':
            redis_cli.set(constants.REDIS_LATEST_SOIL_MOISTURE_PREFIX + str(plant_id), payload)
        return

    def handle_temp_humi_msg(self, topic, payload):
        plant_id = int(topic.split('/')[2])
        temp, humi = payload.split('_')[0], payload.split('_')[1]
        redis_cli.set(constants.REDIS_LATEST_TEMP_PREFIX + str(plant_id), temp)
        redis_cli.set(constants.REDIS_LATEST_HUMI_PREFIX + str(plant_id), humi)
        return
