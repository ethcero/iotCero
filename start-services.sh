#!/bin/bash
echo "launching services..."
python /root/projects/iotCero/services/domoticzSensorParser.py localhost &
python /root/projects/iotCero/services/domoticzVMCParser.py localhost &
python /root/projects/iotCero/services/RFBridgeDecoder.py localhost &
