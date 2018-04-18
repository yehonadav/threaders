import unittest
import time
from threaders import threaders
from random import randrange
import threading


class TestThreaders(unittest.TestCase):
    testing_data = dict(
    )

    # expected results
    expected_results = (
    )

    def test_threaders(self):

        @threaders.threader()
        def function_to_be_threaded(x):
            """
            :rtype: threaders.Thread
            """
            t = time.time()
            time.sleep(0.01 * x)
            return time.time() - t

        # create threads
        threads = []
        for i in range(10):
            threads.append(function_to_be_threaded(i))

        self.assertEqual(len(threads), 10)

        # get first result
        assert threaders.get_first_result(threads) < 0.01

        # kill threads
        t = time.time()
        for thread in threads:
            thread.join()

        assert time.time() - t > 0.09

    def test_thread_pool(self):
        delays = [randrange(1, 3)*0.1 for i in range(50)]
        print_lock = threading.Lock()

        def wait_delay(i, d):
            with print_lock:
                print('{} sleeping for ({})sec'.format(i, d))
            time.sleep(d)

        pool = threaders.ThreadPool(20)

        for i, d in enumerate(delays):
            pool.put(wait_delay, i, d)

        pool.join()


if __name__ == '__main__':
    unittest.main()
