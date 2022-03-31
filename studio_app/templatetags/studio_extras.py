from django import template
from django.db.models import Sum

register = template.Library()


# Membership 에 대해 전달받은 arg 컬럼에 대한 Sum 값을 return
#   arg = [ reg_amount, number_of_lesson ]
@register.filter
def get_total_value_of_selected_member(value, arg):
    return value.aggregate(
        total=Sum(arg)
    ).get('total') or 0
