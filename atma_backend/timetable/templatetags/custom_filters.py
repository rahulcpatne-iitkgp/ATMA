from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='split')
def split(value, key):
    """
    Returns the string split by the given key.
    """
    return value.split(key)

@register.filter(name='filter_by_day')
def filter_by_day(schedules, day):
    """
    Filters schedules by day.
    """
    return schedules.filter(timeslot__day=day)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to the form field."""
    if field.field.widget.attrs.get('class'):
        field.field.widget.attrs['class'] += f' {css_class}'
    else:
        field.field.widget.attrs['class'] = css_class
    return field

@register.filter(name='attr')
def add_attribute(field, attr_value):
    """Add a custom attribute to a form field."""
    attr, value = attr_value.split(':', 1)
    field.field.widget.attrs[attr] = value
    return field

@register.filter(name='add')
def add_strings(value, arg):
    """Concatenate strings."""
    return str(value) + str(arg)