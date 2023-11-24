from typing import Optional
from django.db import models
from django.contrib import admin

import iso639

import sync.models as syncmodels


class Publication(models.Model):
    zotero_publication = models.OneToOneField(syncmodels.Publication, verbose_name="Zotero publication", on_delete=models.CASCADE, to_field="zotero_id", null=True)
    attachment_id = models.CharField(max_length=16, unique=True, null=True)
    title = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.title or self.zotero_publication


class Language(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name or self.code

    def save(self, *args, **kwargs):
        if not self.name:
            try:
                self.name = iso639.Lang(self.code).name
            except (
                iso639.exceptions.DeprecatedLanguageValue,
                iso639.exceptions.InvalidLanguageValue
            ):
                pass
        return super().save(*args, **kwargs)


class BaseAnnotation(models.Model):
    lidia_id = models.CharField(verbose_name="LIDIA ID", max_length=100, unique=True, null=True)
    # Allow nullable zotero_annotation to facilitate placeholders
    zotero_annotation = models.OneToOneField(syncmodels.Annotation, verbose_name="Zotero annotation", on_delete=models.CASCADE, null=True, to_field="zotero_id")
    parent_attachment = models.ForeignKey(Publication, verbose_name="publication", on_delete=models.CASCADE, to_field='attachment_id', blank=True, null=True)
    textselection = models.TextField(default='')
    sort_index = models.CharField(max_length=100, help_text="Index to keep order of annotation in document", default="")

    @property
    def page_number_in_pdf(self) -> Optional[int]:
        # Extract page number from sort index, which is the first part before
        # |, and which starts with zero
        if self.sort_index:
            try:
                return int(self.sort_index.split("|")[0]) + 1
            except ValueError:
                return None


class Annotation(BaseAnnotation):
    RELATION_TYPE_CHOICES = [
        ("", "none"),
        ("contradicts", "contradicts"),
        ("generalizes", "generalizes"),
        ("invalidates", "invalidates"),
        ("specialcase", "is a special case of"),
        ("supports", "supports"),
    ]
    
    argname = models.CharField(verbose_name="argument name", max_length=100, default='')
    arglang = models.ForeignKey(Language, verbose_name="subject language", on_delete=models.SET_NULL, to_field='code', null=True)
    description = models.TextField(default='')
    page_start = models.CharField(verbose_name="start page", max_length=16, null=True)
    page_end = models.CharField(verbose_name="end page", max_length=16, null=True)
    relation_type = models.CharField(max_length=11, choices=RELATION_TYPE_CHOICES, default='')
    relation_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)

    # Type definitions for related managers
    termgroups: models.Manager["TermGroup"]
    continuation_annotations: models.Manager["ContinuationAnnotation"]

    def __str__(self):
        return self.argname or self.lidia_id or self.zotero_annotation or "(no name or ID)"

    @property
    @admin.display(ordering="page_start")
    def page_range(self):
        return f"{self.page_start}–{self.page_end}"

    @property
    @admin.display(description="Page range in PDF")
    def page_range_in_pdf(self) -> Optional[str]:
        if self.page_number_in_pdf is None:
            return None
        begin = end = str(self.page_number_in_pdf)
        # Get continuation annotation with the highest sort index, which will
        # be the one with the highest page number. Ignore continuation
        # annotation if the model was not saved.
        if self.pk and (last_cont := \
                self.continuation_annotations.order_by("-sort_index").first()):
            end = last_cont.page_number_in_pdf
        if end != begin:
            return f"{begin}–{end}"
        else:
            return begin


    @property
    @admin.display(description="Terms")
    def summary_of_term_groups(self):
        return ", ".join([str(x) for x in self.termgroups.all()])

    @property
    @admin.display(description="Quotation")
    def full_quotation(self):
        cont = self.continuation_annotations.order_by("sort_index")
        quotation = self.textselection
        quotation += ''.join(["\n" + x.textselection for x in cont])
        return quotation

    @property
    @admin.display(description="Zotero annotation IDs")
    def all_zotero_ids(self) -> str:
        ids = [self.zotero_annotation_id]
        ids.extend([
            x.zotero_annotation_id for x
            in self.continuation_annotations.order_by("sort_index")
        ])
        return ", ".join(ids)


class ContinuationAnnotation(BaseAnnotation):
    start_annotation = models.ForeignKey(Annotation, on_delete=models.SET_NULL, null=True, related_name="continuation_annotations")

    def __str__(self):
        if self.start_annotation:
            return f"(continuation of {self.start_annotation})"
        else:
            return "(orphaned continuation annotation)"


class ArticleTerm(models.Model):
    term = models.CharField("article term", max_length=100, unique=True)

    def __str__(self):
        return self.term


class LidiaTerm(models.Model):
    VOCAB_CHOICES = [
        ('lol', 'Lexicon of Linguistics'),
        ('custom', 'custom'),
    ]

    vocab = models.CharField("vocabulary", max_length=6, choices=VOCAB_CHOICES)
    term = models.CharField("LIDIA term", max_length=100)

    class Meta:
        unique_together = [['vocab', 'term']]

    def __str__(self):
        return f"{self.term} ({self.get_vocab_display()})"


class Category(models.Model):
    category = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.category

    class Meta:
        verbose_name_plural = "categories"


class TermGroup(models.Model):
    TERMTYPE_CHOICES = [
        ('definiendum', 'Definiendum'),
        ('definiens', 'Definiens'),
        ('other', 'Other'),
    ]

    annotation = models.ForeignKey(Annotation, models.CASCADE, null=True, related_name="termgroups")
    index = models.IntegerField(null=True)
    termtype = models.CharField("term type", max_length=11, choices=TERMTYPE_CHOICES, null=True)
    articleterm = models.ForeignKey(ArticleTerm, models.CASCADE, verbose_name="article term", help_text="Term that was used in the resource", null=True)
    category = models.ForeignKey(Category, models.CASCADE, null=True)
    lidiaterm = models.ForeignKey(LidiaTerm, models.CASCADE, null=True, verbose_name="LIDIA term")

    class Meta:
        unique_together = [['annotation', 'index']]

    def __str__(self):
        lidiaterm = self.lidiaterm.term if self.lidiaterm else None
        return f"{self.articleterm}/{lidiaterm}"
