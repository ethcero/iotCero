#!/bin/bash
echo "launching services..."
python ./services/domoticzSensorParser.py &
python ./services/domoticzVMCParser.py &
