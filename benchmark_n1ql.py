#!/usr/bin/env python

import cProfile
import pstats
import StringIO
from multiprocessing import Value, Lock
from spring.wgen import AsyncKVWorker, N1QLWorker


workload_settings = type(
                         'WorkloadSettings',
                         (object, ),
                         {
                         'creates': 0,
                         'reads': 0,
                         'updates': 100,
                         'deletes': 0,
                         'cases': 0,

                         'ops': 100,
                         'throughput': float('inf'),

                         'size': 2048,
                         'items': 10000,
                         'expiration': 0,
                         'working_set': 100,
                         'working_set_access': 100,

                         'workers': 0,
                         'query_workers': 0,
                         'dcp_workers': 0,

                         'n1ql_workers': 1,
                         'n1ql_throughput': 10,
                         'n1ql_queries': ['SELECT * FROM `{bucket}` USE KEYS(\"{key}\")']
                         }
                         )()

target_settings = type(
                       'TargetSettings',
                       (object, ),
                       {
                       'node': '127.0.0.1:8091',
                       'bucket': 'default',
                       'password': '',
                       'prefix': None,
                       }
                       )


def run():
    curr_queries = Value('L', 0)
    curr_items = Value('i', workload_settings.items)
    deleted_items = Value('i', 0)
    lock = Lock()

    worker = N1QLWorker(workload_settings, target_settings, None)
    worker.run(sid=0,
               lock=lock,
               curr_queries=curr_queries,
               curr_items=curr_items,
               deleted_items=deleted_items)

def profile():
    pr = cProfile.Profile()
    s = StringIO.StringIO()

    pr.enable()
    run()
    pr.disable()

    ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
    ps.reverse_order()
    ps.print_stats()
    ps.dump_stats('profile.prof')


if __name__ == '__main__':
    profile()