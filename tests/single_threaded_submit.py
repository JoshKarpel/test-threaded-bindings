#!/usr/bin/env python

from __future__ import print_function

import sys
import htcondor

import utils


def test_single_threaded_submit(num_jobs):
    submit = utils.dummy_submit()

    schedd = htcondor.Schedd()
    with schedd.transaction() as txn:
        for _ in range(num_jobs):
            result = submit.queue(txn, 1)
            print('submit result', result)

    utils.condor_q()


if __name__ == '__main__':
    num_jobs = int(sys.argv[1])
    test_single_threaded_submit(num_jobs)
