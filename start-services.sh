#!/bin/bash
echo "launching services..."
<<<<<<< HEAD
python ./services/domoticzSensorParser.py &
python ./services/domoticzVMCParser.py &
=======
python ./services/domoticzSensorParser.py localhost &
>>>>>>> 64d55e4c338b7daac61000cb924ebb49a9a5084d
