"""
RSLab Django WSGI config for the lidiabrowser application.

It exposes the WSGI callable as a module-level variable named ``application``.

Since this Django-only setup does not use our default Cookiecutter workflow,
this root-level wsgi file is included to facilitate our deployment script.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

try:
    application = get_wsgi_application()
except Exception as e:
    # Ends up in Apache logs
    print(e)
