#!/usr/bin/env python

import socket
from twisted.names import dns, client
from twisted.internet import reactor, defer

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
        challenge = challenge.payload.data[0].lstrip('challenge: ')
        response = eval(challenge)
        query_a = dns.Query(name = name, type = dns.A, cls = dns.IN)
        query_res = dns.Query(name = 'response: %d' % response, type = dns.TXT, cls = dns.IN)
        res = yield self._lookup_queries([query_a, query_res], timeout)
        defer.returnValue(res)

resolver = SlothNSResolver(servers=[('127.0.0.1', 5454)])

r = resolver.lookupAddress('google.com')
def print_ip(result):
    print socket.inet_ntop(socket.AF_INET, result[0][0].payload.address)
    reactor.stop()

r.addCallback(print_ip)

reactor.run()
