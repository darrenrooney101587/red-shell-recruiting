import os
from datetime import datetime
from django import template

register = template.Library()


@register.filter
def filename(value):
    """Extracts the filename from a file path."""
    return os.path.basename(value)


@register.filter
def in_groups(user, group_names):
    """
    Check if a user belongs to any of the specified groups.
    :param user: User object
    :param group_names: Comma-separated string of group names
    :return: True if the user belongs to any of the groups, False otherwise
    """
    if not user.is_authenticated:
        return False
    group_list = [group.strip() for group in group_names.split(",")]
    return user.groups.filter(name__in=group_list).exists()


@register.filter
def has_perm(user, permission):
    """Checks if a user has the given permission"""
    return user.has_perm(permission)
