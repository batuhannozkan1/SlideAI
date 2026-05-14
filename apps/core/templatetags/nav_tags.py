from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_nav(context, url_prefix: str) -> str:
    request = context.get("request")
    if request and request.path.startswith(url_prefix):
        return "active"
    return ""


@register.simple_tag(takes_context=True)
def active_url_name(context, url_name: str) -> str:
    request = context.get("request")
    if request and hasattr(request, "resolver_match") and request.resolver_match:
        if request.resolver_match.url_name == url_name:
            return "active"
    return ""
