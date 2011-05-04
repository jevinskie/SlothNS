#!/usr/bin/env python

import sys
import time
import urllib2
import random
from threading import Timer, Thread
from Queue import Queue, PriorityQueue
import os

url = 'http://172.18.49.98:8080/fib.php?n='

class fetcher(Thread):
    def __init__(self, res_q, wait_q, work_q):
        Thread.__init__(self)
        self.res_q = res_q
        self.wait_q = wait_q
        self.work_q = work_q

    def run(self):
        attacker, id = self.work_q.get()
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
        start = time.time()
        try:
            urllib2.urlopen(url + str(n) + "&id=%d" % id)
            error = 0
        except urllib2.URLError:
            error = 1
        end = time.time()
        self.res_q.put((n, end - start, error))
        self.wait_q.put((time.time() + delay, attacker, id))
        self.work_q.task_done()

def do_fetch(attacker, id, res_q, wait_q, work_q):
    work_q.put((attacker, id))
    f = fetcher(res_q, wait_q, work_q)
    f.start()

def main(argv=None):
    if argv is None:
        argv = sys.argv

    id_base = int(sys.argv[1])

    wait_q = PriorityQueue()
    work_q = Queue()
    res_q = Queue()

    out_file = open('latency.csv', 'a')

    print "PID: %d" % os.getpid()
    print "Running the gauntlet:"
    id = id_base
    for i in range(256):
        wait_q.put((time.time(), False, id))
        id += 1
    for i in range(1023-256-6+20):
        wait_q.put((time.time(), True, id))
        id += 1

    while True:
        t, attacker, id = wait_q.get()
        delta = t - time.time()
        delay = max(delta, 0)
        if delay > 0:
            Timer(delay, do_fetch, (attacker, id, res_q, wait_q, work_q)).start()
        else:
            do_fetch(attacker, id, res_q, wait_q, work_q)
        wait_q.task_done()

        while not res_q.empty():
            res = res_q.get()
            out_file.write("%d, %f, %d\n" % (res[0], res[1], res[2]))
            out_file.flush()
            res_q.task_done()

    work_q.join()

    while not res_q.empty():
        res = res_q.get()
        out_file.write("%d, %f, %d\n" % (res[0], res[1], res[2]))
        res_q.task_done()

    return 0

if __name__ == "__main__":
    sys.exit(main())


