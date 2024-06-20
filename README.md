# http_benchmark
A benchmark API to test the latency performance and error rate of HTTP addresses.

## To build the docker file use the command:
     docker build -t http_benchmark . 
     
## To run the benchmark use the command(This is an example input you can change qps, query_count, thread_count):
      docker run http_benchmark python3 main.py http://example.com --qps 50 --query_count 150  --thread_count 8
      
## To run the tests use the command:
      docker run http_benchmark python3 -m unittest tests/test.py 
