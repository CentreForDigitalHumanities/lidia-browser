from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Create user groups that allow viewing all or restricted "\
        "annotation data"

    def handle(self, *args, **options):
        # For now, only create a 'view all' group - no distinction yet
        # between all or restricted access
        view_all, _ = Group.objects.get_or_create(name="view_all")
        models = [
            'publication', 'language', 'annotation', 'articleterm',
            'lidiaterm', 'category', 'termgroup'
        ]
        permissions = []
        for model in models:
            permissions.append(Permission.objects.get_by_natural_key(
                "view_" + model, "lidia", model
            ))
        view_all.permissions.add(*permissions)
