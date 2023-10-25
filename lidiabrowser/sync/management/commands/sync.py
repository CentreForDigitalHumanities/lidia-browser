from django.core.management.base import BaseCommand, CommandError

from sync.zoterosync import sync


class Command(BaseCommand):
    help = "Synchronize with data on the Zotero server"

    def handle(self, *args, **options):
        sync()
