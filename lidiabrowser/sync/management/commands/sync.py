from django.core.management.base import BaseCommand, CommandParser

from sync.zoterosync import sync
from sync.models import delete_all


class Command(BaseCommand):
    help = "Synchronize with data on the Zotero server"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--refresh",
            action="store_true",
            help="First remove sync information from database to solve any sync problems"
        )

    def handle(self, *args, **options):
        if options["refresh"]:
            delete_all()
        sync()
