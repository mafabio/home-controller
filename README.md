# Home controller
Simple REST webservice to control Home Automation system.

At the moment the system managed is the BTicino/Legrand MyHome system,
via one of the available IP gateways (F453AV or F454).

## Managed MyHome subsystems
Currently managed commands:
- lights (On/Off)
- temperature read
- active power consumption read

## REST interface
The available rest routes are:
- ```/light/<light_id>/command``` (where command can be *on* or *off*) to switch the actuator on or off
- ```/thermo/<zone>/temp``` in order to read the temperature
- ```/energy/<counter_id>/power``` in order to get active power