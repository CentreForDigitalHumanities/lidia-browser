from django.db import models


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


class Annotation(models.Model):
    RELATION_TYPE_CHOICES = [
        ("", "None"),
        ("contradicts", "Contradicts"),
        ("generalizes", "Generalizes"),
        ("invalidates", "Invalidates"),
        ("specialcase", "Is a special case of"),
        ("supports", "Supports"),
    ]

    zotero_id = models.CharField(max_length=100, unique=True, null=False)
    parent_attachment = models.ForeignKey(Publication, on_delete=models.CASCADE, to_field='attachment_id', blank=True, null=True)
    textselection = models.TextField(default='')
    argname = models.CharField(max_length=100, default='')
    arglang = models.ForeignKey(Language, on_delete=models.SET_NULL, to_field='code', null=True)
    description = models.TextField(default='')
    argcont = models.BooleanField(null=True)
    page_start = models.CharField(max_length=16, null=True)
    page_end = models.CharField(max_length=16, null=True)
    relation_type = models.CharField(max_length=11, choices=RELATION_TYPE_CHOICES, default='')
    relation_to = models.ForeignKey('self', to_field='zotero_id', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.argname or self.zotero_id


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

    annotation_id = models.ForeignKey(Annotation, models.CASCADE, null=True, to_field='zotero_id')
    termtype = models.CharField(max_length=11, choices=TERMTYPE_CHOICES)
    articleterm = models.ForeignKey(ArticleTerm, models.CASCADE, null=True)
    category = models.ForeignKey(Category, models.CASCADE, null=True)
    lidiaterm = models.ForeignKey(LidiaTerm, models.CASCADE, null=True)

    def __str__(self):
        return f"{self.annotation_id}: {self.lidiaterm}"
