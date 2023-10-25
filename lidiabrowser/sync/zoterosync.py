from django.conf import settings

import logging
import yaml
from pyzotero import zotero

from sync.models import Annotation, Publication, Sync

logger = logging.getLogger(__name__)


def get_zotero_instance() -> zotero.Zotero:
    return zotero.Zotero(
        settings.ZOTERO_LIBRARY_ID,
        settings.ZOTERO_LIBRARY_TYPE,
        settings.ZOTERO_API_KEY,
        preserve_json_order=True
    )


def sync_publications(zot: zotero.Zotero, since: int):
    """ Fetches publications which have been updated since the given library version.
    Saves the publications to database.
    """
    # All publications should be placed top-level (not in collections)
    # Non-publication items might exist as well but can be ignored.
    # (There's no way to filter on bibliographic items in general directly?)
    items = zot.everything(zot.top(since=since))
    if items:
        for item in items:
            key = item['key']
            obj = item
            # Annotations are linked to their parent PDF, not the bibliographic
            # item
            # Assuming only one attachment per publication
            url: str = obj.get("links", {}).get("attachment", {}).get("href")
            attachment_id: str = url.rstrip('/').split('/')[-1] if url else ''
            publication, _ = Publication.objects.get_or_create(
                zotero_id=key
            )
            publication.content = obj
            publication.attachment_id = attachment_id
            publication.save()
        logging.info(f"Updated {len(items)} publications")
    else:
        logging.info("No new publications found")


def sync_annotations(zot: zotero.Zotero, since: int):
    """ Fetches items of type 'annotation' which have been updated since the given 
    library version.
    Saves the annotations to database.
    """
    # TODO: use Zotero.follow() or iterfollow() methods
    # https://pyzotero.readthedocs.io/en/latest/#the-follow-and-everything-methods
    items = zot.everything(zot.items(itemType='annotation', since=since))
    if items:
        for item in items:
            key = item['key']
            comment = item['data']['annotationComment']
            comment = comment.removeprefix('~~~~LIDIA~~~~')
            try:
                comment_dict = yaml.safe_load(comment)
            except yaml.YAMLError as e:
                logger.error(
                    f"YAMLError in annotation with key {key}: {e}. Ignoring."
                )
                continue
            if comment_dict is None:
                # This happens if comment is an empty string
                comment_dict = {}
            annotation, _ = Annotation.objects.get_or_create(
                zotero_id=key
            )
            annotation.content = item
            annotation.comment = comment_dict
            annotation.save()
        logging.info(f"Updated {len(items)} annotations")
    else:
        logging.info("No new annotations found")


def get_local_library_version(zot: zotero.Zotero):
    """ Returns the last synced library version from the local database.
    """
    local_library_version = None
    try:
        sync = Sync.objects.get(library_id=zot.library_id)
    except Sync.DoesNotExist:
        # Return -1 if local library version is not available
        # (this happens if the library is synchronized for the first time)
        local_library_version = -1
    else:
        local_library_version = sync.library_version
    logger.info(f"local_library_version: {local_library_version}")
    return local_library_version


def update_local_library_version(zot: zotero.Zotero, version: int):
    if not isinstance(version, int):
        raise ValueError("version argument should be of type int")
    library_id = zot.library_id
    sync, _ = Sync.objects.get_or_create(
        library_id=library_id,
        defaults={
            "library_version": version
        }
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
    if zotero_library_version > local_library_version:
        sync_publications(zot, since=local_library_version)
        sync_annotations(zot, since=local_library_version)
        update_local_library_version(zot, zotero_library_version)
        logger.info("Sync successful")
    else:
        logger.info("Local library up to date")

