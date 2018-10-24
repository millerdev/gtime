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
    parser.add_argument("-n", "--limit", default=20, type=int,
        help="Limit the number of batches to send [20]")
    args = parser.parse_args()
    stats = []

    try:
        run(args.url, args.timeout, args.limit, stats)
    except KeyboardInterrupt:
        pass
    if stats:
        avg = sum(iter(stats)) / float(len(stats))
        print("average success: {:.2f}".format(avg))

def run(url, timeout, limit, stats):
    def exception_handler(request, err):
        add_error(type(err).__name__)

    def add_error(name):
        try:
            record = errors[name]
        except KeyError:
            record = errors[name] = {"name": name, "count": 0}
        record["count"] += 1

    i = 0
    adj = 0
    concurrency = 32
    while i < limit:
        i += 1
        errors = new_errors()
        start = datetime.now()
        print(
            "{} {} request {} -> ".format(i, start, concurrency),
            end="",
            flush=1,
        )
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
        stats.append(success)
        if failed:
            adj = max(int(failed / 2.), 1)
            if adj >= concurrency:
                adj = concurrency - 1
            concurrency -= adj
            fail_msg = " (-{}: {})".format(adj, " ".join(
                "{name}={count}".format(**err)
                for err in sorted(errors.values(), key=itemgetter("name"))
                if err["count"]
            ))
        else:
            if adj:
                fail_msg = " (+{})".format(adj)
                concurrency += adj
                adj *= 2
            else:
                fail_msg = " (+{})".format(concurrency)
                concurrency *= 2
        print("{} responses in {}{}".format(success, elapsed, fail_msg))

def new_errors():
    return {
        "ReadTimeout": {"name": "time", "count": 0},
        "ConnectionError": {"name": "conn", "count": 0},
    }

if __name__ == '__main__':
    main()
