from django.db import models


class Publication(models.Model):
    zotero_id = models.CharField(max_length=100, unique=True)
    content = models.JSONField(default=dict)


class Annotation(models.Model):
    zotero_id = models.CharField(max_length=100, unique=True)
    content = models.JSONField(default=dict)


class Sync(models.Model):
    library_id = models.CharField(max_length=100, unique=True)
    library_version = models.IntegerField()
