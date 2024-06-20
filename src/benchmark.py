import requests
import time
import threading
import statistics
from queue import Queue

class Benchmark:
    def __init__(self, args):
        self.args = args               # Maintain CLI arguments from user
        self.successful_latencies = [] # Keep track of successful latencies
        self.all_latencies = []        # Keep track of all latencies
        self.error_count = 0           # Keep track of the number of errors
        self.status_counts = {}        # Keep track of each HTTP return status and their counts
        self.queue = Queue()           # Queue generates work signals to thread pool
        self.lock = threading.Lock()   # Initialize mutex for race condition avoidance
        self.query_counter = 0         # Keep track of the number of queries sent via worker threads
        self.test_duration = 0         # Amount of time the test took
        # Timeout value must be sufficiently low to ensure correct qps. Multiplying with 0.9 is for error margin
        self.http_timeout = self.args.thread_count * (1/self.args.qps) * 0.9      
        self.sleep_duration = self.calculate_sleep_duration()
        self.construct_thread_pool()

    # Measure average overhead latency and calculate appropriate sleep duration to achieve fps
    def calculate_sleep_duration(self):
        N = 1000
        tmp_queue = Queue()
        tmp_counter = 0
        start_time = time.time()    
        for i in range(N):
            tmp_counter += 1
            tmp_queue.put(None)
        end_time = time.time()
        overhead_latency = (end_time - start_time) / N
        return (1 / self.args.qps) - overhead_latency

    # Create a pool of workers that wait to get a signal from the queue. 
    # When program finishes, threads will be deleted due to daemon flag
    def construct_thread_pool(self):        
        for i in range(self.args.thread_count):
            thread = threading.Thread(target=self._thread_task)
            thread.daemon = True 
            thread.start()  

    # Makes an HTTP GET query and measures latency and error. Uses mutex for thread safety
    def _make_query(self):
        start_time = time.time()
        try:
            response = requests.request(
                method="GET",
                url=self.args.address,
                headers="",
                data="",
                timeout=self.http_timeout
            )
            latency = time.time() - start_time
            with self.lock:
                self.successful_latencies.append(latency)
                self.all_latencies.append(latency)
                if response.status_code not in self.status_counts:
                    self.status_counts[response.status_code] = 0
                self.status_counts[response.status_code] += 1                
        except requests.RequestException as e:
            with self.lock:
                self.all_latencies.append(time.time() - start_time)
                self.error_count += 1

    # Task run on each worker thread. Waits for a signal from queue, makes HTTP request, marks task as done
    def _thread_task(self):
        while True:
            self.queue.get()
            self._make_query()
            self.queue.task_done()
    
    # Executes query_count number of queries through worker threads while achieving qps frequency
    def run(self):
        start_time = time.time()        
        while self.query_counter < self.args.query_count:
            self.query_counter += 1          # Increment query count
            self.queue.put(None)             # Signal worker thread to start query
            time.sleep(self.sleep_duration)  # Sleep appropriate duration to achieve qps
        self.queue.join()                    # Wait for query_count of queries to be fully processed
        self.test_duration = time.time() - start_time

    # Print a summary of configs, measurements, and results
    def print_results(self):
        print("Configs:")
        print(f"- Target QPS: {self.args.qps}")
        print(f"- Query Count: {self.args.query_count}")
        print(f"- Thread Count: {self.args.thread_count}")
        print(f"- HTTP timeout: {self.http_timeout} seconds")        

        print("Measurements:")
        print(f"- Test duration: {self.test_duration:.2f} seconds")
        print(f"- Achieved QPS: {(self.args.query_count / self.test_duration):.2f}")
        print("Latency (Successful):")
        if len(self.successful_latencies) >= 1:
            print(f"- Average: {statistics.mean(self.successful_latencies):.4f} seconds")
            print(f"- Median: {statistics.median(self.successful_latencies):.4f} seconds")
        else:
            print(f"- Average: N/A due to insufficient data points")
            print(f"- Median: N/A due to insufficient data points")
        if len(self.successful_latencies) >= 2:
            print(f"- Std. Dev.: {statistics.stdev(self.successful_latencies):.4f} seconds")
        else:
            print(f"- Std. Dev.: N/A due to insufficient data points")
        print("Latency (Total):")
        print(f"- Average: {statistics.mean(self.all_latencies):.4f} seconds")
        print(f"- Median: {statistics.median(self.all_latencies):.4f} seconds")
        if len(self.all_latencies) >= 2:
            print(f"- Std. Dev.: {statistics.stdev(self.all_latencies):.4f} seconds")
        else:
            print(f"- Std. Dev.: N/A due to insufficient data points")
        print("Error Rate (error / total queries):")
        print(f"- Count: {self.error_count} / {self.args.query_count}")
        print(f"- Percentage: {self.error_count/self.args.query_count*100:.2f}%")

        print("Status Code Counts:")
        for status_code, count in self.status_counts.items():
            print(f"- {status_code}: {count}")