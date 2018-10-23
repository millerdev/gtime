"""Load testing client for HTTP servers

process: slow random service
    workon gt
    gunicorn -b localhost:9999 --worker-class=gevent --log-level=debug slowrand

process: gunicorn/django
    workon hq
    gunicorn -b localhost:8000 -c gtime/gconf.py --log-level=debug gtime.wsgi

process: client
    workon gt
    python client.py
"""

from __future__ import print_function
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime

import grequests

URL = "http://localhost:8080/slow-num"
factor = 1.33

def main():
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument("-s", "--server-url", default=URL,
        help="Server URL [%s]" % URL)
    parser.add_argument("-t", "--timeout", default=5, type=int,
        help="Timeout in seconds [5]")
    args = parser.parse_args()
    url = args.server_url
    timeout = args.timeout

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
        elif failed > concurrency / 10 and concurrency > 3:
            concurrency = int(concurrency / factor)

def exception_handler(request, err):
    etype = type(err).__name__
    if etype != "ReadTimeout":
        print("{}: {}".format(etype, err))

if __name__ == '__main__':
    main()
