#!/usr/bin/python
import paho.mqtt.client as mqtt
import argparse
import signal
import struct
import json

parser = argparse.ArgumentParser(description='Subscribe to sensor queue and parse data to domoticz')
parser.add_argument('hostname', metavar='hostname', help='hostname of mqtt server', nargs='?', default="0.0.0.0")
parser.add_argument('port', metavar='port', help='port of mqtt server', nargs='?', default="1883")
args = parser.parse_args()

domoticz_in_topic = "domoticz/in"
sensors_topic = "/sensor/#"

#associative array where sensor id and domoticz idx are defined
sensor_dict_idx = {}
sensor_dict_idx["1"] = {"temp-hum": 32,"temp":3,"hum":13}


def on_connect(client, userdata, flags, rc):
    client.subscribe(sensors_topic)

def on_message(client, userdata, msg):
    topic = msg.topic.split('/')

    # if topic is not mapped in sensor_dict_idx, exit
    if topic[3] not in  sensor_dict_idx[topic[2]]:
        return

    if topic[3] == "temp":
        out_payload = {"idx": sensor_dict_idx[topic[2]]["temp"]}
        out_payload["svalue"] = msg.payload

    if topic[3] == "hum":
        out_payload = {"idx": sensor_dict_idx[topic[2]]["hum"]}
        out_payload["nvalue"] = int(float(msg.payload))
        out_payload["svalue"] = "%d" % (hum_stat(float(msg.payload)))

    #format temp;hum
    if topic[3] == "temp-hum":
        out_payload = {"idx": sensor_dict_idx[topic[2]]["temp-hum"]}
        data = msg.payload.split(';')
        out_payload["nvalue"] = 0
        out_payload["svalue"] = "%s;%s;%d" % (data[0], data[1], hum_stat(float(data[1])))

    send(json.dumps(out_payload))

def send(payload):
    client.publish(domoticz_in_topic, payload, 0, True)


def hum_stat(humidity):
    if humidity < 30:
        return 2
    elif humidity >= 30 and humidity <= 45:
        return 0
    elif humidity > 45 and humidity <= 70:
        return 1
    else:
        return 3


def signal_handler(sig, frame):
    if sig is not signal.SIGUSR1:
        print "Ending and cleaning up"
        client.disconnect()

signal.signal(signal.SIGUSR1, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(args.hostname, int(args.port), 60)
client.loop_forever()
