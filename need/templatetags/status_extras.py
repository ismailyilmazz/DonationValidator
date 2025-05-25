from django import template
from need.models import Need 

register = template.Library()

status_order = [
    'publish', 'donor_find','courier_find', 'transportation', 'completed'
]


def currentDecoder(current):
    index = 0
    choices = Need.STATUS_CHOICES
    for (choice,_) in choices:
        if choice == status_order[index]:
            index = index+1
        if choice == current:
            break
        
    return status_order[index-1]

@register.simple_tag
def status_passed(current, step):
    current = currentDecoder(current)
    try:
        return status_order.index(current) >= status_order.index(step)
    except ValueError:
        return False

@register.simple_tag
def status_passed_percent(current):
    print(current)
    current = currentDecoder(current)
    print(current)
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
    elif val == 'Courier_Find':
        return "Taşıyıcı Bulundu"
    elif val == 'Transportation':
        return "Taşımada"
    elif val == 'Completed':
        return "Tamamlandı" 
