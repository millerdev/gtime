# Benchmarking scripts for slow gunicorn servers

Virtualenv setup using Python 3.7
```
mkvirtualenv gt
pip install -r requires.txt
```

Process: slow random service
```
workon gt
gunicorn -b localhost:9999 --worker-class=gevent --log-level=debug slowrand
```

Process: gunicorn/django

Note: `hq` is commcarehq virtualenv (Python 2.7.15 gevent 1.2.2
```
workon hq  # or workon gt
gunicorn -b localhost:8000 -c gtime/gconf.py --log-level=debug gtime.wsgi
```

Process: nginx proxy port 8080 -> 8000

Process: client
```
workon gt
python client.py http://localhost:9999/
python client.py http://localhost:8080/
python client.py http://localhost:8080/slow-loc
python client.py http://localhost:8080/slow-ext
```
