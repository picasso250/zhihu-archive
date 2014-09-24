#coding: utf-8

import time

data = {}

def timer(tag = 'default'):
    if tag not in data:
        data[tag] = time.time()
        return 0
    else:
        t = time.time()
        d = t - data[tag]
        data[tag] = t
        return int(d*1000)
