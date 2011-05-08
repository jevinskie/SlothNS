#!/usr/bin/env python

import sys
sys.path.append('./pow')

import random
from twisted.internet import reactor, threads, defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall
import pow as p
import numpy
from scipy import stats
from math import isnan
import time
import logging
from construct import *
import os

logger = logging.getLogger('slothns')
hdlr = logging.FileHandler('slothns.log')
stdhdlr = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
stdhdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.addHandler(stdhdlr)
logger.setLevel(logging.INFO)
n_clients = int(sys.argv[1])

utilization = numpy.zeros(n_clients)
util_95 = 0.0


class SlothNSLite(DatagramProtocol):
    def __init__(self, n = 22, seed = 0):
        self.liveChallenges = {}
        logger.info("setting up the PoW object... ")
        self.pow = p.pow(n, seed)
        logger.info("done setting up PoW object!")


    def calculate_badness(self, idd):
        global utilization, util_95
        min_l = 15
        max_l = 32
        l_diff = max_l - min_l
    
        util = min(utilization[idd], util_95)
        if util_95 == 0.0:
            util_95 = 1.0
        percent_bad = util / util_95
        if isnan(percent_bad):
            percent_bad = 0.0
        l = int(round(percent_bad * l_diff + min_l))
        logger.info("id %d is asked for l= %d" % (idd, l))
        return l
        
    @defer.inlineCallbacks
    def datagramReceived(self, data, (host, port)):
        if data[0:8] == "SLOTHINT":
            init = p._pow_init_wire_lite.parse(data)
            logger.info("challenging id: %d" % init.id)
            req = yield threads.deferToThread(p.pow_req, self.pow, self.calculate_badness(init.id))
            self.liveChallenges[init.id] = req
            self.transport.write(req.pack_lite(init.id), (host, port))
        elif data[0:8] == "SLOTHRSL":
            res_foo = p._pow_res_wire_lite.parse(data)
            logger.info("checking response from id: %d" % res_foo.id)
            req = self.liveChallenges[res_foo.id]
            res = yield threads.deferToThread(p.pow_res, self.pow, req, wire_lite = data)
            c = Container()
            c.magic = None
            c.id = res_foo.id
            r = yield threads.deferToThread(req.verify_res, res)
            if r:
                logger.info("response from id: %d was valid, sending answer" % res_foo.id)
                c.ok = 1
            else:
                logger.info("response from id: %d was invalid, sending answer" % res_foo.id)
                c.ok = 0
            self.transport.write(p._pow_fin_wire_lite.build(c), (host, port))
            del self.liveChallenges[res_foo.id]
        


class BadnessWatcher(DatagramProtocol):
    def datagramReceived(self, data, (host, port)):
        global utilization, util_95
        try:
            n, idd, duration = map(int, data.split())
        except:
            return
        utilization[idd] += n
        util_95 = stats.scoreatpercentile(utilization, 95)
        logger.info("id: %d asked for %d and took %d" % (idd, n, duration))
        logger.info("util_95: %r" % util_95)
        return

def check_load():
    l = os.getloadavg()
    logger.info("load: %f %f %f" % (l[0], l[1], l[2]))


lite = reactor.listenUDP(5555, SlothNSLite())
badwatch = reactor.listenUDP(22000, BadnessWatcher())
LoopingCall(check_load).start(5)

reactor.run()

