from django.contrib.admin.apps import AdminConfig


class LidiaBrowserAdminConfig(AdminConfig):
    default_site = "lidiabrowser.admin.LidiaBrowserAdminSite"
