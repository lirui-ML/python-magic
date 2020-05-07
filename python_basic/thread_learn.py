#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参考：
    1. https://mp.weixin.qq.com/s/jwbgKc8AZiiZ-WEmgOpucg
    2. https://mp.weixin.qq.com/s/Tj_Ivu0Xn7bQNbe_RId1Xw
"""

import time
import threading
import logging
from concurrent.futures import ThreadPoolExecutor

def time_cal(func):
    def wrap(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        end_time = time.time()
        print("use time: {}".format(end_time - start_time))
        return res
    return wrap

def thread_func(name):
    logging.info("Thread %s: starting", name)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)

@time_cal
def single_thread_main():
    logformat = "%(asctime)s: %(message)s"
    logging.basicConfig(format=logformat, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main  : before creating thread")
    x = threading.Thread(target=thread_func, args=(1,), daemon=True)
    logging.info("Main    : before running thread")
    x.start()
    logging.info("Main    : wait for the thread to finish")
    x.join()
    logging.info("Main    : all done")

@time_cal
def multi_thread_main():
    logformat = "%(asctime)s: %(message)s"
    logging.basicConfig(format=logformat, level=logging.INFO,
                        datefmt="%H:%M:%S")

    threads = []
    for index in range(3):
        logging.info("Main    : create and start thread %d.", index)
        x = threading.Thread(target=thread_func, args=(index, ))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)

@time_cal
def threadPool_main():
    logformat = "%(asctime)s: %(message)s"
    logging.basicConfig(format=logformat, level=logging.INFO,
                        datefmt="%H:%M:%S")

    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(thread_func, range(3))


class FakeDatabase:
    def __init__(self):
        self.value = 0

    def update(self, name):
        logging.info("Thread %s: starting update", name)
        local_copy = self.value
        local_copy += 1
        time.sleep(0.1)
        self.value = local_copy
        logging.info("Thread %s: finishing update", name)


def race_conditons_main():
    logformat = "%(asctime)s: %(message)s"
    logging.basicConfig(format=logformat, level=logging.INFO,
                        datefmt="%H:%M:%S")

    database = FakeDatabase()
    logging.info("Testing update. Starting value is %d.", database.value)
    with ThreadPoolExecutor(max_workers=2) as executor:
        for index in range(2):
            executor.submit(database.update, index)
    logging.info("Testing update. Ending value is %d.", database.value)


if __name__ == '__main__':
    # single_thread_main()
    # multi_thread_main()
    # threadPool_main()
    race_conditons_main()


