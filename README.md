# test-threaded-bindings

Testing the multi-threadability of the HTCondor Python bindings.

## Setup

`git clone https://github.com/htcondor/python-bindings-crashes`

If you don't have a local HTCondor install, use the `dr` script to run something in Docker.
Running `dr` without any arguments will land you in a `bash` shell.
See the Dockerfile in `docker/Dockerfile` for possible build arguments (to change Python or HTCondor versions).
If you need to use build args you won't be able to use the `dr` script (unless you edit it).
Sorry!

Some of the test scripts take arguments, often the number of jobs to submit.

Example calls:
```
dr
dr python tests/single_threaded_submit.py 10
dr python tests/separate_transactions_raw.py 100
```

## Test Results

### `single_threaded_submit`

Behaves as expected!

### `shared_everything_raw`

Raw threading, sharing the `Schedd`, `transaction`, and `Submit`.
Works correctly for 1 job, but fails when the number of jobs is more than a few with:

```
<same exception from each thread as below>
...
Exception in thread Thread-9:
Traceback (most recent call last):
  File "/opt/conda/lib/python3.7/threading.py", line 917, in _bootstrap_inner
    self.run()
  File "/opt/conda/lib/python3.7/threading.py", line 865, in run
    self._target(*self._args, **self._kwargs)
  File "shared_everything_raw.py", line 16, in do_submit
    result = submit.queue(txn, 1)
RuntimeError: Failed to create new cluster.

Exception in thread Thread-10:
Traceback (most recent call last):
  File "/opt/conda/lib/python3.7/threading.py", line 917, in _bootstrap_inner
    self.run()
  File "/opt/conda/lib/python3.7/threading.py", line 865, in run
    self._target(*self._args, **self._kwargs)
  File "shared_everything_raw.py", line 16, in do_submit
    result = submit.queue(txn, 1)
RuntimeError: Failed to create new cluster.

Traceback (most recent call last):
  File "shared_everything_raw.py", line 41, in <module>
    test_multi_threaded_submit_raw_shared(num_jobs)
  File "shared_everything_raw.py", line 33, in test_multi_threaded_submit_raw_shared
    t.join()
RuntimeError: Failed to commmit and disconnect from queue.
```

### `shared_everything_executor`

Same as previous, but use a `ThreadPoolExecutor` to manage the threads (this is the more modern way).
I suspect this fails in exactly the same way as previous, but we only get the exception from the main thread this time:

```
Traceback (most recent call last):
  File "shared_everything_executor.py", line 35, in <module>
    test_multi_threaded_submit_raw_shared(num_jobs)
  File "shared_everything_executor.py", line 28, in test_multi_threaded_submit_raw_shared
    pool.submit(do_submit, txn, submit)
RuntimeError: Failed to commmit and disconnect from queue.
```

### `separate_transactions_raw`

In this one I try to build individual transactions for each thread.
Explodes for even one job, although it looks like that job does actually make it into the queue.

```
140022410094336 15
Traceback (most recent call last):
  File "separate_transactions_raw.py", line 41, in <module>
    test_separate_transactions_raw(num_jobs)
  File "separate_transactions_raw.py", line 30, in test_separate_transactions_raw
    t.start()
RuntimeError: Failed to commit ongoing transaction. SCHEDD:2:Failed to apply a required job transform.

$ condor_q
-- Schedd: test@cb90524ecd52 : <172.17.0.2:9618?... @ 03/06/19 16:48:33
OWNER    BATCH_NAME         SUBMITTED   DONE   RUN    IDLE   HOLD  TOTAL JOB_IDS
test     140022410094336   3/6  16:48      _      _      _      1      1 15.0

Total for query: 5 jobs; 0 completed, 0 removed, 0 idle, 0 running, 5 held, 0 suspended
Total for all users: 5 jobs; 0 completed, 0 removed, 0 idle, 0 running, 5 held, 0 suspended
```

Note that matching batch name.

### `ephemeral_schedd`

When doing `with htcondor.Schedd().transaction() as txn:`, the `Schedd` object
has no references to it, and is immediately freed. If this happens before the
transaction finishes, it explodes.

Ticket: https://htcondor-wiki.cs.wisc.edu/index.cgi/tktview?tn=6721

```
Traceback (most recent call last):
  File "/home/test/tests/ephemeral_schedd.py", line 22, in <module>
    test_ephemeral_schedd()
  File "/home/test/tests/ephemeral_schedd.py", line 15, in test_ephemeral_schedd
    result = submit.queue(txn, 1)
RuntimeError: Job queue attempt without active transaction
```
