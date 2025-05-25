from django import template

register = template.Library()

status_order = [
    'publish', 'donor_find', 'transportation', 'completed'
]

@register.simple_tag
def status_passed(current, step):
    try:
        return status_order.index(current) >= status_order.index(step)
    except ValueError:
        return False

@register.simple_tag
def status_passed_percent(current):
    try:
        index = status_order.index(current) + 1
        total = len(status_order)
        return (index / total) * 100
    except ValueError:
        return 0

@register.simple_tag
def step_statuses():
    return status_order

@register.simple_tag
def toTurkish(val):
    if val == 'Publish':
        return "Yayında"
    elif val == 'Donor_Find':
        return "Bağışçı Bulundu"
    elif val == 'Transportation':
        return "Taşımada"
    elif val == 'Completed':
        return "Tamamlandı" 
