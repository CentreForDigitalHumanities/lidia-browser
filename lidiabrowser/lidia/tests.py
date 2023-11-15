import pytest
from django.contrib.auth.models import Group, Permission

from lidiabrowser.init import initiate_groups


@pytest.mark.django_db
class TestInitgroups:
    def test_basic(self):
        groups = initiate_groups()
        assert isinstance(groups["view_all"], Group)
        view_all = Group.objects.get(name="view_all")
        viewpublicationpermission = Permission.objects.get_by_natural_key(
            "view_publication", "lidia", "publication"
        )
        assert view_all.permissions.contains(viewpublicationpermission)

    def test_double(self):
        # Calling twice on the same database should be fine
        initiate_groups()
        initiate_groups()
