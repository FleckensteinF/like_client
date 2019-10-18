#! /usr/bin/env python

import datetime
import requests
import sys

#base_url = "https://likeserver-164912.appspot.com/"
base_url = "http://localhost:8080/"
liked_times = set()

def really_post_like(button_id):
    r = requests.post(base_url+"like", data = {'button_id':button_id, 'client':'like_button'})
    return r

def get_likes(button_id):
    r = requests.get(base_url+"like", params = {'button_id':button_id, 'client':'like_button'})
    return r

def parse_likes(like_return):
    like_times = set()
    first = True
    for line in like_return.split("\n"):
        line = line.strip()
        if not line:
            continue
        if first:
            if line != "likes:":
                #print "invalid blub"
                return set()
            else:
                first = False
                continue
        like_time = datetime.datetime.strptime(line, "%Y-%m-%d_%H-%M-%S.%f")
        if like_time not in liked_times:
            like_times.add(like_time)
    return like_times

def exec_like(like_time):
    print "like"
    liked_times.add(like_time)

if __name__ == "__main__":
    assert 2 <= len(sys.argv) <= 3
    button_id = sys.argv[1]
    post_like = None
    if len(sys.argv) > 2:
        post_like = sys.argv[2]
        assert post_like == "1"
    r = None
    if post_like:
        r = really_post_like(button_id)
    else: 
        r = get_likes(button_id)
        like_times = parse_likes(r.text)
        for lt in like_times:
            exec_like(lt)

    print r.status_code
    print r.text
