#!/usr/bin/env python

import RPi.GPIO as gpio
import time
import os
import sys
import select
import datetime
import requests
import traceback
import json

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

def get_likes(f):
        r=requests.get(base_url+"like",params={'button_id':my_button,'client':'like_button','json_encoding':'1'})
        print "got likes with ", r.status_code
        print >> f, "got likes with ", r.status_code
        print "text: ", r.text
        print >> f, "text: ", r.text
        if not r.ok:
            return None
        json_encoded_r=json.loads(r.text)
        print "JSON'd Likes: ", json_encoded_r
        print >> f, "JSON'd Likes: ", json_encoded_r
        return json_encoded_r

def parse_likes(like_return):
        if not like_return:
                return set()
        like_times=set()
        for line in like_return:
                line=line.strip()
                if not line:
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
                                r = get_likes(f)
                                if r is not None:
                                    like_times=parse_likes(r['likes'])
                                    for lt in like_times:
                                            exec_like(lt)
                                    users_online = r['like_queries']
                                    gpio.output(connection_pin, gpio.HIGH)
                                    time.sleep(0.5)
                                    gpio.output(connection_pin, gpio.LOW)
                                    time.sleep(0.5)
                                    for i in range(users_online):
                                            gpio.output(connection_pin, gpio.HIGH)
                                            time.sleep(0.2)
                                            gpio.output(connection_pin, gpio.LOW)
                                            time.sleep(0.2)
                        except Exception as e:
                                print >> f, "inner"
                                print >> f, traceback.format_exc()
                                print traceback.format_exc()
                                try:
                                    print "Failed to get likes ", e
                                    print >> f, "Failed to get likes ", e
                                except TypeError as et:
                                    print "Unprintable Exception"
                                    print >> f, "Unprintable Exception"
                led_state = not led_state
                gpio.output(script_running_pin, gpio.HIGH if led_state else gpio.LOW)
                time.sleep(0.5)
                gpio.output(connection_pin, gpio.LOW)
                f.flush()

if __name__ == "__main__":
        current_time = datetime.datetime.now()
        filename = "/home/pi/like_logs/"+current_time.strftime("%Y-%m-%d_%H-%M-%S")+".log"
        with open(filename, 'w') as f:
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
