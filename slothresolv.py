#!/usr/bin/env python

import socket
from twisted.names import dns, client
from twisted.internet import reactor, defer
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
        res = yield client.Resolver.lookupAddress(self, name, timeout)
        challenge = res[2][0]
        req = pow_wire_req()
        req.unpack(challenge.payload.payload)
        resp = pow_wire_res()
        resp.magic = 0xFACEFEED
        resp.r = req.a * req.b
        query_a = dns.Query(name = name)
        query_res = dns.Query(name = resp.pack(), type = dns.NULL)
        res = yield self._lookup_queries([query_a, query_res], timeout)
        defer.returnValue(res)

resolver = SlothNSResolver(servers=[('127.0.0.1', 5454)])

r = resolver.lookupAddress('google.com')
def print_ip(result):
    print socket.inet_ntop(socket.AF_INET, result[0][0].payload.address)
    reactor.stop()

r.addCallback(print_ip)

reactor.run()
