"""
WSGI config for gtime project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gtime.settings")

application = get_wsgi_application()

# patch gevent
from gevent.monkey import patch_all
#from psycogreen.gevent import patch_psycopg

patch_all(subprocess=True)
#patch_psycopg()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
