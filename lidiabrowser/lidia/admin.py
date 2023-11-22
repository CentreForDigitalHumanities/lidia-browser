from typing import List, Type
from django.contrib import admin
from django.http import HttpRequest

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


# class BaseTermGroupListFilter(admin.SimpleListFilter):
    


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ["parent_attachment_display", "argname_display", "description", "arglang", "page_range_complete", "summary_of_term_groups", "relation_display"]
    list_display_links = ["argname_display"]
    list_filter = ["parent_attachment", "arglang", "termgroups__articleterm__term", "termgroups__lidiaterm__term", "termgroups__category__category"]
    ordering = ("parent_attachment", "sort_index")
    inlines = [
        ContinuationInline,
        TermGroupInline,
    ]
    search_fields = [
        "argname",
        "description",
        "termgroups__lidiaterm__term",
        "termgroups__articleterm__term",
        "termgroups__category__category",
    ]
    readonly_fields = [
        "page_range",
        "page_range_in_pdf",
        "full_quotation"
    ]  # Necessary for callables

    @admin.display(
        ordering="argname",
        description="name",
        empty_value="(no name)"
    )
    def argname_display(self, obj: Annotation):
        return obj.argname if obj.argname else "(no name)"

    @admin.display(
        ordering="parent_attachment",
        description="publication",
    )
    def parent_attachment_display(self, obj: Annotation):
        if not obj.parent_attachment:
            return "(undefined)"
        title = obj.parent_attachment.title
        if not title:
            return "(no title)"
        elif len(title) > 50:
            return title[0:45] + "…"
        else:
            return title

    @admin.display(
        description="relation",
    )
    def relation_display(self, obj: Annotation):
        if not obj.relation_type:
            return None
        return f"{obj.get_relation_type_display()} {obj.relation_to}"

    @admin.display(
        description="page range",
        ordering="page_start"
    )
    def page_range_complete(self, obj: Annotation):
        return f"{obj.page_range} ({obj.page_range_in_pdf})"

    def get_fieldsets(self, request: HttpRequest, obj=None):
        fieldsets = [
            (
                None, {
                    "fields": [
                        "parent_attachment",
                        "argname",
                        "full_quotation",
                        "description",
                        "page_range",
                        "page_range_in_pdf",
                        "arglang",
                    ],
                }
            ), (
                "Relation to other annotation", {
                    "fields": [
                        "relation_type",
                        "relation_to",
                    ],
                }
            ), (
                "Technical details", {
                    "fields": [
                        "lidia_id",
                    ]
                }
            )
        ]
        if request.user.is_superuser:  # type: ignore
            # Only show link to annotation in sync to superuser
            fieldsets[2][1]["fields"].append("zotero_annotation")
        return fieldsets

    def get_inlines(self, request: HttpRequest, obj=None):
        inlines: List[Type[admin.TabularInline]] = [TermGroupInline]
        if request.user.is_superuser:  # type: ignore
            # Only show continuation annotations to superuser because
            # for normal users this distinction is irrelevant
            inlines.append(ContinuationInline)
        return inlines

class PublicationAdmin(admin.ModelAdmin):
    list_display = ["zotero_publication", "attachment_id", "title"]
    change_form_template = "lidia/change_form_publication.html"


class LidiaTermAdmin(admin.ModelAdmin):
    list_display = ["term", "vocab"]
    list_filter = ["vocab"]


class LanguageAdmin(admin.ModelAdmin):
    list_display = ["code", "name"]


admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Category)
admin.site.register(LidiaTerm, LidiaTermAdmin)
admin.site.register(ArticleTerm)
