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
