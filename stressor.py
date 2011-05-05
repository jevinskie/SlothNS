#!/usr/bin/env python

import sys
import time
import urllib2
import random
from threading import Timer, Thread
from Queue import PriorityQueue, Empty
import os
from slothresolv import query
from multiprocessing import Pool, Manager, Queue
sys.path.append('./pow')
from pow import *
import logging

logger = logging.getLogger('stressor')
hdlr = logging.FileHandler('stressor.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

url = 'http://172.18.48.92:8080/fib.php?n='

p = pow(22, 0)
shared_pow = pow(p.n, p.seed, share = p)

wait_q_q = Queue()
res_q = Queue()

class fetcher(Thread):
    def __init__(self, res_q, wait_q_q, work_q):
        Thread.__init__(self)
        self.res_q = res_q
        self.wait_q_q = wait_q_q
        self.work_q = work_q

def fetch(attacker, id):
    pow_obj = shared_pow
    if attacker:
        n = 100
    elif random.uniform(0, 1) > 0.9:
        n = 29
    else:
        n = 9
    logger.info("id: %d asking for n: %d pid: %d" % (id, n, os.getpid()))
    if attacker:
        delay = 0
    else:
        delay = random.expovariate(1.0/45)
    start = time.time()
    query('google.com', logger, id = id, pow_obj = pow_obj)
    logger.info("id: %d completed PoW, sending HTTP req for n: %d" % (id, n))
    try:
        urllib2.urlopen(url + str(n) + "&id=%d" % id)
        error = 0
    except urllib2.URLError:
        error = 1
    end = time.time()
    res_q.put((id, n, end - start, error), timeout=5)
    wait_q_q.put((time.time() + delay, attacker, id), timeout=5)

start_time = time.time()


def main(argv=None):
    if argv is None:
        argv = sys.argv

    id_base = int(sys.argv[1])

    manager = Manager()

    wait_q = PriorityQueue()

    out_file = open('latency.csv', 'a')

    logger.info("PID: %d" % os.getpid())
    logger.info("Running the gauntlet:")
    id = id_base
    num_clients = 0
    for i in range(10):
        wait_q.put((time.time(), False, id))
        id += 1
        num_clients += 1
    for i in range(10):
        wait_q.put((time.time(), True, id))
        id += 1
        num_clients += 1

    pool = Pool(processes=num_clients)

    while True:
        t, attacker, id = wait_q.get()
        delta = t - time.time()
        delay = max(delta, 0)
        if delay > 0:
            Timer(delay, pool.apply_async, (fetch, (attacker, id))).start()
        else:
            pool.apply_async(fetch, (attacker, id))
        wait_q.task_done()

        while not wait_q_q.empty():
            wait_q.put(wait_q_q.get(timeout = 5))

        # we have to make sure there is at least one element in wait_q before the end of the loop
        if wait_q.empty():
            r = wait_q_q.get()
            wait_q.put(r)

        while not res_q.empty():
            id, n, t, error = res_q.get(timeout = 5)
            logger.info("id: %d got a response for n = %d in %f error: %d" % (id, n, t, error))
            out_file.write("%d, %d, %f, %d\n" % (id, n, t, error))
            out_file.flush()
        if time.time() - start_time > 120:
            break


    while not res_q.empty():
        res = res_q.get()
        out_file.write("%d, %f, %d\n" % (res[0], res[1], res[2]))

    return 0

if __name__ == "__main__":
    sys.exit(main())


