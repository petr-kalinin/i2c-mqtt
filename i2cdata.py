#!/usr/bin/python3
import traceback
from pcf8574 import PCF8574
import datetime
import paho.mqtt.client as mqtt
import logging

logging.basicConfig(format='%(asctime)s:%(filename)s:%(lineno)d: %(message)s', level=logging.DEBUG)

i2c_port_num = 1
pcfs = {
    '20': PCF8574(i2c_port_num, 0x20),
    '24': PCF8574(i2c_port_num, 0x24)
}

current_state = {}
last_time = {}

def on_message(client, userdata, msg):
    topic = msg.topic
    value = msg.payload.decode()
    logging.info("Recv: %s %s " % (msg.topic, value))
    current_state[msg.topic] = value

def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code "+str(rc))
    client.subscribe("#")

client = mqtt.Client()
client.on_message = on_message
client.on_connect = on_connect
client.connect("localhost", 1883, 60)

while True:
    try:
        now = datetime.datetime.now()
        for key in pcfs:
            state = pcfs[key].port
            for i in range(len(state)):
                topic = "track/sensor/" + key + "/" + str(i)
                value = "INACTIVE" if state[i] else "ACTIVE"
                if current_state.get(topic) != value or last_time.get(topic) < now - datetime.timedelta(minutes = 1):
                    logging.info("%s -> %s" % (topic, value))
                    client.publish(topic, value)
                    last_time[topic] = now
        now = datetime.datetime.now()
        while datetime.datetime.now() - now < datetime.timedelta(seconds=0.3):
            client.loop(timeout=0.3)
    except Exception as e:
        pass
        logging.error("Error!")
        logging.error(e)
        logging.error(traceback.format_exc())