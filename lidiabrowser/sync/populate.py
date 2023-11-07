from django.db import transaction

import yaml
import logging

import sync.models as syncmodels
from sync.zoteroutils import get_attachment_url, get_attachment_id_from_url
from lidia.models import Publication as LidiaPublication
from lidia.models import Annotation as LidiaAnnotation
from lidia.models import Language  #, ArticleTerm, LidiaTerm, Category

logger = logging.getLogger(__name__)


LIDIAPREFIX = "~~~~LIDIA~~~~"


def populate():
    for pub in syncmodels.Publication.objects.iterator():
        with transaction.atomic():
            zotero_id = pub.zotero_id
            attachment_url = get_attachment_url(pub.content)
            attachment_id = get_attachment_id_from_url(attachment_url)
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
                publication.title = data.get('title', '')
                # Just save all fields without checking which fields need updating
                publication.save()

    for annotation in syncmodels.Annotation.objects.iterator():
        with transaction.atomic():
            zotero_id = annotation.zotero_id
            data = annotation.content.get('data', {})
            annotation_comment = data.get('annotationComment', '')
            if not annotation_comment.startswith(LIDIAPREFIX):
                logger.info(
                    f"Ignoring annotation with key {zotero_id}: not a LIDIA annotation"
                )
                continue
            yamlstr = annotation_comment.removeprefix(LIDIAPREFIX)
            try:
                anno = yaml.safe_load(yamlstr)
            except yaml.YAMLError as e:
                logger.error(f"YAMLError: {e}")
                continue

            arglang_obj, _ = Language.objects.get_or_create(code=anno.get('arglang', 'unspecified'))

            relation_to_id = anno.get('relationTo') or None
            if relation_to_id:
                # Create a placeholder annotation to reference
                relation_to_obj, _ = LidiaAnnotation.objects.get_or_create(zotero_id=relation_to_id)

            defaults = {
                'textselection': data.get('annotationText', ''),
                # Publication should exist so use foreign key column directly
                'parent_attachment_id': data.get('parentItem'),
                'argname': anno.get('argname', '') or '',
                # "arglang" can be an empty string instead of 'unspecified'
                'arglang_id': anno.get('arglang', 'unspecified') or 'unspecified',
                'description': anno.get('description', ''),
                'argcont': anno.get('argcont', None) or None,
                'page_start': anno.get('pagestart', None) or None,
                'page_end': anno.get('pageend', None) or None,
                'relation_type': anno.get('relationType', '') or '',
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
