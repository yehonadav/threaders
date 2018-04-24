# -*- coding: utf-8 -*-
#
# Copyright 2018 Yehonadav Bar Elan
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

""" this is a nice module to make your threading life super easy.
please enjoy =)
here is a usage example code:

from threaders import threaders
import time


@threaders.threader()
def function_to_be_threaded(x):
    ''' :rtype: threaders.Thread '''
    t = time.time()
    time.sleep(0.5*(x+0.1)/5+0.05)
    return time.time()-t


def main():
    # create threads
    threads = []
    for i in range(10):
        threads.append(function_to_be_threaded(i))

    # get first result
    print(threaders.get_first_result(threads))

    # kill threads
    t = time.time()
    for thread in threads:
        thread.join()
    print("all threads terminated: {}".format(time.time()-t))


if __name__ == "__main__":
    main()
"""

import threading
from queue import Queue, Empty
from time import time


class Thread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, max_results=0, daemon=None):
        self.results = Queue(max_results)
        threading.Thread.__init__(self, group, target, name, (self.results,) + args, kwargs, daemon=daemon)


def threader(group=None, name=None, daemon=True):
    """ decorator to thread functions
    :param group: reserved for future extension when a ThreadGroup class is implemented
    :param name: thread name
    :param daemon: thread behavior """

    def decorator(target):
        """ :param target: function to be threaded """

        def wrapped_job(queue, *args, **kwargs):
            """ this function calls the decorated function
            and puts the result in a queue
            :type queue: Queue """
            queue.put(target(*args, **kwargs))

        def wrap(*args, **kwargs):
            """ this is the function returned from the decorator. It fires off
            wrapped_f in a new thread and returns the thread object with
            the result queue attached
            :rtype: Thread """
            thread = Thread(group=group, target=wrapped_job, name=name, args=args, kwargs=kwargs, daemon=daemon)
            thread.start()
            return thread

        return wrap

    return decorator


class ThreadWorker(Thread):
    """Thread executing tasks from a given tasks queue
    :type pool: ThreadPool """

    def __init__(self, pool, group=None, name=None, daemon=True, collect_results=False, max_results=0, timeout=0.1):
        Thread.__init__(self, group=group, name=name, daemon=daemon, max_results=max_results)
        self.pool = pool
        self.start()
        self.collect_results = collect_results
        self.running_task = None
        self.timeout = timeout

    def start(self):
        Thread.start(self)

    def run(self):
        while self._is_stopped is False:
            if self.pool.lifecycle is not None:
                if self.pool.lifecycle <= time() - self.pool.creation_time:
                    if self.pool.is_stopped is False:
                        self.pool.is_stopped = True
                    self.stop()
                    break
            if self.pool.tasks.qsize() > 0:
                try:
                    self.running_task = target, args, kwargs = self.pool.tasks.get(timeout=self.timeout)
                    result = target(*args, **kwargs)
                    self.running_task = None
                    self.pool.tasks.task_done()
                    if result is not None:
                        if self.pool.collect_results is True:
                            self.pool.results.put(result)
                        if self.collect_results is True:
                            self.results.put(result)
                except Empty:
                    pass
                except Exception as e:
                    if self.pool.store_errors is True:
                        self.pool.errors.put(e)
                    else:
                        self.stop()
                        self.pool.add()
                        raise e

    def stop(self):
        self._is_stopped = True


class ThreadPool:
    """Pool of threads consuming tasks from a queue"""

    def __init__(
            self,
            workers=1,
            lifecycle=None,
            max_tasks=0,
            daemon=True,
            collect_results=False,
            worker_collect_results=False,
            max_results=0,
            max_worker_results=0,
            timeout=0.1,
            store_errors=False):
        """ create a pool of workers, run tasks, collect results
        :param workers: number of workers
        :param lifecycle: give your pool a set time to live before stopping
        :param max_tasks: limit the tasks queue
        :param collect_results: you can collect results from your workers
        :type workers: int
        :type lifecycle: int
        :type max_tasks: int
        :type collect_results: bool
        """
        self.tasks = Queue(max_tasks)
        self.errors = Queue(max_tasks)
        self.collect_results = collect_results
        self.is_stopped = False
        self.results = Queue(max_results)
        self.lifecycle = lifecycle
        self.creation_time = time()
        self.timeout = timeout
        self.store_errors = store_errors
        self.worker_collect_results = worker_collect_results
        self.daemon = daemon
        self.max_worker_results = max_worker_results
        self.threads = [
            ThreadWorker(self, collect_results=worker_collect_results, daemon=daemon, max_results=max_worker_results,
                         timeout=timeout) for _ in range(workers)]

    def add(self):
        self.threads.append(ThreadWorker(self, collect_results=self.worker_collect_results, daemon=self.daemon,
                                         max_results=self.max_worker_results,
                                         timeout=self.timeout))

    def put(self, target, *args, **kwargs):
        """Add a task to the queue"""
        self.tasks.put((target, args, kwargs))

    def join(self):
        """Wait for completion of all the tasks in the queue"""
        if self.is_stopped is False:
            while not self.tasks.empty():
                pass
            self.stop()
        for thread in self.threads:
            thread.join()

    def stop(self):
        self.is_stopped = True
        for thread in self.threads:
            thread.stop()

    def start(self):
        self.is_stopped = False
        for thread in self.threads:
            thread.start()

    def get_all(self, timeout=None):
        results = []
        while not self.results.empty():
            try:
                results.append(self.results.get(timeout))
            except:
                pass
        return results

    def get(self, timeout=None):
        """ will return the first unNone result.
        this method demand for self.collect_results = True
        if no results are found, will return None
        :type timeout: float
        """
        t = time()
        some_tasks_are_running = None
        while self.collect_results:
            # get result
            if not self.results.empty():
                try:
                    return self.results.get(self.timeout)
                except Empty:
                    pass

            # return none if all tasks are done but there are no results
            while self.tasks.empty():
                some_tasks_are_running = False
                for thread in self.threads:
                    if timeout is not None and time() - t >= timeout:
                        raise TimeoutError
                    elif thread.running_task is not None:
                        some_tasks_are_running = True
                        break
                if some_tasks_are_running is False:
                    break
            if some_tasks_are_running is False:
                return None

            if timeout is not None and time() - t >= timeout:
                raise TimeoutError

    def get_and_stop(self, timeout=None):
        try:
            return self.get(timeout)
        finally:
            self.stop()

    def get_and_join(self, timeout=None):
        try:
            return self.get(timeout)
        finally:
            self.join()

    def get_stop_and_join(self, timeout=None):
        try:
            return self.get_and_stop(timeout)
        finally:
            self.join()

    def get_all_and_stop(self, timeout=None):
        try:
            return self.get_all(timeout)
        finally:
            self.stop()

    def get_all_and_join(self, timeout=None):
        try:
            return self.get_all(timeout)
        finally:
            self.join()

    def get_all_stop_and_join(self, timeout=None):
        try:
            return self.get_all_and_stop(timeout)
        finally:
            self.join()


def get_first_result(threads, timeout=None):
    """ this blocks, waiting for the first result that returns from a thread
    :type threads: list[Thread]
    :type timeout: float
    """
    t = time()
    while True:
        for thread in threads:
            if not thread.results.empty():
                return thread.results.get()
        if timeout is not None:
            if time() - t >= timeout:
                raise TimeoutError
