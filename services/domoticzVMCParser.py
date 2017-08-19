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
domoticz_out_topic = "domoticz/out"
gateway_sub_topic = "/gateway/1/data"
gateway_pub_topic = "/gateway/1/cmd"

#associative array where sensor id and domoticz idx are defined
sensor_dict_idx = {}
sensor_dict_idx["T_INT"] = 33
sensor_dict_idx["T_OUT"] = 34
sensor_dict_idx["T_EXT"] = 36
sensor_dict_idx["T_IMP"] = 35
sensor_dict_idx["BYPASS_STATUS"] = 38
sensor_dict_idx["ACTUAL_FLOW"] = 37
sensor_dict_idx["MANUAL_BYPASS"] = 39
sensor_dict_idx["FLOW_RATE"] = 40



def on_connect(client, userdata, flags, rc):
    client.subscribe(gateway_sub_topic)
    client.subscribe(domoticz_out_topic)

def on_message(client, userdata, msg):

    if msg.topic == gateway_sub_topic:
        data = json.loads(msg.payload)
        if "T_INT" in data:
            out_payload = {"idx": sensor_dict_idx["T_INT"]}
            out_payload["svalue"] = fix_temp(data["T_INT"])
            send(domoticz_in_topic,json.dumps(out_payload))
        if "T_OUT" in data:
            out_payload = {"idx": sensor_dict_idx["T_OUT"]}
            out_payload["svalue"] = fix_temp(data["T_OUT"])
            send(domoticz_in_topic,json.dumps(out_payload))
        if "T_EXT" in data:
            out_payload = {"idx": sensor_dict_idx["T_EXT"]}
            out_payload["svalue"] = fix_temp(data["T_EXT"])
            send(domoticz_in_topic,json.dumps(out_payload))
        if "T_IMP" in data:
            out_payload = {"idx": sensor_dict_idx["T_IMP"]}
            out_payload["svalue"] = fix_temp(data["T_IMP"])
            send(domoticz_in_topic,json.dumps(out_payload))
        if "BYPASS_STATUS" in data:
            out_payload = {"idx": sensor_dict_idx["BYPASS_STATUS"]}
            out_payload["svalue"] = fix_temp(data["BYPASS_STATUS"])
            send(domoticz_in_topic,json.dumps(out_payload))
        if "ACTUAL_FLOW" in data:
            out_payload = {"idx": sensor_dict_idx["ACTUAL_FLOW"]}
            out_payload["svalue"] = fix_temp(data["ACTUAL_FLOW"])
            send(domoticz_in_topic,json.dumps(out_payload))
        if "MANUAL_BYPASS" in data:
            out_payload = {"idx": sensor_dict_idx["MANUAL_BYPASS"]}
            out_payload["svalue"] = fix_temp(data["MANUAL_BYPASS"])
            send(domoticz_in_topic,json.dumps(out_payload))

#    if msg.topic == domoticz_out_topic:


def fix_temp(temp):
    return str(float(temp)/10)

def send(topic, payload):
    client.publish(topic, payload, 0, True)


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
