import pytest
from django.contrib.auth.models import Group, Permission

from lidiabrowser.init import initiate_groups
import lidia.models as models


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


@pytest.mark.django_db
class TestLanguage:
    def test_save(self):
        language = models.Language(code="nld")
        language.save()
        assert language.name == "Dutch"

    def test_save_emptylanguage(self):
        language = models.Language(code="")
        language.save()
        assert not language.name

    def test_save_nonexistinglanguage(self):
        language = models.Language(code="nonexisting")
        language.save()
        assert not language.name


@pytest.mark.django_db
class TestBaseAnnotation:
    def test_page_number_in_pdf(self):
        baseannot = models.BaseAnnotation(
            sort_index="00024|000002|00069"
        )
        assert baseannot.page_number_in_pdf == 25

    def test_page_number_in_pdf_empty(self):
        baseannot = models.BaseAnnotation()
        assert baseannot.page_number_in_pdf is None


@pytest.mark.django_db
class TestAnnotation:
    def test_page_range_in_pdf_nocont(self):
        annot = models.Annotation(
            sort_index="00024|000002|00069"
        )
        annot.save()
        assert annot.page_range_in_pdf == "25"

    def test_page_range_in_pdf_cont(self):
        annot = models.Annotation(
            sort_index="00024|000002|00069"
        )
        annot.save()
        cont = models.ContinuationAnnotation(
            sort_index="00026|000004|00099"
        )
        cont.start_annotation = annot
        cont.save()
        assert annot.page_range_in_pdf == "25–27"

