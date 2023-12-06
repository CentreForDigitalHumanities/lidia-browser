from django.core.management.base import BaseCommand, CommandParser

from sync.populate import populate
from lidia.models import delete_all


class Command(BaseCommand):
    help = "Parse raw sync content and populate LIDIA models"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--refresh",
            action="store_true",
            help="First remove annotations from database to solve any sync problems"
        )

    def handle(self, *args, **options):
        if options["refresh"]:
            delete_all()
        populate()
