#!/usr/bin/env python

from __future__ import print_function

import htcondor

import time
import sys
import threading
import faulthandler

import functools
import contextlib

import utils

ORIGINAL_NAMES = {}


def add_locks(schedd):
    # print(schedd.__dict__)
    for name, method in schedd.__dict__.items():
        ORIGINAL_NAMES[method] = name
        if not callable(method):
            continue

        if name in {'__init__'}:
            continue

        print(name, method)
        if name in {'transaction'}:
            print('wrapping {} with context lock'.format(name))
            setattr(schedd, name, add_lock_to_context_manager(method))
        else:
            print('wrapping {} with normal lock'.format(name))
            setattr(schedd, name, add_lock(method))

    return schedd


LOCK = threading.RLock()


def add_lock(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        # log("waiting for lock {} for {}".format(LOCK, ORIGINAL_NAMES[method]))
        with LOCK:
            log("acquired lock {}".format(LOCK))
            x = method(*args, **kwargs)
            log("about to return and release lock {} for {}".format(LOCK, ORIGINAL_NAMES[method]))
            return x

    return wrapper


def add_lock_to_context_manager(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        return LockedContext(method(*args, **kwargs))

    return wrapper


class LockedContext:
    def __init__(self, cm):
        log("context lock __init__")
        self.cm = cm

    def __enter__(self):
        log("context lock __enter__")
        LOCK.acquire()
        log("acquired context lock {}".format(LOCK))
        return self.cm.__enter__()

    def __exit__(self, *args, **kwargs):
        log("context lock __exit__")
        try:
            return self.cm.__exit__(*args, **kwargs)
        finally:
            log("about to release context lock {}".format(LOCK))
            LOCK.release()


htcondor.Schedd = add_locks(htcondor.Schedd)


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
        time.sleep(.1)
        sub = utils.short_sleep_submit()
        schedd = htcondor.Schedd()
        log("about to get submit transaction")
        with schedd.transaction() as txn:
            log("got submit transaction")
            # result = sub.queue_with_itemdata(txn, 1, iter(["1", "2"]))
            result = sub.queue(txn, 1)
            log("submitted and got result", result)
        log("exited submit transaction block")


def query_forever():
    while True:
        time.sleep(.1)
        schedd = htcondor.Schedd()
        log("about to query")
        results = schedd.query()
        log("query result length: {}".format(len(results)))


def log(*args):
    print("{:.6f}".format(time.time()), threading.current_thread().name, *args)


if __name__ == '__main__':
    faulthandler.enable(file = sys.stderr, all_threads = True)
    num_query_threads = int(sys.argv[1])

    print(htcondor.Schedd)
    for k, v in htcondor.Schedd.__dict__.items():
        print(k, v)
    htcondor.enable_debug()
    run_test(num_query_threads = num_query_threads)
