#!/usr/bin/env python

from __future__ import print_function

import sys
import threading

import htcondor

import utils


def do_submit(txn, submit):
    ident = threading.get_ident()
    submit['JobBatchName'] = str(ident)
    result = submit.queue(txn, 1)
    print(ident, result)


def test_separate_transactions_raw(num_jobs):
    submit = utils.dummy_submit()

    schedd = htcondor.Schedd()

    threads = []
    for _ in range(num_jobs):
        with schedd.transaction() as txn:
            t = threading.Thread(target = do_submit, args = (txn, submit))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()

    utils.condor_q()


if __name__ == '__main__':
    num_jobs = int(sys.argv[1])

    test_separate_transactions_raw(num_jobs)
