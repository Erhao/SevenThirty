# -*- encoding: utf-8 -*-

import sys
import datetime
import socket, sys
import paho.mqtt.client as mqtt
from config.conf_local import local_conf


def on_connect(mqttc, obj, rc):
    print("OnConnetc, rc: "+str(rc))

def on_publish(mqttc, obj, mid):
    print("OnPublish, mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mqttc, obj, level, string):
    print("Log:"+string)

def on_message(mqttc, obj, msg):
    curtime = datetime.datetime.now()
    strcurtime = curtime.strftime("%Y-%m-%d %H:%M:%S")
    print(strcurtime + ": " + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    on_exec(str(msg.payload))

def on_exec(strcmd):
    print ("Exec:",strcmd)


if __name__ == '__main__':
    mqttc = mqtt.Client("t_client1")
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.on_log = on_log

    # 设置账号密码(可选)
    mqttc.username_pw_set(local_conf.mqtt_broker['USERNAME'], password=local_conf.mqtt_broker['PASSWORD'])

    mqttc.connect(local_conf.mqtt_broker['HOST'], local_conf.mqtt_broker['PORT'], 60)
    mqttc.subscribe(topic, 0)
    mqttc.loop_forever()