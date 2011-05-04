#!/usr/bin/env python

import sys
import time
import urllib2
import random
from threading import Timer, Thread
from Queue import PriorityQueue, Empty
import os
from slothresolv import query
from multiprocessing import Pool, Manager

url = 'http://172.18.48.222:8080/fib.php?n='

class fetcher(Thread):
    def __init__(self, res_q, wait_q_q, work_q):
        Thread.__init__(self)
        self.res_q = res_q
        self.wait_q_q = wait_q_q
        self.work_q = work_q

def fetch(attacker, id, res_q, wait_q_q):
    if attacker:
        n = 100
    elif random.uniform(0, 1) > 0.9:
        n = 29
    else:
        n = 9
    if attacker:
        delay = 0
    else:
        delay = random.expovariate(1.0/45)
    print "starting fetch"
    start = time.time()
    print "starting query"
    query('google.com', id = id)
    print "query is done"
    try:
        print "starting url open"
        urllib2.urlopen(url + str(n) + "&id=%d" % id)
        print "url open done"
        error = 0
    except urllib2.URLError:
        print "url open failed"
        error = 1
    end = time.time()
    res_q.put((n, end - start, error))
    print "putting in wait_q_q"
    wait_q_q.put((time.time() + delay, attacker, id))

def main(argv=None):
    if argv is None:
        argv = sys.argv

    id_base = int(sys.argv[1])

    manager = Manager()

    wait_q = PriorityQueue()
    wait_q_q = manager.Queue()
    res_q = manager.Queue()

    out_file = open('latency.csv', 'a')

    print "PID: %d" % os.getpid()
    print "Running the gauntlet:"
    id = id_base
    num_clients = 0
    for i in range(10):
        wait_q.put((time.time(), False, id))
        id += 1
        num_clients += 1
    for i in range(20):
        wait_q.put((time.time(), True, id))
        id += 1
        num_clients += 1

    pool = Pool(processes=num_clients)

    while True:
        t, attacker, id = wait_q.get()
        print "got a wait_q"
        delta = t - time.time()
        delay = max(delta, 0)
        if delay > 0:
            print "delaying"
            Timer(delay, pool.apply_async, (fetch, (attacker, id, res_q, wait_q_q))).start()
        else:
            print "no delay"
            pool.apply_async(fetch, (attacker, id, res_q, wait_q_q))
        wait_q.task_done()

        print "empty wait_q_q"
        while not wait_q_q.empty():
            print "got a wait_q_q"
            wait_q.put(wait_q_q.get())

        # we have to make sure there is at least one element in wait_q before the end of the loop
        if wait_q.empty():
            print "wait_q is empty"
            r = wait_q_q.get()
            print "got a wait_q_q"
            wait_q.put(r)

        print "empty res_q"
        while not res_q.empty():
            res = res_q.get()
            print "got a res_q"
            out_file.write("%d, %f, %d\n" % (res[0], res[1], res[2]))
            out_file.flush()
        print "done with empty queue"

    print "done with infinite loop"
    while not res_q.empty():
        res = res_q.get()
        out_file.write("%d, %f, %d\n" % (res[0], res[1], res[2]))

    return 0

if __name__ == "__main__":
    sys.exit(main())


