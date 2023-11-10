from django.conf import settings

import logging
from pyzotero import zotero

from sync.models import Annotation, Publication, Sync

logger = logging.getLogger(__name__)


def get_zotero_instance() -> zotero.Zotero:
    return zotero.Zotero(
        settings.ZOTERO_LIBRARY_ID,
        settings.ZOTERO_LIBRARY_TYPE,
        settings.ZOTERO_API_KEY,
        preserve_json_order=True,
    )


def sync_publications(zot: zotero.Zotero, since: int):
    """Fetches publications which have been updated since the given library version.
    Saves the publications to database.
    """
    # All publications should be placed top-level (not in collections)
    # Non-publication items might exist as well but can be ignored.
    # (There's no way to filter on bibliographic items in general directly?)
    items = zot.everything(zot.top(since=since))
    n_created = 0
    n_updated = 0
    for item in items:
        key = item["key"]
        obj = item
        # Annotations are linked to their parent PDF, not the bibliographic
        # item
        # Assuming only one attachment per publication
        publication, created = Publication.objects.get_or_create(zotero_id=key)
        publication.content = obj
        publication.save()
        if created:
            n_created += 1
        else:
            n_updated += 1
    logging.info(
        f"Updated {n_updated} publications; added {n_created} new publications."
    )


def sync_annotations(zot: zotero.Zotero, since: int):
    """Fetches items of type 'annotation' which have been updated since the given
    library version.
    Saves the annotations to database.
    """
    # TODO: use Zotero.follow() or iterfollow() methods
    # https://pyzotero.readthedocs.io/en/latest/#the-follow-and-everything-methods
    items = zot.everything(zot.items(itemType="annotation", since=since))
    n_created = 0
    n_updated = 0
    for item in items:
        key = item["key"]
        annotation, created = Annotation.objects.get_or_create(zotero_id=key)
        annotation.content = item
        annotation.save()
        if created:
            n_created += 1
        else:
            n_updated += 1
    logging.info(f"Updated {n_updated} annotations; added {n_created} new annotations.")


def get_local_library_version(zot: zotero.Zotero):
    """Returns the last synced library version from the local database."""
    local_library_version = None
    try:
        sync = Sync.objects.get(library_id=zot.library_id)
    except Sync.DoesNotExist:
        # Return -1 if local library version is not available
        # (this happens if the library is synchronized for the first time)
        local_library_version = -1
    else:
        local_library_version = sync.library_version
    return local_library_version


def update_local_library_version(zot: zotero.Zotero, version: int):
    if not isinstance(version, int):
        raise ValueError("version argument should be of type int")
    library_id = zot.library_id
    sync, _ = Sync.objects.get_or_create(
        library_id=library_id, defaults={"library_version": version}
    )
    sync.library_version = version
    sync.save()


def sync() -> None:
    """
    Synchronize with data on the Zotero server.
    """
    zot = get_zotero_instance()
    zotero_library_version = zot.last_modified_version()
    local_library_version = get_local_library_version(zot)
    logger.info(f"Remote library version: {zotero_library_version}.")
    if local_library_version == -1:
        logger.info("Local library not present.")
    else:
        logger.info(f"Local library version: {local_library_version}.")
    if zotero_library_version > local_library_version:
        sync_publications(zot, since=local_library_version)
        sync_annotations(zot, since=local_library_version)
        update_local_library_version(zot, zotero_library_version)
        logger.info("Sync successful")
    else:
        logger.info("Local library up to date; not syncing")


