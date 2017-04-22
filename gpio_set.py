#!/usr/bin/env python

import RPi.GPIO as gpio
import time
import os
import sys

button_pin=27
gpio.setmode(gpio.BCM)
gpio.setup(button_pin, gpio.OUT)

if sys.argv[1] == "1":
	print "Liking"
	gpio.output(button_pin, gpio.HIGH);
elif sys.argv[1] == "0":
	print "Stopping liking"
	gpio.output(button_pin, gpio.LOW);

