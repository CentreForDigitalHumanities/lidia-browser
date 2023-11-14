from django.contrib.auth.models import Group, Permission, User

ANONYMOUSUSERNAME = "anonymous"


def initiate_groups() -> dict[str, Group]:
    """Create groups for viewer accounts and return a dictionary containing
    the group objects."""
    # For now, only create a 'view all' group - no distinction yet
    # between all or restricted access
    view_all, _ = Group.objects.get_or_create(name="view_all")
    models = [
        'publication', 'language', 'annotation', 'articleterm',
        'lidiaterm', 'category', 'termgroup'
    ]
    permissions = []
    for model in models:
        permissions.append(Permission.objects.get_by_natural_key(
            "view_" + model, "lidia", model
        ))
    view_all.permissions.add(*permissions)
    return {
        "view_all": view_all
    }


def create_anonymous_user(view_all_group: Group) -> User:
    anonymous_user = User.objects.create_user(
        ANONYMOUSUSERNAME,
        is_staff=True
    )
    anonymous_user.groups.add(view_all_group)
    return anonymous_user


def get_anonymous_user() -> User:
    try:
        anonymous_user = User.objects.get(username=ANONYMOUSUSERNAME)
    except User.DoesNotExist:
        groups = initiate_groups()
        anonymous_user = create_anonymous_user(groups["view_all"])
    return anonymous_user

