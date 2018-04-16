import unittest
import threaders
import time


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


if __name__ == '__main__':
    unittest.main()
