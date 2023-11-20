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


# class BaseTermGroupListFilter(admin.SimpleListFilter):
    


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ["parent_attachment_display", "argname_display", "description", "arglang", "page_range", "summary_of_term_groups", "relation_display"]
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
    fieldsets = [
        (
            None, {
                "fields": [
                    "parent_attachment",
                    "argname",
                    "description",
                    "page_range",
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
                    "zotero_annotation",
                ]
            }
        )
    ]

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


class PublicationAdmin(admin.ModelAdmin):
    list_display = ["zotero_id", "attachment_id", "title"]


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
