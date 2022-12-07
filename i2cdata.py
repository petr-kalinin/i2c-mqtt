#!/usr/bin/python3
from pcf8574 import PCF8574
import datetime
import paho.mqtt.client as mqtt

i2c_port_num = 1
pcf_address = 0x24
pcf = PCF8574(i2c_port_num, pcf_address)

current_state = {}

def on_message(client, userdata, msg):
    topic = msg.topic
    value = msg.payload.decode()
    print("Recv: ", msg.topic, value)
    current_state[msg.topic] = value

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("/trains/#")

client = mqtt.Client()
client.on_message = on_message
client.on_connect = on_connect
client.connect("localhost", 1883, 60)

while True:
    state = pcf.port
    new_state = []
    for i in range(len(state)):
        topic = "/trains/track/sensor/" + str(i)
        value = "INACTIVE" if state[i] else "ACTIVE"
        if current_state.get(topic) != value:
            print(topic, "->", value)
            client.publish(topic, value)
    now = datetime.datetime.now()
    while datetime.datetime.now() - now < datetime.timedelta(seconds=1):
        client.loop(timeout=1.0)