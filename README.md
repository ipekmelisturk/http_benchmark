# http_benchmark
A benchmark API to test the latency performance and error rate of HTTP addresses.

## To build the docker file use the command:
     _docker build -t http_benchmark ._ 
     
## To run the benchmark use the command(This is an example input you can change qps, query_count, thread_count):
      _docker run http_benchmark python3 main.py http://example.com --qps 50 --query_count 150  --thread_count 8_ 
      
## To run the tests use the command:
      _docker run http_benchmark python3 -m unittest tests/test.py_ 
