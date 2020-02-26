import os

import htcondor


def held_submit():
    return htcondor.Submit({"executable": "fubar", "hold": "true",})


def short_sleep_submit():
    return htcondor.Submit({"executable": "/bin/sleep", "arguments": "1",})


def condor_q():
    os.system("condor_q")
