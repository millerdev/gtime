"""Load testing client for HTTP servers

process: slow random service
    workon gt
    gunicorn -b localhost:9999 --worker-class=gevent --log-level=debug slowrand

process: gunicorn/django
    workon hq  # or workon gt
    gunicorn -b localhost:8000 -c gtime/gconf.py --log-level=debug gtime.wsgi

process: nginx proxy port 8080 -> 8000

process: client
    workon gt
    python client.py http://localhost:9999/
    python client.py http://localhost:8080/
    python client.py http://localhost:8080/slow-loc
    python client.py http://localhost:8080/slow-ext
"""

from __future__ import print_function
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
from operator import itemgetter

import grequests
import requests

def main():
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument("url", help="Server URL")
    parser.add_argument("-t", "--timeout", default=5, type=int,
        help="Timeout in seconds [5]")
    args = parser.parse_args()
    url = args.url
    timeout = args.timeout

    def exception_handler(request, err):
        add_error(type(err).__name__)

    def add_error(name):
        try:
            record = errors[name]
        except KeyError:
            record = errors[name] = {"name": name, "count": 0}
        record["count"] += 1

    adj = 0
    concurrency = 32
    while True:
        errors = new_errors()
        start = datetime.now()
        print("{} request {} -> ".format(start, concurrency), end="", flush=1)
        rs = grequests.map(
            (grequests.get(url, timeout=timeout) for x in range(concurrency)),
            exception_handler=exception_handler,
        )
        elapsed = datetime.now() - start
        success = 0
        failed = 0
        for resp in rs:
            if resp is None:
                failed += 1
                continue
            if resp.status_code != requests.codes.ok:
                failed += 1
                add_error(str(resp.status_code))
            else:
                success += 1
            resp.close()
        if failed:
            fail_msg = " ({})".format(" ".join(
                "{name}={count}".format(**err)
                for err in sorted(errors.values(), key=itemgetter("name"))
                if err["count"]
            ))
        else:
            fail_msg = ""
        print("{} responses in {}{}".format(success, elapsed, fail_msg))
        if not failed:
            if adj:
                concurrency += adj
                adj *= 2
            else:
                concurrency *= 2
        else:
            adj = max(int(failed / 2.), 1)
            concurrency -= adj
            if concurrency < 1:
                concurrency = 1
                adj = 0

def new_errors():
    return {
        "ReadTimeout": {"name": "time", "count": 0},
        "ConnectionError": {"name": "conn", "count": 0},
    }

if __name__ == '__main__':
    main()
