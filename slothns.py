#!/usr/bin/env python

import sys
sys.path.append('./pow')

import random
from twisted.internet import reactor, interfaces, defer
from twisted.names import dns, server
from twisted.python import log
import operator
import subprocess
from pow import *

class SlothNSServerFactory(server.DNSServerFactory):
    def __init__(self, baseip = None, n = 20, seed = 0, l = 10, verbose = 0):
        server.DNSServerFactory.__init__(self, verbose = verbose)
        self.liveChallenges = {}
        if verbose:
            print "setting up the PoW object... ",
            sys.stdout.flush()
        self.pow = pow(n, seed)
        if verbose:
            print "done!"
        self.l = l
        self.baseip = baseip
        return

    def makeRR(self, name, resource):
        rr = dns.RRHeader(name = name, type = resource.TYPE, ttl = resource.ttl, payload = resource)
        return rr

    def issueChallenge(self, message, protocol, address, id):
        req = pow_req(self.pow, self.l)
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
        if id not in self.liveChallenges:
            self.issueChallenge(message, protocol, address, id)
        else:
            self.checkResponse(message, protocol, address, id)
        return

factory = SlothNSServerFactory(baseip = sys.argv[1], verbose = 10)
ltcp = reactor.listenTCP(5454, factory)

f2 = dns.DNSDatagramProtocol(factory)
udp = reactor.listenUDP(5454, f2)

reactor.run()

