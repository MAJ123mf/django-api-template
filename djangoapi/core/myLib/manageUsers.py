from django.contrib.auth.models import User

def getUserGroups(user: User):
    """
    Gets a list with the user groups that the user belongs to. The user is an object of the
        django.contrib.auth.models.User class
    """
    l = user.groups.values_list('name', flat=True)  # QuerySet Object
    return list(l)

def getUserGroups_fromUsername(username):
    """
    Gets a list with the user groups that the user belongs to. The username is the username,
    usually an email
    """
    user = User.objects.get(username=username)
    return getUserGroups(user)

def canExport(user: User) -> bool:
    """
    Checks if the user has the permission to export data.
    The user is an object of the django.contrib.auth.models.User class.
    """
    return user.has_perm('export.can_export_geopackage')

def canExport_fromUsername(username: str) -> bool:
    """
    Checks if the user has the permission to export data.
    The username is the username, usually an email.
    """
    user = User.objects.get(username=username)
    return canExport(user)
