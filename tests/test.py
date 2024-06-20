import unittest
from unittest.mock import patch
from main import Validate_Arguments, Parse_Arguments
from src.benchmark import Benchmark

class TestBenchmark(unittest.TestCase):
    def test_config(self):
        # Test case for valid arguments
        valid_args = [
            ('http://example.com', 10, 100, 10),
            ('https://example.com', 1, 1, 1)
        ]
        # Try valid arguments using Validate_Arguments from main.py.
        for address, qps, query_count, thread_count in valid_args:
            args = type('', (), {})()
            args.address = address
            args.qps = qps
            args.query_count = query_count
            args.thread_count = thread_count
            self.assertTrue(Validate_Arguments(args))
            print("Validation of valid arguments to the CLI")

        # Test cases for invalid arguments
        invalid_args = [
            ('example.com', 10, 100, 10),  # Invalid URL
            ('http://example.com', -1, 100, 10),  # Negative QPS
            ('http://example.com', 10, -100, 10),  # Negative query count
            ('http://example.com', 10, 100, -10)  # Negative thread count
        ]
        # Try invalid arguments using Validate_Arguments from main.py. It will already print out en error message.
        for address, qps, query_count, thread_count in invalid_args:
            args = type('', (), {})()
            args.address = address
            args.qps = qps
            args.query_count = query_count
            args.thread_count = thread_count
            self.assertFalse(Validate_Arguments(args))
            print("Validation of invalid arguments to the CLI")

    def test_benchmark(self):
        # Setup the arguments
        args = type('', (), {})()
        args.address = "http://example.com"
        args.qps = 2
        args.query_count = 5
        args.thread_count = 2

        # Initialize the Benchmark class
        benchmark = Benchmark(args)

        # Run the benchmark
        benchmark.run()
        # Validate the results
        self.assertGreater(len(benchmark.successful_latencies), 0)
        print("Validation of successful latency count is greater than 0")
        self.assertEqual(len(benchmark.all_latencies), args.query_count)
        print("Validation of all latencies are equal to the query count")
        self.assertEqual(benchmark.error_count + len(benchmark.successful_latencies), len(benchmark.all_latencies))
        print("Validation of test duratiion is almost equal to the (1 / qps) * query count")
        self.assertAlmostEqual(benchmark.test_duration, (1 / args.qps) * args.query_count, delta=0.1)
