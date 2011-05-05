#!/usr/bin/env python

import sys
sys.path.append('./pow')

import socket
from twisted.names import dns, client
from twisted.internet import reactor, defer, threads
from twisted.internet.threads import blockingCallFromThread
import operator
from threading import Thread
from pow import *
import os
import time

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
    def lookupAddress(self, name, logger, t, id = None, pow_obj = None, timeout = None):
        logger.info("broke into lua id: %d pid %d time %f" % (id, os.getpid(), time.time() - t))
        query_aaaa = dns.Query(name = name, type = dns.AAAA)
        if id != None:
            logger.info("making a dns query from id: %d pid: %d" % (id, os.getpid()))
            query_id = dns.Query(name = 'id=%d' % id, type = dns.TXT)
            res = yield self._lookup_queries([query_aaaa, query_id], timeout)
        else:
            logger.info("making a dns query")
            res = yield self._lookup_queries([query_aaaa], timeout)
        challenge = res[2][0]
        logger.info("got the chal, making the request for id: %d" % id)
        req = pow_req(pow_obj = pow_obj, wire = challenge.payload.payload)
        logger.info("making the chal response for id: %d l = %d" % (id, req.l))
        res = yield threads.deferToThread(req.create_res)
        query_res = dns.Query(name = res.pack(), type = dns.NULL)
        if id != None:
            logger.info("sending the chal response id: %d" % id)
            res = yield self._lookup_queries([query_aaaa, query_id, query_res], timeout)
        else:
            res = yield self._lookup_queries([query_aaaa, query_res], timeout)
        logger.info("got the dns response: %d" % id)
        defer.returnValue(res)

#resolver = SlothNSResolver(servers=[('172.18.49.98', 5454)])
resolver = SlothNSResolver(servers=[('127.0.0.1', 5454)])

running = False

def foo():
    print "ranned"

def query(name, logger, id = None, pow_obj = None):
    global running
    if not running:
        running = True
        Thread(target=reactor.run, args=(False,)).start()
    logger.info("inside query: id: %d pid: %d" % (id, os.getpid()))
    t_now = time.time()
    return blockingCallFromThread(reactor, resolver.lookupAddress, name, logger, t_now, id = id, pow_obj = pow_obj)

def shutdown():
    reactor.stop()

