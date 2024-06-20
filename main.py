import argparse 
import validators
from src.benchmark import Benchmark

# Fetch CLI arguments of HTTP address, qps, query count, and thread count from the user
def Parse_Arguments():
    parser = argparse.ArgumentParser(description="HTTP Benchmarking tool that measures latency and error rate.")
    parser.add_argument('address', type=str, help='HTTP address to run the benchmark on.')
    parser.add_argument('--qps', type=float, required=True, help='Queries per second.')
    parser.add_argument('--query_count', type=int, default='128', help='Total number of queries to send.')
    parser.add_argument('--thread_count', type=int, default='8', help='Number of threads to be used.')
    return parser.parse_args()

# Validate CLI arguments. Checks that the provided URL is valid, and that the other values are positive
def Validate_Arguments(args):
    address_check = validators.url(args.address)
    qps_check = (args.qps > 0)
    querry_count_check = (args.query_count > 0)
    thread_count_check = (args.thread_count > 0)

    validation_check = address_check and qps_check and querry_count_check and thread_count_check

    if not validation_check:
        print("Validation check failed for CLI arguments. Please ensure that you provide a valid HTTP address, and that the other values are positive.")

    return validation_check

# Parses and validates CLI arguments. Runs benchmarking and displays results.
def main():
    args = Parse_Arguments()
    if not Validate_Arguments(args):
        exit()
    benchmark = Benchmark(args)
    benchmark.run()
    benchmark.print_results()

if __name__ == "__main__":
    main()



