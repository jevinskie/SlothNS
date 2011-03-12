#!/usr/bin/env python

import random
from twisted.internet import reactor, interfaces, defer
from twisted.names import dns, server
from twisted.python import log
import operator


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

        pow = 'challenge: %d * %d' % pow_params

        name = str(message.queries[0].name)

        txt = dns.Record_TXT(pow, ttl=0)

        challenge = self.makeRR(name, txt)

        message.additional.append(challenge)

        self.sendReply(protocol, message, address)
        return

    def checkResponse(self, message, protocol, address):
        query = filter(lambda q: q.type == dns.A, message.queries)[0]
        response = filter(lambda q: q.type == dns.TXT, message.queries)[0]
        response = response.name.name.lstrip('response: ')
        response = int(response)
        ip = address[0]
        correct_response = reduce(operator.mul, self.liveChallenges[ip])
        del self.liveChallenges[ip]
        if correct_response == response:
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

