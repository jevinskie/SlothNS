#!/usr/bin/env python

import sys
import resource
from pow import *
from multiprocessing import Pool
import time
#from ctypes import *
import os

n = int(sys.argv[1])
l = int(sys.argv[2])

print "make pow"
p = pow(n, 0)

print "make req"
req = p.create_req(l)

print "make wire"
wire = req.pack()

print "making shared p2"
p2 = pow(p.n, p.seed, share = p)
print "done shared p2"

def void(wire):
    global p2
    print "im in %d" % os.getpid()
    req = pow_req(pow_obj = p2, wire = wire)
    print "creating res"
    sys.stdout.flush()
    res = req.create_res()

    print "verifying res"
    sys.stdout.flush()
    print req.verify_res(res)
    sys.stdout.flush()

    return

pool = Pool(processes=100)
for i in range(100):
    pool.apply(void, (wire,))

print "memory usage:"
u = resource.getrusage(resource.RUSAGE_SELF)
mb = u.ru_maxrss / (1.0 * 2**10)
print "TOTAL: %d MB" % mb

if len(sys.argv) > 3:
    raw_input("paused... press enter to continue\n")
