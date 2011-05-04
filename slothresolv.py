#!/usr/bin/env python

import sys
sys.path.append('./pow')

import socket
from twisted.names import dns, client
from twisted.internet import reactor, defer
from twisted.internet.threads import blockingCallFromThread
import operator
from threading import Thread
from pow import *

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
    def lookupAddress(self, name, id = None, pow_obj = None, timeout = None):
        query_aaaa = dns.Query(name = name, type = dns.AAAA)
        if id != None:
            query_id = dns.Query(name = 'id=%d' % id, type = dns.TXT)
            res = yield self._lookup_queries([query_aaaa, query_id], timeout)
        else:
            res = yield self._lookup_queries([query_aaaa], timeout)
        challenge = res[2][0]
        req = pow_req(pow_obj = pow_obj, wire = challenge.payload.payload)
        res = req.create_res()
        query_res = dns.Query(name = res.pack(), type = dns.NULL)
        if id != None:
            res = yield self._lookup_queries([query_aaaa, query_id, query_res], timeout)
        else:
            res = yield self._lookup_queries([query_aaaa, query_res], timeout)
        defer.returnValue(res)

#resolver = SlothNSResolver(servers=[('172.18.49.98', 5454)])
resolver = SlothNSResolver(servers=[('127.0.0.1', 5454)])

running = False

def query(name, id = None, pow_obj = None):
    global running
    if not running:
        running = True
        Thread(target=reactor.run, args=(False,)).start()
    return blockingCallFromThread(reactor, resolver.lookupAddress, name, id = id, pow_obj = pow_obj)

def shutdown():
    reactor.stop()

