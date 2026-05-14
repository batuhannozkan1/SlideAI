from django.utils.text import slugify as django_slugify


def generate_slug(text: str, max_length: int = 255) -> str:
    return django_slugify(text)[:max_length]
