from django.contrib import admin


class LidiaBrowserAdminSite(admin.AdminSite):
    site_header = "LIDIA Annotation Browser"
    site_title = "LIDIA Annotation Browser"
    site_url = None  # type: ignore
    logout_template = "lidiabrowser/logged_out.html"
    login_template = "lidiabrowser/login.html"
