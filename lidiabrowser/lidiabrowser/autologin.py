from django.contrib.auth import login
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from lidiabrowser.init import get_anonymous_user


def index_view_autologin(request: HttpRequest):
    # If the user is not authenticated, automatically login to the 
    # anonymous user, which should be created if necessary.
    if not request.user.is_authenticated:
        # Create anonymous user and viewer group if necessary
        anonymous_user = get_anonymous_user()
        login(request, anonymous_user)
    return HttpResponseRedirect(reverse("admin:index"))
    
