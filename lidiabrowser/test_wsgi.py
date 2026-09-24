import runpy
from pathlib import Path
from unittest.mock import Mock

import pytest
from django.core import wsgi
from django.core.exceptions import ImproperlyConfigured


def test_wsgi_propagates_startup_failure(monkeypatch):
    failure = ImproperlyConfigured("invalid application configuration")
    monkeypatch.setattr(wsgi, "get_wsgi_application", Mock(side_effect=failure))

    with pytest.raises(ImproperlyConfigured, match="invalid application configuration") as exc_info:
        runpy.run_path(str(Path(__file__).with_name("wsgi.py")))

    assert exc_info.value is failure
