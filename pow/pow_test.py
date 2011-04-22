#!/usr/bin/env python

from pow import *

print "creating pow"
p = pow(24, 0)
print "creating req"
req = p.create_req(20)
print "creating res"
res = req.create_res()
print "verifying res"
print req.verify_res(res)

