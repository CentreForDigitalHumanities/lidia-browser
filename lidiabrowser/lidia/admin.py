from django.contrib import admin

from .models import (
    Annotation,
    ArticleTerm,
    ContinuationAnnotation,
    LidiaTerm,
    Publication,
    Language,
    TermGroup,
    Category,
)


class ContinuationInline(admin.TabularInline):
    model = ContinuationAnnotation
    fk_name = "start_annotation"
    ordering = ("sort_index",)
    fields = ["textselection", "sort_index"]
    extra = 0


class TermGroupInline(admin.TabularInline):
    model = TermGroup
    fk_name = "annotation"
    ordering = ("index",)
    fields = ["termtype", "articleterm", "category", "lidiaterm"]
    extra = 0


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ["zotero_annotation", "lidia_id", "parent_attachment", "argname", "arglang", "page_start"]
    list_filter = ["parent_attachment", "arglang"]
    ordering = ("parent_attachment", "sort_index")
    inlines = [
        ContinuationInline,
        TermGroupInline,
    ]


class PublicationAdmin(admin.ModelAdmin):
    list_display = ["zotero_id", "attachment_id", "title"]


admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Language)
admin.site.register(Category)
admin.site.register(LidiaTerm)
admin.site.register(ArticleTerm)
