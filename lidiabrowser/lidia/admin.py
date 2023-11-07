from django.contrib import admin

from .models import (
    Annotation,
    Publication,
    Language,
    TermGroup,
    Category,
)
    


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ["sort_index", "zotero_id", "lidia_id", "parent_attachment", "argname", "arglang", "page_start"]
    list_filter = ["parent_attachment", "arglang"]
    ordering = ("parent_attachment", "sort_index")


class PublicationAdmin(admin.ModelAdmin):
    list_display = ["zotero_id", "attachment_id", "title"]


admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Language)
admin.site.register(TermGroup)
admin.site.register(Category)
