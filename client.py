# usage:
# python client.py

from __future__ import print_function
import sys
from datetime import datetime

import grequests

url = "http://localhost:8080/ping/"
concurrent_requests = 60
timeout = 5  # seconds

def main():
    while True:
        start = datetime.now()
        rs = grequests.map(
            (grequests.get(url, timeout=timeout) for x in range(concurrent_requests)),
            exception_handler=exception_handler,
        )
        elapsed = datetime.now() - start
        failed = sum(1 for r in rs if r is None)
        print("got %s responses%s in %s" % (
            sum(1 for r in rs if r is not None),
            ((" (%s failed)" % failed) if failed else ""),
            elapsed,
        ))

def exception_handler(request, err):
    etype = type(err).__name__
    if etype != "ReadTimeout":
        print("{}: {}".format(etype, err))

if __name__ == '__main__':
    main()
