import unittest
import time
from threaders import threaders
from random import randrange
import threading


class TestThreaders(unittest.TestCase):
    def test_threaders(self):
        @threaders.threader()
        def function_to_be_threaded(x):
            """
            :rtype: threaders.Thread
            """
            t = time.time()
            time.sleep(0.01 * x)
            return time.time() - t

        t = time.time()

        # create threads
        threads = []
        for i in range(10):
            threads.append(function_to_be_threaded(i))

        self.assertEqual(len(threads), 10)

        self.assertGreater(0.01, threaders.get_first_result(threads))

        # kill threads
        for thread in threads:
            thread.join()

        self.assertGreater(time.time() - t, 0.09)

    def test_thread_pool(self):
        # create data
        delays = (randrange(1, 3)*0.01 for _ in range(50))

        # add lock
        print_lock = threading.Lock()

        def wait_delay(i, d):
            with print_lock:
                pass
            time.sleep(d)
            return i

        # create thread pool
        pool = threaders.ThreadPool(20, collect_results=True, worker_collect_results=True)
        for i, d in enumerate(delays):
            pool.put(wait_delay, i, d)

        self.assertIn(threaders.get_first_result(pool.threads, timeout=1), range(50))
        pool.join()

        # validation
        self.assertEqual(pool.results.qsize(), 50)

    def test_thread_pool_first_result(self):
        def wait_delay():
            from random import randint
            tt = randint(1, 5) * 0.01
            time.sleep(tt)
            return tt

        pool = threaders.ThreadPool(5, collect_results=True)
        for _ in range(20):
            pool.put(wait_delay)

        self.assertIn(pool.get(), (0.01, 0.02, 0.03, 0.04, 0.05))
        pool.join()

    def test_thread_pool_first_result_timeout(self):
        def wait_delay():
            from random import randint
            tt = randint(1, 5) * 0.01
            time.sleep(tt)
            return tt

        pool = threaders.ThreadPool(5, collect_results=True)
        for _ in range(20):
            pool.put(wait_delay)

        validation = False
        while not pool.tasks.empty():
            try:
                pool.get(timeout=0.009)
            except TimeoutError:
                validation = True
                break

        pool.join()
        self.assertEqual(validation, True)

    def test_thread_pool_first_result_return_none(self):
        def wait_delay():
            from random import randint
            tt = randint(1, 5) * 0.1
            time.sleep(tt)

        pool = threaders.ThreadPool(5, collect_results=True)
        for _ in range(1):
            pool.put(wait_delay)

        validation = pool.get()

        pool.join()
        self.assertEqual(validation, None)

    def test_thread_pool_first_result_return_none_with_timeout(self):
        def wait_delay():
            from random import randint
            tt = randint(1, 5) * 0.1
            time.sleep(tt)

        pool = threaders.ThreadPool(5, collect_results=True)
        for _ in range(1):
            pool.put(wait_delay)

        validation = pool.get(timeout=1)

        pool.join()
        self.assertEqual(validation, None)

    def test_thread_pool_first_result_raise_timeout_before_returning_none(self):
        def wait_delay():
            from random import randint
            tt = randint(1, 5) * 0.1
            time.sleep(tt)

        pool = threaders.ThreadPool(5, collect_results=True)
        for _ in range(1):
            pool.put(wait_delay)

        try:
            validation = False
            pool.get(timeout=0.09)
        except TimeoutError:
            validation = True

        pool.join()
        self.assertEqual(validation, True)


if __name__ == '__main__':
    unittest.main()
