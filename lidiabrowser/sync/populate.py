from typing import Optional
from django.db import transaction

import yaml
import logging

import sync.models as syncmodels
from sync.zoteroutils import get_attachment_url, get_attachment_id_from_url
from lidia.models import (
    Annotation,
    ArticleTerm,
    BaseAnnotation,
    Category,
    ContinuationAnnotation,
    Language,
    LidiaTerm,
    Publication,
    TermGroup,
)

logger = logging.getLogger(__name__)


LIDIAPREFIX = "~~~~LIDIA~~~~"


def process_continuation_annotations() -> None:
    # Get all annotations in order of presence in documents
    annotations = BaseAnnotation.objects.order_by(
        "parent_attachment", "sort_index"
    )
    current_parent = None
    current_first_annotation = None
    to_be_deleted = []
    for annotation in annotations:
        if hasattr(annotation, "annotation"):
            # Object is of Annotation model (first annotation)
            current_first_annotation = annotation.annotation  # type: ignore
            current_parent = annotation.parent_attachment
        elif hasattr(annotation, "continuationannotation"):
            # Object is of ContinuationAnnotation model
            if annotation.parent_attachment != current_parent:
                # This continuation annotation is the first annotation in
                # the current attachment. This should not be the case, so
                # delete it and give a warning.
                logger.warning(
                    f"Annotation {annotation} in {annotation.parent_attachment} "
                    "is a continuation annotation but there is no annotation "
                    "before it. This annotation will be absent from the database."
                )
                to_be_deleted.append(annotation)
                continue
            ca = annotation.continuationannotation  # type: ignore
            assert isinstance(ca, ContinuationAnnotation)
            ca.start_annotation = current_first_annotation
            ca.save()
    
    for annotation in to_be_deleted:
        annotation.delete()


def create_lidiaterm(lexiconterm: str, customterm: str) -> Optional[LidiaTerm]:
    if not lexiconterm:
        return None
    if lexiconterm == 'custom':
        if not customterm:
            return None
        vocab = 'custom'
        term = customterm
    else:
        vocab = 'lidia'
        term = lexiconterm
    lidiaterm, _ = LidiaTerm.objects.get_or_create(
        vocab=vocab,
        term=term
    )
    return lidiaterm


def create_term_group(annotation: Annotation, index: int, data: dict) -> TermGroup:
    articleterm_str = data.get("articleterm", None) or None
    if articleterm_str:
        articleterm, _ = ArticleTerm.objects.get_or_create(term=articleterm_str)
    else:
        articleterm = None
    category_str = data.get("category", None) or None
    if category_str == 'custom':
        category_str = data.get("customcategory", None)
    if category_str:
        category, _ = Category.objects.get_or_create(category=category_str)
    else:
        category = None
    lidiaterm = create_lidiaterm(
        data.get("lexiconterm", ""),
        data.get("customterm", "")
    )
    
    defaults = {
        "termtype": data.get("termtype", None) or None,
        "articleterm": articleterm,
        "category": category,
        "lidiaterm": lidiaterm,
    }
    termgroup, created = TermGroup.objects.get_or_create(
        annotation=annotation,
        index=index,
        defaults=defaults
    )
    if not created:
        for field, value in defaults.items():
            setattr(termgroup, field, value)
        termgroup.save()

    return termgroup


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
            publication, created = Publication.objects.get_or_create(
                zotero_publication_id=zotero_id,
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

            lidia_id = anno.get("lidiaId") or zotero_id
            defaults = {
                'zotero_annotation': annotation,
                'textselection': data.get('annotationText', ''),
                # Publication should exist so use foreign key column directly
                'parent_attachment_id': data.get('parentItem'),
                'sort_index': data.get("annotationSortIndex"),
            }
            argcont = anno.get('argcont')
            if argcont:
                ContinuationAnnotation.objects.get_or_create(
                    lidia_id=lidia_id,
                    defaults=defaults
                )
            else:
                arglang_id = anno.get('arglang', 'unspecified') or 'unspecified'
                Language.objects.get_or_create(code=arglang_id)

                relation_to_id = anno.get('relationTo') or None
                relation_to_obj = None
                if relation_to_id:
                    # Create a placeholder annotation to reference
                    relation_to_obj, _ = Annotation.objects.get_or_create(lidia_id=relation_to_id)

                defaults |= {
                    'argname': anno.get('argname', '') or '',
                    'arglang_id': arglang_id,
                    'description': anno.get('description', ''),
                    'page_start': anno.get('pagestart', None) or None,
                    'page_end': anno.get('pageend', None) or None,
                    'relation_type': anno.get('relationType', '') or '',
                    'relation_to': relation_to_obj,
                }

                lidia_annotation, created = Annotation.objects.get_or_create(
                    lidia_id=lidia_id,
                    defaults=defaults
                )
                if not created:
                    for field, value in defaults.items():
                        setattr(lidia_annotation, field, value)
                    lidia_annotation.save()

                termgroupdata = anno.get('termgroups', [])
                if termgroupdata is None:
                    termgroupdata = []
                for index, data in enumerate(termgroupdata):
                    termgroup = create_term_group(lidia_annotation, index, data)
                    termgroup.save()

    process_continuation_annotations()

    remaining_placeholders = Annotation.objects.filter(
        zotero_annotation__isnull=True
    )
    count = remaining_placeholders.count()
    if count:
        logger.warning(
            f"There were references to {count} non-existing annotation(s)."
        )
        # TODO: include a warning in the annotations having invalid references
        remaining_placeholders.delete()

