#!/usr/bin/env python

import sys
import time
import urllib2
import random
from threading import Timer, Thread
from Queue import Queue, PriorityQueue

url = 'http://rossmann-a354.rcac.purdue.edu:8080/fib.php?n='

class fetcher(Thread):
    def __init__(self, res_q, wait_q, work_q):
        Thread.__init__(self)
        self.res_q = res_q
        self.wait_q = wait_q
        self.work_q = work_q

    def run(self):
        attacker = self.work_q.get()
        if attacker:
            n = 100
        elif random.uniform(0, 1) > 0.9:
            n = 9
        else:
            n = 29
        n = 1
        if attacker:
            delay = 0
        else:
            # mean of 60 seconds
            delay = random.expovariate(1.0/45)
        start = time.time()
        urllib2.urlopen(url + str(n))
        end = time.time()
        self.res_q.put((n, end - start))
        self.wait_q.put((time.time() + delay, attacker))
        self.work_q.task_done()

def do_fetch(attacker, res_q, wait_q, work_q):
    work_q.put(attacker)
    f = fetcher(res_q, wait_q, work_q)
    f.start()

def main(argv=None):
    if argv is None:
        argv = sys.argv

    wait_q = PriorityQueue()
    work_q = Queue()
    res_q = Queue()

    out_file = open('latency.csv', 'w')

    print "Running the gauntlet:"
    for i in range(256):
        wait_q.put((time.time(), False))

    while True:
        t, attacker = wait_q.get()
        delta = t - time.time()
        delay = max(delta, 0)
        out_file.write("%f, " % delay)
        out_file.flush()
        Timer(delay, do_fetch, (attacker, res_q, wait_q, work_q)).start()
        wait_q.task_done()

        while not res_q.empty():
            res = res_q.get()
            out_file.write("%d, %f\n" % (res[0], res[1]))
            res_q.task_done()

    work_q.join()

    while not res_q.empty():
        res = res_q.get()
        out_file.write("%d, %f\n" % (res[0], res[1]))
        res_q.task_done()

    return 0

if __name__ == "__main__":
    sys.exit(main())


