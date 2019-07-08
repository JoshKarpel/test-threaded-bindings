#!/usr/bin/env python

from __future__ import print_function

import sys
import htcondor

import utils


def test_ephemeral_schedd():
    submit = utils.dummy_submit()

    with htcondor.Schedd().transaction() as txn:
        result = submit.queue(txn, 1)
        print('submit result', result)

    utils.condor_q()


if __name__ == '__main__':
    test_ephemeral_schedd()
