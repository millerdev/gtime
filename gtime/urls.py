"""gtime URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import time
import random
import requests
from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponse

def index(request):
    return HttpResponse("ok")

def slow_ext(request):
    """Slow external request"""
    resp = requests.get("http://localhost:9999/")
    return HttpResponse(resp.content)

def slow_loc(request):
    """Delayed response"""
    time.sleep(3)
    return HttpResponse(str(random.randint(0, 1000)))

def slow_int(request):
    """Recursive request to /slow-loc"""
    resp = requests.get("http://localhost:8080/slow-loc")
    return HttpResponse(resp.content)

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^slow-int$', slow_int, name="slow_int"),
    url(r'^slow-ext$', slow_ext, name="slow_ext"),
    url(r'^slow-loc$', slow_loc, name="slow_loc"),
]
