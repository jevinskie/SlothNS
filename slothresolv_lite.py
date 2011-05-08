#!/usr/bin/env python

import sys
sys.path.append('./pow')

import socket
import pow as p
import os
from construct import *

ip = '172.18.49.16'

def query(logger, idd, pow_obj = None):
    logger.info("inside query: id: %d pid: %d" % (idd, os.getpid()))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    c = Container()
    c.magic = None
    c.id = idd
    sock.sendto(p._pow_init_wire_lite.build(c), (ip, 5555))
    req_wire = sock.recv(512)
    logger.info("got the chal, making the request for id: %d" % idd)
    req = p.pow_req(pow_obj = pow_obj, wire_lite = req_wire)
    assert idd == req.id
    logger.info("making the chal response for id: %d l = %d" % (idd, req.l))    
    res = req.create_res()
    logger.info("sending the chal response id: %d" % idd)
    sock.sendto(res.pack_lite(idd), (ip, 5555))
    logger.info("waiting for the response response for id: %d" % idd)
    fin_wire = sock.recv(128)
    fin = p._pow_fin_wire_lite.parse(fin_wire)
    assert idd == fin.id
    if fin.ok:
        logger.info("fin for id: %d is good" % idd)
        return True
    else:
        logger.info("sending the chal response id: %d" % idd)
        return False

