#!/usr/bin/python
import paho.mqtt.client as mqtt
import argparse
import signal
import struct

parser = argparse.ArgumentParser(description='Subscribe to sensor queue and parse data to domoticz')
parser.add_argument('hostname', metavar='hostname', help='hostname of mqtt server', nargs='?', default="0.0.0.0")
parser.add_argument('port', metavar='port', help='port of mqtt server', nargs='?', default="1883")
args = parser.parse_args()

domoticz_in_topic = "/domoticz/in"
sensors_topic = "/sensor/#"

#associative array where sensor id and domoticz idx are defined
dictionary["1"] = 15;


def on_connect(client, userdata, flags, rc):
    client.subscribe(domoticz_in_topic)

def on_message(client, userdata, msg):
    topic = msg.topic.split('/')
    payload = msg.payload
    

    client.publish(args.trigger_out, sensor + ";" + payload + ";" + unit, 0, True)


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
