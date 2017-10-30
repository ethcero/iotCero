#!/usr/bin/python
import paho.mqtt.client as mqtt
import argparse
import signal
import struct

parser = argparse.ArgumentParser(description='Subscribe to sensor queue and parse data to mqtt')
parser.add_argument('hostname', metavar='hostname', help='hostname of mqtt server', nargs='?', default="0.0.0.0")
parser.add_argument('port', metavar='port', help='port of mqtt server', nargs='?', default="1883")
args = parser.parse_args()

RF_IN_TOPIC = "rfbridge/rfin"
PREFIX_OUT_TOPIC = "RFdevice/"
SUFFIX_OUT_TOPIC = "/rfin"

#associative array where sensor id and domoticz idx are defined
rf_device = {}
rf_device["chuango"] = {"sync_time":18000, "low_time":568, "high_time":1650, "pulse_tolerance":70, "out_topic":"chuango"} # chuango alarm


def on_connect(client, userdata, flags, rc):
    client.subscribe(RF_IN_TOPIC)

def on_message(client, userdata, msg):
# Data from RF bridge
    if msg.topic == RF_IN_TOPIC:
        decode(msg.payload)


def decode(rf_in_buffer):
    byte_data = bytearray.fromhex(rf_in_buffer)
    sync_time = byte_data[0] << 8 | byte_data[1]
    low_time = byte_data[2] << 8 | byte_data[3]
    high_time = byte_data[4] << 8 | byte_data[5]
    msg_data =  byte_data[6] << 16 | byte_data[7] << 8 | byte_data[8]

    #print "sync_time:%d low_time:%d high_time:%d msg_data:%s" % (sync_time,low_time,high_time,hex(msg_data))

    for k,device in rf_device.items():
        if  abs(low_time - device["low_time"]) <= device["pulse_tolerance"] \
                and abs(high_time - device["high_time"]) <= device["pulse_tolerance"]:
            #print "aceptado: %s" % hex(msg_data)
            send(PREFIX_OUT_TOPIC + device["out_topic"] + SUFFIX_OUT_TOPIC,hex(msg_data))            
            break

def send(topic, payload):
    client.publish(topic, payload, 0, False)


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
