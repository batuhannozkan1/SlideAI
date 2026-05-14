from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_nav(context, url_prefix: str) -> str:
    request = context.get("request")
    if request and request.path.startswith(url_prefix):
        return "active"
    return ""
