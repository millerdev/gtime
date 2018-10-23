# usage:
#
# process: gunicorn/django
#   workon hq
#   gunicorn -c gtime/gconf.py --workers=2 --bind=localhost:8000 --log-level=debug gtime.wsgi
#
# process: client
#   workon gt
#   python client.py

from __future__ import print_function
import sys
from datetime import datetime

import grequests

url = "http://localhost:8080/ping/"
timeout = 5  # seconds
factor = 1.33

def main():
    concurrency = 20
    while True:
        print("request %s -> " % concurrency, end="")
        sys.stdout.flush()
        start = datetime.now()
        rs = grequests.map(
            (grequests.get(url, timeout=timeout) for x in range(concurrency)),
            exception_handler=exception_handler,
        )
        elapsed = datetime.now() - start
        failed = sum(1 for r in rs if r is None)
        print("%s responses%s in %s" % (
            sum(1 for r in rs if r is not None),
            ((" (%s failed)" % failed) if failed else ""),
            elapsed,
        ))
        if not failed:
            concurrency = int(concurrency * factor)
        elif failed > 2 and concurrency > 3:
            concurrency = int(concurrency / factor)

def exception_handler(request, err):
    etype = type(err).__name__
    if etype != "ReadTimeout":
        print("{}: {}".format(etype, err))

if __name__ == '__main__':
    main()
