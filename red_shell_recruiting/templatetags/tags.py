import random

from django import template
from user_agents import parse

register = template.Library()


@register.simple_tag(takes_context=True)
def is_mobile_device(context):
    request = context.get("request")
    if not request:
        return False
    user_agent_string = request.META.get("HTTP_USER_AGENT", "")
    user_agent = parse(user_agent_string)
    return user_agent.is_mobile or user_agent.is_tablet


@register.simple_tag
def css_invalidate_int(a=0, b=1000000):
    """
    Simple tag to generate a random integer between `a` and `b`.

    Args:
        a (int): The lower bound of the random number (inclusive).
        b (int): The upper bound of the random number (inclusive).

    Returns:
        int: A random integer between `a` and `b`.
    """
    if b is None:
        a, b = 0, a
    return random.randint(a, b)
