threaders


threaders is a small module to help write

clean threaded code using threading decorators

and minimize repeating copy-paste actions.


Installing


Install and update using pip:

pip install -U threaders


A Simple Example:


from threaders import threaders

import time


@threaders.threader()

def function_to_be_threaded(x):

    """ :rtype: Thread """

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




Example with a thread pool:




from random import randrange

from time import sleep

import threading


delays = [randrange(1, 3) for i in range(50)]

print_lock = threading.Lock()


def wait_delay(i, d):

    with print_lock:

        print('{} sleeping for ({})sec'.format(i, d))

    sleep(d)


pool = threaders.ThreadPool(10)


for i, d in enumerate(delays):

    pool.put(wait_delay, i, d)


pool.join()
