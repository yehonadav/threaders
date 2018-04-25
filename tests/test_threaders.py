import unittest
import time
from threaders import threaders
from random import randrange
import threading


class TestThreaders(unittest.TestCase):
    def test_threaders(self):
        @threaders.threader()
        def function_to_be_threaded(x):
            """:rtype: threaders.Thread"""
            t = time.time()
            time.sleep(0.01 * x)
            return time.time() - t

        test_start_time = time.time()
        t = time.time()

        # create threads
        threads = [function_to_be_threaded(i) for i in range(10)]

        self.assertEqual(len(threads), 10)

        self.assertGreater(0.01, threaders.get_first_result(threads))

        # kill threads
        for thread in threads:
            thread.join()

        self.assertGreater(time.time() - t, 0.09)

        test_end_time = time.time()
        print("test_threaders {}s".format(test_end_time - test_start_time))
        self.assertGreater(5, threading.active_count())

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

        test_start_time = time.time()

        # create thread pool
        pool = threaders.ThreadPool(workers=20, collect_results=True, worker_collect_results=True)
        for i, d in enumerate(delays):
            pool.put(wait_delay, i, d)

        self.assertIn(threaders.get_first_result(pool.threads, timeout=1), range(50))
        pool.join()

        # validation
        self.assertEqual(pool.results.qsize(), 50)

        test_end_time = time.time()
        print("test_thread_pool {}s".format(test_end_time - test_start_time))
        self.assertGreater(5, threading.active_count())

    def test_thread_pool_first_result(self):
        def wait_delay():
            from random import randint
            tt = randint(1, 5) * 0.01
            time.sleep(tt)
            return tt

        test_start_time = time.time()

        pool = threaders.ThreadPool(workers=5, collect_results=True)
        for _ in range(20):
            pool.put(wait_delay)

        self.assertIn(pool.get(), (0.01, 0.02, 0.03, 0.04, 0.05))
        pool.join()

        test_end_time = time.time()
        print("test_thread_pool_first_result {}s".format(test_end_time - test_start_time))
        self.assertGreater(5, threading.active_count())

    def test_thread_pool_first_result_timeout(self):
        def wait_delay():
            from random import randint
            tt = randint(1, 5) * 0.01
            time.sleep(tt)
            return tt

        test_start_time = time.time()

        pool = threaders.ThreadPool(workers=5, collect_results=True)
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

        test_end_time = time.time()
        print("test_thread_pool_first_result_timeout {}s".format(test_end_time - test_start_time))
        self.assertGreater(5, threading.active_count())

    def test_thread_pool_first_result_return_none(self):
        def wait_delay():
            from random import randint
            tt = randint(1, 5) * 0.1
            time.sleep(tt)

        test_start_time = time.time()

        pool = threaders.ThreadPool(workers=5, collect_results=True)
        for _ in range(1):
            pool.put(wait_delay)

        validation = pool.get()

        pool.join()
        self.assertEqual(validation, None)

        test_end_time = time.time()
        print("test_thread_pool_first_result_return_none {}s".format(test_end_time - test_start_time))
        self.assertGreater(5, threading.active_count())

    def test_thread_pool_first_result_return_none_with_timeout(self):
        def wait_delay():
            from random import randint
            tt = randint(1, 5) * 0.1
            time.sleep(tt)

        test_start_time = time.time()

        pool = threaders.ThreadPool(workers=5, collect_results=True)
        for _ in range(1):
            pool.put(wait_delay)

        validation = pool.get(timeout=1)

        pool.join()
        self.assertEqual(validation, None)

        test_end_time = time.time()
        print("test_thread_pool_first_result_return_none_with_timeout {}s".format(test_end_time - test_start_time))
        self.assertGreater(5, threading.active_count())

    def test_thread_pool_first_result_raise_timeout_before_returning_none(self):
        def wait_delay():
            from random import randint
            tt = randint(1, 5) * 0.1
            time.sleep(tt)

        test_start_time = time.time()

        pool = threaders.ThreadPool(workers=5, collect_results=True)
        for _ in range(1):
            pool.put(wait_delay)

        try:
            validation = False
            pool.get(timeout=0.09)
        except TimeoutError:
            validation = True

        pool.join()
        self.assertEqual(validation, True)

        test_end_time = time.time()
        print("test_thread_pool_first_result_raise_timeout_before_returning_none {}s".format(test_end_time - test_start_time))
        self.assertGreater(5, threading.active_count())

    def test_thread_pool_get_stop_and_join(self):
        def wait_delay():
            from random import randint
            tt = randint(1, 5) * 0.1
            time.sleep(tt)
            return tt

        test_start_time = time.time()

        pool = threaders.ThreadPool(workers=5, collect_results=True)
        for _ in range(100):
            pool.put(wait_delay)

        t = time.time()
        pool.get_stop_and_join()
        t = time.time() - t

        self.assertGreater(1, t)

        test_end_time = time.time()
        print("test_thread_pool_get_stop_and_join {}s".format(test_end_time - test_start_time))
        self.assertGreater(5, threading.active_count())

    def test_thread_pool_get_none_stop_and_join(self):
        def wait_delay():
            time.sleep(0.1)

        test_start_time = time.time()

        pool = threaders.ThreadPool(workers=5, collect_results=True)
        for _ in range(30):
            pool.put(wait_delay)

        t = time.time()
        pool.get_stop_and_join()
        t = time.time() - t

        self.assertGreater(1, t)

        test_end_time = time.time()
        print("test_thread_pool_get_none_stop_and_join {}s".format(test_end_time - test_start_time))
        pool.join()
        self.assertGreater(5, threading.active_count())

    def test_thread_pool_with_lifecycle(self):
        def wait_delay():
            time.sleep(0.1)
            return threading.current_thread().name

        test_start_time = time.time()

        pool = threaders.ThreadPool(workers=30, lifecycle=1, collect_results=True)
        for _ in range(1000):
            pool.put(wait_delay)

        time.sleep(1.1)
        self.assertEqual(pool.is_stopped, True)

        results_size = pool.results.qsize()
        self.assertGreater(301, results_size)
        self.assertGreater(results_size, 250)

        test_end_time = time.time()
        print("test_thread_pool_with_lifecycle {}s".format(test_end_time-test_start_time))
        pool.join()
        self.assertGreater(5, threading.active_count())

    def test_thread_pool_with_error_storage(self):
        def wait_delay():
            time.sleep(0.1)
            return threading.current_thread().name

        def raise_exception():
            ex = 1 + ""

        test_start_time = time.time()

        pool = threaders.ThreadPool(workers=30, lifecycle=100, collect_results=True, store_errors=True)
        for _ in range(100):
            pool.put(wait_delay)
        pool.put(raise_exception)

        while pool.errors.qsize() < 1:
            pass

        self.assertEqual(len(pool.threads), 30)
        pool.join()

        error = pool.errors.get()
        with self.assertRaises(TypeError):
            raise error

        test_end_time = time.time()
        print("test_thread_pool_with_error_storage {}s".format(test_end_time-test_start_time))
        self.assertGreater(5, threading.active_count())

    def test_thread_pool_with_exception(self):
        def wait_delay():
            time.sleep(0.001)
            return threading.current_thread().name

        def raise_exception():
            ex = 1 + ""

        test_start_time = time.time()

        pool = threaders.ThreadPool(workers=30, lifecycle=100, collect_results=True)
        pool.put(raise_exception)
        for _ in range(100):
            pool.put(wait_delay)

        self.assertGreater(threading.active_count(), 30)

        try:
            pool.join()
        except TypeError:
            pass

        test_end_time = time.time()
        print("test_thread_pool_with_exception {}s".format(test_end_time-test_start_time))
        self.assertGreater(5, threading.active_count())

    def test_thread_pool_get_all(self):
        def wait_delay():
            time.sleep(0.001)
            return threading.current_thread().name

        test_start_time = time.time()

        pool = threaders.ThreadPool(workers=30, collect_results=True)
        for _ in range(100):
            pool.put(wait_delay)

        pool.join()

        results = pool.get_all()

        self.assertEqual(len(results), 100)

        test_end_time = time.time()
        print("test_thread_pool_get_all {}s".format(test_end_time-test_start_time))
        self.assertGreater(5, threading.active_count())

    def test_dynamic_pool(self):
        def wait_delay():
            time.sleep(0.3)
            return threading.current_thread().name

        test_start_time = time.time()

        pool = threaders.DynamicPool(max_workers=10)
        for _ in range(20):
            pool.put(wait_delay)

        max_worker_validation = 0
        while len(pool.threads) > 0 or pool.tasks.qsize() > 0:
            workers = len(pool.threads)
            if workers > max_worker_validation:
                max_worker_validation = workers
        self.assertEqual(max_worker_validation, 10)

        pool.join()

        results = pool.gets()

        self.assertEqual(len(results), 20)

        test_end_time = time.time()
        print("test_dynamic_pool {}s".format(test_end_time-test_start_time))
        self.assertGreater(5, threading.active_count())

if __name__ == '__main__':
    unittest.main()
