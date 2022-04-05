from time import strftime

from django import template
from django.db.models import Sum

register = template.Library()


# 회원의 기본 일정을 합쳐 문자열로 만들어 반환
@register.filter
def get_members_of_lesson(value):
    return ', '.join([attendance.member.name + '[' + attendance.get_status_display() + ']' for attendance in value.lesson_related_attendance.all()])
