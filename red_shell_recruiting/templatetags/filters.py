import os
from django import template

register = template.Library()

@register.filter
def filename(value):
    """Extracts the filename from a file path."""
    return os.path.basename(value)
