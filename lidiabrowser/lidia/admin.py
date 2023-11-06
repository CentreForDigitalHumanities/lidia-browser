from django.contrib import admin

from .models import Annotation, Publication


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ["zotero_id", "parent_attachment", "argname", "arglang", "page_start"]
    list_filter = ["parent_attachment", "arglang"]


class PublicationAdmin(admin.ModelAdmin):
    list_display = ["zotero_id", "attachment_id", "title"]


admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Publication, PublicationAdmin)
