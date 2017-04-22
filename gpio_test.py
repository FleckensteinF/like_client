#!/usr/bin/env python

import RPi.GPIO as gpio
import time
import os
import sys
import select

button_pin=17
set_button_pin=27
gpio.setmode(gpio.BCM)
gpio.setup(set_button_pin, gpio.OUT)
gpio.setup(button_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)

gpio.output(set_button_pin, gpio.LOW)

def want_like():
	if select.select([sys.stdin,], [], [], 0.0)[0]:
		ch = os.read(sys.stdin.fileno(), 1)
		if not ch:
			return False
		return ch == '1'
	else:
		return False

while True:
	if (gpio.input(button_pin)):
		print "Like"
	else:
		print "OFF"
	if want_like():
		print "Liking"
		gpio.output(set_button_pin, gpio.HIGH)
		time.sleep(1.0)
		print "Stopping liking"
		gpio.output(set_button_pin, gpio.LOW)
	time.sleep(0.5)

