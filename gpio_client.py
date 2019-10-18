#!/usr/bin/env python

import RPi.GPIO as gpio
import time
import os
import sys
import select
import datetime
import requests
import traceback

base_url="https://likeserver-164912.appspot.com/"
my_button="Christian"
liked_times=set()

button_pin=17
set_button_pin=27
connection_pin=24
script_running_pin=23

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
        gpio.setup(connection_pin, gpio.OUT)
        gpio.setup(script_running_pin, gpio.OUT)
        
        gpio.output(set_button_pin, gpio.LOW)
        gpio.output(connection_pin, gpio.LOW)
        gpio.output(script_running_pin, gpio.LOW)

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

def main_loop(f):
        count=0
        led_state=False
        while True:                
                if (gpio.input(button_pin)):
                        print "Like"
                        print >> f, "Like"
                        try:
                                r=really_post_like()
                                print "posted like with ", r.status_code
                                print >> f, "posted like with ", r.status_code
                                gpio.output(connection_pin, gpio.HIGH)
                        except Exception as e:
                                print "Failed to post like ", e
                                print >> f, "Failed to post like ", e
                else:
                        print "OFF"
                        print >> f, "OFF"
                if want_like():
                        print "Liking"
                        print >> f, "Liking"
                        gpio.output(set_button_pin, gpio.HIGH)
                        time.sleep(1.0)
                        print "Stopping liking"
                        print >> f, "Stopping liking"
                        gpio.output(set_button_pin, gpio.LOW)
                count=count+1
                if count >= 10:
                        count = 0
                        try:
                                r = get_likes()
                                print "got likes with ", r.status_code
                                print >> f, "got likes with ", r.status_code
                                print "text: ", r.text
                                print >> f, "text: ", r.text                                
                                like_times=parse_likes(r.text)
                                for lt in like_times:
                                        exec_like(lt)
                                gpio.output(connection_pin, gpio.HIGH)
                        except Exception as e:
                                print >> f, "inner"
                                print >> f, traceback.format_exc()
                                print "Failed to get likes ", e
                                print >> f, "Failed to get likes ", e
                led_state = not led_state
                gpio.output(script_running_pin, gpio.HIGH if led_state else gpio.LOW)
                time.sleep(0.5)
                gpio.output(connection_pin, gpio.LOW)
                f.flush()

if __name__ == "__main__":
        with open("/tmp/like_log", 'w') as f:
                setup_gpio()
                try:
                        main_loop(f)
                        f.flush()
                        os.fsync()
                except Exception as e:
                        print >> f, "outer"
                        print >> f, traceback.format_exc()
                        print >> f, "Exception: ",e
                        print "Exception: ",e
                        raise e
