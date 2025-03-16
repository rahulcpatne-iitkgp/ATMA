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