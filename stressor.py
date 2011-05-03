#!/usr/bin/env python

#!/usr/bin/env python

from multiprocessing import Pool
import sys
import time
import urllib2
import random

from multiprocessing.pool import IMapIterator

url = 'http://rossmann-a246.rcac.purdue.edu:8080/fib.php?n='

def wrapper(func):
  def wrap(self, timeout=None):
    # Note: the timeout of 1 googol seconds introduces a rather subtle 
    # bug for Python scripts intended to run many times the age of the universe.
    return func(self, timeout=timeout if timeout is not None else 1e100)
  return wrap
IMapIterator.next = wrapper(IMapIterator.next)

def fetch(delay, attacker = False):
    time.sleep(delay)
    if attacker:
        n = 10
    elif random.uniform(0, 1) > 0.9:
        n = 29
    else:
        n = 9
    n = 1
    if attacker:
        delay = 0
    else:
        # mean of 60 seconds
        delay = random.expovariate(1.0/60)
    start = time.time()
    urllib2.urlopen(url + str(n))
    end = time.time()
    return (n, end - start, delay)




def main(argv=None):
    if argv is None:
        argv = sys.argv

    pool = Pool(processes=100)

    out_file = open('latency.csv', 'w')
    
    def process_result(res):
        out_file.write("%d, %f, %f\n" % (res[0], res[1], res[2]))
        #if ran < 1000:
        #    pool.apply_async(fetch, (res[2],), callback=process_result)

    print "Running the gauntlet:"
    for i in range(50):
        pool.apply_async(fetch, (0,), callback=process_result)

    pool.close()
    pool.join()


    return 0

if __name__ == "__main__":
    sys.exit(main())


