#!/usr/bin/env python

import sys
import resource
from pow import *
import time

n = int(sys.argv[1])
l = int(sys.argv[2])

print "creating pow"
sys.stdout.flush()
start = time.time()
p = pow(n, 9)
end = time.time()

print "pow took %f" % (end-start)

print "creating req"
sys.stdout.flush()
req = p.create_req(l)

print "creating res"
sys.stdout.flush()
start = time.time()
res = req.create_res()
end = time.time()
print "res took %f" % (end-start)

print "verifying res"
sys.stdout.flush()
print req.verify_res(res)
sys.stdout.flush()

print "memory usage:"
u = resource.getrusage(resource.RUSAGE_SELF)
mb = u.ru_maxrss / (1.0 * 2**10)
print "TOTAL: %d MB" % mb

if len(sys.argv) > 3:
    raw_input("paused... press enter to continue\n")
