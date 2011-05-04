#!/usr/bin/env python

import sys
sys.path.append('./pow')

import socket
from twisted.names import dns, client
from twisted.internet import reactor, defer
import operator
from pow import *

result = None

class SlothNSResolver(client.Resolver):

    def _lookup_queries(self, queries, timeout):
        key = tuple(queries)
        waiting = self._waiting.get(key)
        if waiting is None:
            self._waiting[key] = []
            d = self.queryUDP(queries, timeout)
            def cbResult(result):
                for d in self._waiting.pop(key):
                    d.callback(result)
                return result
            d.addCallback(self.filterAnswers)
            d.addBoth(cbResult)
        else:
            d = defer.Deferred()
            waiting.append(d)
        return d

    @defer.inlineCallbacks
    def lookupAddress(self, name, timeout = None):
        global result
        res = yield client.Resolver.lookupIPV6Address(self, name, timeout)
        challenge = res[2][0]
        req = pow_req(wire = challenge.payload.payload)
        res = req.create_res()
        query_aaaa = dns.Query(name = name, type = dns.AAAA)
        query_res = dns.Query(name = res.pack(), type = dns.NULL)
        res = yield self._lookup_queries([query_aaaa, query_res], timeout)
        result = res
        reactor.stop()

resolver = SlothNSResolver(servers=[('127.0.0.1', 5454)])

def query():
    global result
    reactor.callWhenRunning(resolver.lookupAddress, 'google.com')
    reactor.run()
    return result

