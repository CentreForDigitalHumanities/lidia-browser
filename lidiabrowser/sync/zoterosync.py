from django.conf import settings
from django.db import transaction

import logging
from pyzotero import zotero
import yaml

from sync.models import Annotation, Publication, Sync
from lidia.models import Publication as LidiaPublication
from lidia.models import Annotation as LidiaAnnotation
from lidia.models import Language, ArticleTerm, LidiaTerm, Category

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
    if True or zotero_library_version > local_library_version:
        sync_publications(zot, since=local_library_version)
        sync_annotations(zot, since=local_library_version)
        update_local_library_version(zot, zotero_library_version)
        logger.info("Sync successful")
    else:
        logger.info("Local library up to date; not syncing")


def populate():
    for pub in Publication.objects.iterator():
        with transaction.atomic():
            zotero_id = pub.zotero_id
            attachment_url = pub.content.get('links', {}).get('attachment', {}).get('href', '')
            attachment_id = attachment_url.rstrip('/').split('/')[-1]
            data = pub.content.get('data', {})
            defaults = {
                'attachment_id': attachment_id,
                'title': data.get('title', ''),
                }
            publication, created = LidiaPublication.objects.get_or_create(
                zotero_id=zotero_id,
                # Only set fields if a new object is created
                defaults=defaults
            )
            if not created:
                publication.attachment_id = attachment_id
                publication.title = data.get('title', ''),
                # Just save all fields without checking which fields need updating
                publication.save()

    for annotation in Annotation.objects.iterator():
        with transaction.atomic():
            zotero_id = annotation.zotero_id
            data = annotation.content.get('data', {})
            annotation_comment = data.get('annotationComment', '')
            anno = annotation_comment.removeprefix('~~~~LIDIA~~~~')
            try:
                anno = yaml.safe_load(anno)
            except yaml.YAMLError as e:
                logger.error(f"YAMLError: {e}")
                continue

            arglang_obj, _ = Language.objects.get_or_create(code=anno.get('arglang', 'unspecified'))

            relation_to_id = anno.get('relation_to') or None
            if relation_to_id:
                # Create a placeholder annotation to reference
                relation_to_obj, _ = LidiaAnnotation.objects.get_or_create(zotero_id=relation_to_id)

            defaults = {
                'textselection': data.get('annotationText', ''),
                # Publication should exist so use foreign key column directly
                'parent_attachment_id': data.get('parentItem'),
                # "argname" fallback NULL for unique constraint
                'argname': anno.get('argname', None) or None,
                # "arglang" can be an empty string instead of 'unspecified'
                'arglang_id': anno.get('arglang', 'unspecified') or 'unspecified',
                'description': anno.get('description', ''),
                'argcont': anno.get('argcont', None) or None,
                'page_start': anno.get('page_start', None) or None,
                'page_end': anno.get('page_end', None) or None,
                'relation_type': anno.get('relation_type', '') or '',
                'relation_to_id': relation_to_id,
                }

            lidia_annotation, created = LidiaAnnotation.objects.get_or_create(
                zotero_id=zotero_id,
                defaults=defaults
            )
            if not created:
                for field, value in defaults.items():
                    setattr(lidia_annotation, field, value)
                lidia_annotation.save()
