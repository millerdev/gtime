"""Random number service with delayed response"""
import random
import time


def application(environ, start_response):
    time.sleep(3)
    start_response('200 OK', [('Content-Type', 'text/html')])
    yield str(random.randint(0, 1000)).encode('utf-8')
