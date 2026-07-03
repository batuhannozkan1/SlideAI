from __future__ import annotations

from django import template

register = template.Library()

_SIZES = {"sm", "lg", "xl"}            # md = default (no class)
_WEIGHTS = {"bold", "normal"}
_COLORS = {"ok", "warn", "risk", "info", "brand"}


@register.filter
def el_style(styles, key):
    """CSS classes for a text element's style preset, read from content.styles[key].

    styles is the optional `content.styles` dict; key is the element name
    (heading / eyebrow / subtitle / highlight / description). Returns a safe,
    bounded class string (e.g. "sz-lg fw-bold tc-info") — unknown values are ignored.
    """
    if not isinstance(styles, dict):
        return ""
    s = styles.get(key)
    if not isinstance(s, dict):
        return ""
    classes = []
    if s.get("size") in _SIZES:
        classes.append("sz-" + s["size"])
    if s.get("weight") in _WEIGHTS:
        classes.append("fw-" + s["weight"])
    if s.get("color") in _COLORS:
        classes.append("tc-" + s["color"])
    return " ".join(classes)
