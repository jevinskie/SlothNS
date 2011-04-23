#!/usr/bin/env python

import random
from twisted.internet import reactor, interfaces, defer
from twisted.names import dns, server
from twisted.python import log
import operator

from ctypes import *

class pow_wire_req(BigEndianStructure):
    _fields_ = [("magic", c_uint32),
                ("a", c_uint32),
                ("b", c_uint32),]
    _pack_ = 1
    def pack(self):
        return string_at(addressof(self), sizeof(self))
    def unpack(self, packed):
        memmove(addressof(self), packed, min(sizeof(self), len(packed)))

class pow_wire_res(BigEndianStructure):
    _fields_ = [("magic", c_uint32),
                ("r", c_uint32),]
    _pack_ = 1
    def pack(self):
        return string_at(addressof(self), sizeof(self))
    def unpack(self, packed):
        memmove(addressof(self), packed, min(sizeof(self), len(packed)))


class SlothNSServerFactory(server.DNSServerFactory):
    def __init__(self, verbose = 0):
        server.DNSServerFactory.__init__(self, verbose = verbose)
        self.liveChallenges = {}
        return

    def makeRR(self, name, resource):
        rr = dns.RRHeader(name = name, type = resource.TYPE, ttl = resource.ttl, payload = resource)
        return rr

    def issueChallenge(self, message, protocol, address):
        pow_params = tuple([random.randrange(1,10) for i in range(2)])

        ip = address[0]

        self.liveChallenges[ip] = pow_params

        req = pow_wire_req()
        req.magic = 0xFEEDFACE
        req.a = pow_params[0]
        req.b = pow_params[1]

        name = str(message.queries[0].name)

        null = dns.Record_NULL(req.pack(), ttl=0)

        challenge = self.makeRR(name, null)

        message.additional.append(challenge)

        self.sendReply(protocol, message, address)
        return

    def checkResponse(self, message, protocol, address):
        query = filter(lambda q: q.type == dns.A, message.queries)[0]
        response = filter(lambda q: q.type == dns.NULL, message.queries)[0]
        res = pow_wire_res()
        res.unpack(response)
        ip = address[0]
        correct_response = reduce(operator.mul, self.liveChallenges[ip])
        del self.liveChallenges[ip]
        if correct_response == res.r:
            rand_addr = '.'.join([str(random.randrange(1,255)) for i in range(4)])
            a = dns.Record_A(address = rand_addr, ttl = 0)
            message.answers.append(self.makeRR(query.name.name, a))
            self.sendReply(protocol, message, address)
        else:
            message.rCode = dns.EREFUSED
            protocol.writeMessage(message, address)

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

