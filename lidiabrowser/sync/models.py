from django.db import models


class Publication(models.Model):
    zotero_id = models.CharField(max_length=100, unique=True)
    content = models.JSONField(default=dict)

    def __str__(self):
        return self.zotero_id


class Annotation(models.Model):
    zotero_id = models.CharField(max_length=100, unique=True)
    content = models.JSONField(default=dict)

    def __str__(self):
        return self.zotero_id


class Sync(models.Model):
    library_id = models.CharField(max_length=100, unique=True)
    library_version = models.IntegerField()

    def __str__(self):
        return f"Library #{self.library_id}"
