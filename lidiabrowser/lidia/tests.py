import pytest
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command


@pytest.mark.django_db
class TestInitgroups:
    def test_basic(self):
        call_command("initgroups")
        view_all = Group.objects.get(name="view_all")
        viewpublicationpermission = Permission.objects.get_by_natural_key(
            "view_publication", "lidia", "publication"
        )
        assert view_all.permissions.contains(viewpublicationpermission)

    def test_double(self):
        # Calling twice on the same database should be fine
        call_command("initgroups")
        call_command("initgroups")
