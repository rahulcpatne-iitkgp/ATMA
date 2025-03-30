from django import template

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
    """
    Adds a CSS class to a form field widget.
    """
    return field.as_widget(attrs={"class": css_class})