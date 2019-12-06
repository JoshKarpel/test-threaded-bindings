#!/usr/bin/env python

from __future__ import print_function

import htcondor

import time
import sys
import threading
import faulthandler

import utils


def run_test(num_query_threads = 1):
    submit_thread = threading.Thread(target = submit_forever, name = 'submit'.ljust(10))
    query_threads = [
        threading.Thread(target = query_forever, name = 'query-{}'.format(i).ljust(10))
        for i in range(num_query_threads)
    ]

    submit_thread.start()
    for qt in query_threads:
        qt.start()


def submit_forever():
    while True:
        sub = utils.short_sleep_submit()
        schedd = htcondor.Schedd()
        log("about to get submit transaction")
        with schedd.transaction() as txn:
            time.sleep(.1)
            log("got submit transaction")
            result = sub.queue(txn, 1)
            log("submitted and got result", result)
        log("exited submit transaction block")


def query_forever():
    while True:
        schedd = htcondor.Schedd()
        log("about to query")
        results = schedd.query()
        log("query result length: {}".format(len(results)))


def log(*args):
    print("{:.6f}".format(time.time()), threading.current_thread().name, *args)


if __name__ == '__main__':
    faulthandler.enable(file = sys.stderr, all_threads = True)
    num_query_threads = int(sys.argv[1])

    htcondor.enable_debug()
    run_test(num_query_threads = num_query_threads)
