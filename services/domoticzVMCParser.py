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

DOMOTICZ_IN_TOPIC = "domoticz/in"
DOMOTICZ_OUT_TOPIC = "domoticz/out"
GATEWAY_SUB_TOPIC = "/gateway/1/data"
GATEWAY_PUB_TOPIC = "/gateway/1/cmd"
GATEWAY_PUB_TOPIC_FLOW = GATEWAY_PUB_TOPIC + "/flow"
GATEWAY_PUB_TOPIC_BYPASS = GATEWAY_PUB_TOPIC + "/bypass"
GATEWAY_PUB_TOPIC_STANDBY = GATEWAY_PUB_TOPIC + "/standby"

#associative array where sensor id and domoticz idx are defined
domoticz_dict_idx = {}
domoticz_dict_idx["T_INT"] = 33
domoticz_dict_idx["T_OUT"] = 34
domoticz_dict_idx["T_EXT"] = 36
domoticz_dict_idx["T_IMP"] = 35
domoticz_dict_idx["BYPASS_STATUS"] = 38
domoticz_dict_idx["ACTUAL_FLOW"] = 42
domoticz_dict_idx["MANUAL_BYPASS"] = 39
domoticz_dict_idx["FLOW_RATE"] = 40
domoticz_dict_idx["MODE_ACTIVATION"] = 41



def on_connect(client, userdata, flags, rc):
    client.subscribe(GATEWAY_SUB_TOPIC)
    client.subscribe(DOMOTICZ_OUT_TOPIC)

def on_message(client, userdata, msg):

# Data from VMC
    if msg.topic == GATEWAY_SUB_TOPIC:
        data = json.loads(msg.payload)
        if "T_INT" in data:
            out_payload = {"idx": domoticz_dict_idx["T_INT"]}
            out_payload["svalue"] = fix_temp(data["T_INT"])
            send(DOMOTICZ_IN_TOPIC,json.dumps(out_payload))
        if "T_OUT" in data:
            out_payload = {"idx": domoticz_dict_idx["T_OUT"]}
            out_payload["svalue"] = fix_temp(data["T_OUT"])
            send(DOMOTICZ_IN_TOPIC,json.dumps(out_payload))
        if "T_EXT" in data:
            out_payload = {"idx": domoticz_dict_idx["T_EXT"]}
            out_payload["svalue"] = fix_temp(data["T_EXT"])
            send(DOMOTICZ_IN_TOPIC,json.dumps(out_payload))
        if "T_IMP" in data:
            out_payload = {"idx": domoticz_dict_idx["T_IMP"]}
            out_payload["svalue"] = fix_temp(data["T_IMP"])
            send(DOMOTICZ_IN_TOPIC,json.dumps(out_payload))
        if "BYPASS_STATUS" in data:
            out_payload = {"idx": domoticz_dict_idx["BYPASS_STATUS"], "command": "switchlight"}
            out_payload["switchcmd"] = switchcmd_from_int_to_string(data["BYPASS_STATUS"])
            send(DOMOTICZ_IN_TOPIC,json.dumps(out_payload))
        if "ACTUAL_FLOW" in data:
            out_payload = {"idx": domoticz_dict_idx["ACTUAL_FLOW"]}
            out_payload["svalue"] = str(data["ACTUAL_FLOW"])
            send(DOMOTICZ_IN_TOPIC,json.dumps(out_payload))        

# commands to VMC
    if msg.topic == DOMOTICZ_OUT_TOPIC:
        in_data = json.loads(msg.payload)
        if(in_data["idx"] == domoticz_dict_idx["MANUAL_BYPASS"]):
            send(GATEWAY_PUB_TOPIC_BYPASS,in_data["nvalue"])

        if(in_data["idx"] == domoticz_dict_idx["MODE_ACTIVATION"]):
            send(GATEWAY_PUB_TOPIC_STANDBY,in_data["nvalue"])

        if(in_data["idx"] == domoticz_dict_idx["FLOW_RATE"]):
            send(GATEWAY_PUB_TOPIC_FLOW,in_data["nvalue"])

def switchcmd_from_int_to_string(data):
    return "Off" if data == 0 else "On"

def switchcmd_from_string_to_int(data):
    return 0 if data == "Off" else 1

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
