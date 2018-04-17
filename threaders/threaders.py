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

import threaders
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
from queue import Queue


class Thread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        self.queue = Queue()
        threading.Thread.__init__(self, group, target, name, (self.queue,) + args, kwargs, daemon=daemon)


def threader(group=None, name=None, daemon=True):
    """ decorator to thread functions
    :param group: reserved for future extension when a ThreadGroup class is implemented
    :param name: thread name
    :param daemon: thread behavior
    :rtype: decorator
    """
    def decorator(job):
        """
        :param job: function to be threaded
        :rtype: wrap
        """
        def wrapped_job(queue, *args, **kwargs):
            """ this function calls the decorated function
            and puts the result in a queue
            :type queue: Queue
            """
            ret = job(*args, **kwargs)
            queue.put(ret)

        def wrap(*args, **kwargs):
            """ this is the function returned from the decorator. It fires off
            wrapped_f in a new thread and returns the thread object with
            the result queue attached
            :rtype: Thread
            """
            thread = Thread(group=group, target=wrapped_job, name=name, args=args, kwargs=kwargs, daemon=daemon)
            thread.start()
            return thread
        return wrap
    return decorator


def get_first_result(threads):
    """ this blocks, waiting for the first result that returns from a thread
    :type threads: list[Thread]
    """
    while True:
        for thread in threads:
            if not thread.is_alive():
                return thread.queue.get()
