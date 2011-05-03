#!/usr/bin/env python

import sys
import resource
from pow import *

n = int(sys.argv[1])
l = int(sys.argv[2])

print "creating pow"
sys.stdout.flush()
p = pow(n, 0)

print "creating req"
sys.stdout.flush()
req = p.create_req(l)

print "creating res"
sys.stdout.flush()
res = req.create_res()

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
