"""
WSGI config for aminoProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""
# before:
# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aminoProject.settings")

# application = get_wsgi_application()

# Then, update your wsgi.py file to use dj-static:
# from django.core.wsgi import get_wsgi_application
# from dj_static import Cling
# application = Cling(get_wsgi_application())

# try:
import os

from django.core.wsgi import get_wsgi_application
from dj_static import Cling

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aminoProject.settings")

application = Cling(get_wsgi_application())
