#!/usr/bin/env python

import sys
sys.path.append('./pow')

import random
from twisted.internet import reactor, interfaces, defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.base import DelayedCall
from twisted.names import dns, server
from twisted.python import log
import operator
import subprocess
from pow import *
import numpy
from scipy import stats
from math import isnan
import time
import logging

logger = logging.getLogger('slothns')
hdlr = logging.FileHandler('slothns.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
n_clients = int(sys.argv[2])

utilization = numpy.zeros(n_clients)
util_95 = 0.0

class SlothNSServerFactory(server.DNSServerFactory):
    def __init__(self, baseip = None, n = 22, seed = 0, l = 26, verbose = 0):
        server.DNSServerFactory.__init__(self, verbose = verbose)
        self.liveChallenges = {}
        logger.info("setting up the PoW object... ")
        self.pow = pow(n, seed)
        logger.info("done setting up PoW object!")
        self.l = l
        self.baseip = baseip
        return

    def makeRR(self, name, resource):
        rr = dns.RRHeader(name = name, type = resource.TYPE, ttl = resource.ttl, payload = resource)
        return rr

    def calculate_badness(self, id):
        global utilization, util_95
        min_l = 15
        max_l = 29
        l_diff = max_l - min_l
    
        util = min(utilization[id], util_95)
        if util_95 == 0.0:
            util_95 = 1.0
        percent_bad = util / util_95
        if isnan(percent_bad):
            percent_bad = 0.0
        l = int(round(percent_bad * l_diff + min_l))
        logger.info("id %d is asked for l= %d" % (id, l))
        return l

    def issueChallenge(self, message, protocol, address, id):
        req = pow_req(self.pow, self.calculate_badness(id))
        self.liveChallenges[id] = req

        name = next((q.name.name for q in message.queries if q.type == dns.AAAA), None)

        null_req = dns.Record_NULL(req.pack(), ttl=0)

        challenge = self.makeRR(name, null_req)

        message.additional.append(challenge)

        self.sendReply(protocol, message, address)
        return

    def gen_rand_ipv6(self):
        rand_part = ':'.join([hex(random.randrange(0,2**16))[2:] for i in range(4)])
        whole = self.baseip + ':' + rand_part
        #subprocess.check_call(['ip', 'addr', 'add', whole, 'dev', 'he-ipv6'])
        return whole

    def checkResponse(self, message, protocol, address, id):
        query = next((q for q in message.queries if q.type == dns.AAAA), None)
        response = next((q for q in message.queries if q.type == dns.NULL), None)
        if response == None:
            del self.liveChallenges[id]
            return
        req = self.liveChallenges[id]
        res = pow_res(self.pow, req, wire = response.name.name)
        if req.verify_res(res):
            aaaa = dns.Record_AAAA(address = self.gen_rand_ipv6(), ttl = 0)
            message.answers.append(self.makeRR(query.name.name, aaaa))
            self.sendReply(protocol, message, address)
        else:
            message.rCode = dns.EREFUSED
            protocol.writeMessage(message, address)
        del self.liveChallenges[id]
        return


    def handleQuery(self, message, protocol, address):
        id = next((q for q in message.queries if q.type == dns.TXT), None)
        if id == None:
            id = address[0]
        else:
            id = int(id.name.name.split('=')[1])
        if id not in self.liveChallenges:
            logger.info("challenging id: %d" % id)
            self.issueChallenge(message, protocol, address, id)
        else:
            logger.info("checking response of id: %d" % id)
            self.checkResponse(message, protocol, address, id)
        return

class BadnessWatcher(DatagramProtocol):
    def datagramReceived(self, data, (host, port)):
        global utilization, util_95
        try:
            n, id, duration = map(int, data.split())
        except:
            return
        utilization[id] += duration
        util_95 = stats.scoreatpercentile(utilization, 95)
        logger.info("id: %d asked for %d and took %d" % (id, n, duration))
        logger.info("utilization: %r" % utilization)
        logger.info("util_95: %r" % util_95)
        return


factory = SlothNSServerFactory(baseip = sys.argv[1], verbose = 10)
ltcp = reactor.listenTCP(5454, factory)

f2 = dns.DNSDatagramProtocol(factory)
udp = reactor.listenUDP(5454, f2)

badwatch = reactor.listenUDP(22000, BadnessWatcher())

#reactor.callLater(60*3, reactor.stop)

reactor.run()

