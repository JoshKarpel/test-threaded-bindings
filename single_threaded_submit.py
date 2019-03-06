#!/usr/bin/env python

from __future__ import print_function

import htcondor

import utils


def test_single_threaded_submit():
    submit = utils.dummy_submit()

    schedd = htcondor.Schedd()
    with schedd.transaction() as txn:
        result = submit.queue(txn, 1)
        print('submit result', result)

    utils.condor_q()


if __name__ == '__main__':
    test_single_threaded_submit()
