from django import template

register = template.Library()


@register.filter
def addclass(field, css_class):
    return field.as_widget(attrs={"class": css_class})
