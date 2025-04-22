from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Szótárból kulcs alapján értéket ad vissza."""
    return dictionary.get(key)
