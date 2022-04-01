from time import strftime

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


# 강사가 속한 지점 반환 (지점, 지점 형태로)
@register.filter
def get_studios_of_teacher(value):
    return ', '.join([studio.name for studio in value.StudioTeachers.all()])


# 회원 상태에 따른 수 반환
@register.filter
def get_number_of_members_by_status(value, arg):
    return value.filter(status=arg).count()


# 회원의 기본 일정을 합쳐 문자열로 만들어 반환
@register.filter
def get_default_schedule_of_member(value):
    return ', '.join([schedule.get_day_of_week_display() + '-' + schedule.lesson_time.strftime("%H:%M") for schedule in value.memberdefaultschedule_set.all()])