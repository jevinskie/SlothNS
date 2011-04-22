#!/usr/bin/env python

import sys
from pow import *

print "creating pow"
sys.stdout.flush()
p = pow(24, 0)

print "creating req"
sys.stdout.flush()
req = p.create_req(20)

print "creating res"
sys.stdout.flush()
res = req.create_res()

print "verifying res"
sys.stdout.flush()
print req.verify_res(res)
sys.stdout.flush()

