#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from openwebnet import DomoticController
import json

homeController = DomoticController('192.168.1.35')

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to Home Controller!"

@app.route("/light/<int:light_id>/<state>")
def switch(light_id, state):
    """ Switches lights on or off

    PUT /light/74/on
    PUT /light/74/off
    """

    binary_state = 1 if state == 'on' else 0
    homeController.setLight(light_id, binary_state)

    return json.dumps({'id': light_id, 'state': state})

@app.route("/thermo/<int:zone>/temp")
def getTemp(zone):
    temp = homeController.getThermoZoneTemp(zone)

    return json.dumps({'zone': zone, 'temperature': temp})

@app.route("/energy/<int:counter>/power")
def getPower(counter):
    power = homeController.getActivePower(counter)

    return json.dumps({'counter': counter, 'power': power})

if __name__ == "__main__":
    app.run(host='0.0.0.0')
