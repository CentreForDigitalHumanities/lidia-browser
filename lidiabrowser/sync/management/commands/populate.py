from django.core.management.base import BaseCommand

from sync.zoterosync import populate


class Command(BaseCommand):
    help = "Parse raw sync content and populate LIDIA models"

    def handle(self, *args, **options):
        populate()
