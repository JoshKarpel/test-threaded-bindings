#!/usr/bin/env python

from __future__ import print_function

import sys
import threading

import htcondor

import utils


def do_submit(txn, submit):
    ident = threading.get_ident()
    submit["JobBatchName"] = str(ident)
    result = submit.queue(txn, 1)
    print(ident, result)


def test_multi_threaded_submit_raw_shared(num_jobs):
    submit = utils.held_submit()

    schedd = htcondor.Schedd()
    with schedd.transaction() as txn:
        threads = []
        for _ in range(num_jobs):
            threads.append(threading.Thread(target=do_submit, args=(txn, submit)))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    utils.condor_q()


if __name__ == "__main__":
    num_jobs = int(sys.argv[1])

    test_multi_threaded_submit_raw_shared(num_jobs)
