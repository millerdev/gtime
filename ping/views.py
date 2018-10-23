# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import random

import requests

from django.http import HttpResponse


def index(request):
    resp = requests.get("http://localhost:8000/ping/svc/")
    return HttpResponse(resp.content)


def svc(request):
    time.sleep(3)
    return HttpResponse(str(random.randint(0, 1000)))
