# project/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def add_class(value, css_class):
    """Adds a CSS class to a form field widget."""
    if hasattr(value, 'widget'):
        value.widget.attrs['class'] = value.widget.attrs.get('class', '') + ' ' + css_class
    return value
