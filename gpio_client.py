#!/usr/bin/env python

import RPi.GPIO as gpio
import time
import os
import sys
import select
import datetime
import requests

base_url="https://likeserver-164912.appspot.com/"
my_button="wera"
liked_times=set()

button_pin=17
set_button_pin=27

def really_post_like():
        r=requests.post(base_url+"like",data={'button_id':my_button,'client':'like_button'})
        return r

def get_likes():
        r=requests.get(base_url+"like",params={'button_id':my_button,'client':'like_button'})
        return r

def parse_likes(like_return):
        like_times=set()
        first = True
        for line in like_return.split('\n'):
                line=line.strip()
                if not line:
                        continue
                if first:
                        if line != 'likes:':
                                return set()
                        else:
                                first=False
                                continue
                like_time=datetime.datetime.strptime(line,"%Y-%m-%d_%H-%M-%S.%f")
                if like_time not in liked_times:
                        like_times.add(like_time)
        return like_times
        
def setup_gpio():
        gpio.setmode(gpio.BCM)
        gpio.setup(set_button_pin, gpio.OUT)
        gpio.setup(button_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)

        gpio.output(set_button_pin, gpio.LOW)

def exec_like(like_time):
        print "Liking"
        gpio.output(set_button_pin, gpio.HIGH)
        time.sleep(1.0)
        print "Stopping liking"
        gpio.output(set_button_pin, gpio.LOW)
        liked_times.add(like_time)

def want_like():
	if select.select([sys.stdin,], [], [], 0.0)[0]:
		ch = os.read(sys.stdin.fileno(), 1)
		if not ch:
			return False
		return ch == '1'
	else:
		return False

def main_loop():
        count=0
        while True:                
                if (gpio.input(button_pin)):
                        print "Like"
                        try:
                                r=really_post_like()
                                print "posted like with ", r.status_code
                        except Exception as e:
                                print "Failed to post like ", e

                else:
                        print "OFF"
                if want_like():
                        print "Liking"
                        gpio.output(set_button_pin, gpio.HIGH)
                        time.sleep(1.0)
                        print "Stopping liking"
                        gpio.output(set_button_pin, gpio.LOW)
                count=count+1
                if count >= 10:
                        count = 0
                        try:
                                r = get_likes()
                                print "got likes with ", r.status_code
                                print "text: ", r.text
                                like_times=parse_likes(r.text)
                                for lt in like_times:
                                        exec_like(lt)
                        except Exception as e:
                                print "Failed to get likes ", e
                time.sleep(0.5)

if __name__ == "__main__":
        setup_gpio()
        try:
                main_loop()
        except Exception as e:
                print "Exception: ",e
