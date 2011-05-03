#!/usr/bin/env python

import sys
sys.path.append('./pow')

import random
from twisted.internet import reactor, interfaces, defer
from twisted.names import dns, server
from twisted.python import log
import operator
from pow import *

class SlothNSServerFactory(server.DNSServerFactory):
    def __init__(self, n = 25, seed = 0, l = 21, verbose = 0):
        server.DNSServerFactory.__init__(self, verbose = verbose)
        self.liveChallenges = {}
        if verbose:
            print "setting up the PoW object... ",
            sys.stdout.flush()
        self.pow = pow(n, seed)
        if verbose:
            print "done!"
        self.l = l
        return

    def makeRR(self, name, resource):
        rr = dns.RRHeader(name = name, type = resource.TYPE, ttl = resource.ttl, payload = resource)
        return rr

    def issueChallenge(self, message, protocol, address):
        ip = address[0]

        req = pow_req(self.pow, self.l)
        self.liveChallenges[ip] = req

        name = str(message.queries[0].name)

        null_req = dns.Record_NULL(req.pack(), ttl=0)

        challenge = self.makeRR(name, null_req)

        message.additional.append(challenge)

        self.sendReply(protocol, message, address)
        return

    def checkResponse(self, message, protocol, address):
        query = filter(lambda q: q.type == dns.A, message.queries)[0]
        response = filter(lambda q: q.type == dns.NULL, message.queries)[0]
        ip = address[0]
        req = self.liveChallenges[ip]
        res = pow_res(self.pow, req, wire = response.name.name)
        if req.verify_res(res):
            rand_addr = '.'.join([str(random.randrange(1,255)) for i in range(4)])
            a = dns.Record_A(address = rand_addr, ttl = 0)
            message.answers.append(self.makeRR(query.name.name, a))
            self.sendReply(protocol, message, address)
        else:
            message.rCode = dns.EREFUSED
            protocol.writeMessage(message, address)
        del self.liveChallenges[ip]
        return


    def handleQuery(self, message, protocol, address):
        ip = address[0]
        if ip not in self.liveChallenges:
            self.issueChallenge(message, protocol, address)
        else:
            self.checkResponse(message, protocol, address)
        return

factory = SlothNSServerFactory(verbose = 10)
ltcp = reactor.listenTCP(5454, factory)

f2 = dns.DNSDatagramProtocol(factory)
udp = reactor.listenUDP(5454, f2)

reactor.run()

