from django import template

register = template.Library()

@register.filter
def chunked(value, size):
    return [value[i:i + size] for i in range(0, len(value), size)]
