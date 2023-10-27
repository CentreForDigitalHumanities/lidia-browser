from django.contrib import admin

from .models import Annotation, Publication, Sync


class AnnotationAdmin(admin.ModelAdmin):
    pass


class PublicationAdmin(admin.ModelAdmin):
    pass


class SyncAdmin(admin.ModelAdmin):
    pass


admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Sync, SyncAdmin)
