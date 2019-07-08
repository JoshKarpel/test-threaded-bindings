import os

import htcondor


def dummy_submit():
    return htcondor.Submit({
        'executable': 'fubar',
        'hold': 'true',
    })


def condor_q():
    os.system('condor_q')
