#!/usr/bin/env python

import os
import re
import socket
import sys
import time

parts = [
    r'(?P<time>\d+)',                   # time %t
    r'(?P<duration>\d+)',               # request duration %d
    r'"(?P<request>.+)"',               # request "%r"
    r'"(?P<agent>.*)"',                 # user agent "%{User-agent}i"
    r'(?P<status>[0-9]+)',              # status %>s
    r'(?P<size>\S+)',                   # size %b (careful, can be '-')
]

pattern = re.compile(r'\s+'.join(parts)+r'\s*\Z')

req = re.compile(r'GET.*fib\.php\?n=(?P<n>\d+)&id=(?P<id>\d+) HTTP/1\.1')

f = open(sys.argv[1], 'r')
f.seek(0,  os.SEEK_END)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = '127.0.0.1'
port = int(sys.argv[2])

while True:
    line = f.readline()
    if not line:
        time.sleep(0.1)
    m = pattern.match(line)
    if m == None:
        continue
    res = m.groupdict()
    if not re.match(r'Python-urllib', res['agent']):
        continue
    m = req.match(res['request'])
    if m == None:
        continue
    req_param = m.groupdict()
    n = req_param['n']
    id = req_param['id']
    print "n = %s id = %s duration = %s" % (n, id, res['duration'])
    sys.stdout.flush()
    s.sendto("%s %s %s" % (n, id, res['duration']), (ip, port))

