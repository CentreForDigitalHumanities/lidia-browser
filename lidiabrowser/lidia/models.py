from django.db import models

import iso639

import sync.models as syncmodels


class Publication(models.Model):
    zotero_id = models.CharField(max_length=100, unique=True)
    attachment_id = models.CharField(max_length=16, unique=True, null=True)
    title = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.title or self.zotero_id


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


class Annotation(models.Model):
    RELATION_TYPE_CHOICES = [
        ("", "None"),
        ("contradicts", "Contradicts"),
        ("generalizes", "Generalizes"),
        ("invalidates", "Invalidates"),
        ("specialcase", "Is a special case of"),
        ("supports", "Supports"),
    ]
    
    lidia_id = models.CharField(verbose_name="LIDIA ID", max_length=100, unique=True, null=True)
    # Allow nullable zotero_annotation to facilitate placeholders
    zotero_annotation = models.OneToOneField(syncmodels.Annotation, verbose_name="Zotero annotation", on_delete=models.CASCADE, null=True, to_field="zotero_id")
    parent_attachment = models.ForeignKey(Publication, verbose_name="publication", on_delete=models.CASCADE, to_field='attachment_id', blank=True, null=True)
    textselection = models.TextField(verbose_name="quoted text", default='')
    sort_index = models.CharField(max_length=100, help_text="Index to keep order of annotation in document", default="")
    argname = models.CharField(verbose_name="argument name", max_length=100, default='')
    arglang = models.ForeignKey(Language, verbose_name="subject language", on_delete=models.SET_NULL, to_field='code', null=True)
    description = models.TextField(default='')
    argcont = models.BooleanField(verbose_name="continuation", help_text="True if the annotation is a continuation of the previous argument", null=True)
    page_start = models.CharField(verbose_name="start page", max_length=16, null=True)
    page_end = models.CharField(verbose_name="end page", max_length=16, null=True)
    relation_type = models.CharField(max_length=11, choices=RELATION_TYPE_CHOICES, default='')
    relation_to = models.ForeignKey('self', to_field='lidia_id', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.argname or self.lidia_id or self.zotero_annotation or "(no name or ID)"


class ArticleTerm(models.Model):
    term = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.term


class LidiaTerm(models.Model):
    VOCAB_CHOICES = [
        ('lol', 'Lexicon of Linguistics'),
        ('custom', 'Custom'),
    ]

    vocab = models.CharField(max_length=6, choices=VOCAB_CHOICES)
    term = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.term


class Category(models.Model):
    category = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.category


class TermGroup(models.Model):
    TERMTYPE_CHOICES = [
        ('', 'Undefined'),
        ('definiendum', 'Definiendum'),
        ('definiens', 'Definiens'),
        ('other', 'Other'),
    ]

    annotation = models.ForeignKey(Annotation, models.CASCADE, null=True)
    termtype = models.CharField(max_length=11, choices=TERMTYPE_CHOICES)
    articleterm = models.ForeignKey(ArticleTerm, models.CASCADE, null=True)
    category = models.ForeignKey(Category, models.CASCADE, null=True)
    lidiaterm = models.ForeignKey(LidiaTerm, models.CASCADE, null=True)

    def __str__(self):
        return f"{self.annotation}: {self.lidiaterm}"
