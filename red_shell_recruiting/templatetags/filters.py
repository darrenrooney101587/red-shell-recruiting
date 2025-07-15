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


@register.filter
def dict_get(d: dict, key) -> any:
    """
    Django template filter to get a value from a dict by key.
    Args:
        d (dict): The dictionary to look up.
        key: The key to look up.
    Returns:
        Any: The value for the key, or None if not found.
    """
    if not isinstance(d, dict):
        return None
    return d.get(key)
