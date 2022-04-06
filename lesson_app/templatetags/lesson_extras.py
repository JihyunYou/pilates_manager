from time import strftime

from django import template
from django.db.models import Sum

register = template.Library()


# 회원1, 회원2
@register.filter
def get_attendance_info_type1(value):
    return ','.join([attendance.member.name for attendance in value.lesson_related_attendance.all()])


# 회원1[수업상태1], 회원2[수업상태2]
@register.filter
def get_attendance_info_type2(value):
    return ', '.join([attendance.member.name + '[' + attendance.get_status_display() + ']' for attendance in value.lesson_related_attendance.all()])


# 회원1, 회원2 [수업상태]
@register.filter
def get_attendance_info_type3(value):
    first_attendance = value.lesson_related_attendance.first()
    return get_attendance_info_type1(value) + ' [' + first_attendance.get_status_display() + ']'


# 수업 상태에 따른 text-color 반환
@register.filter
def get_attendance_info_type4(value):
    first_attendance = value.lesson_related_attendance.first()
    status_text_color = [
        'text-success', 'text-primary', 'text-warning', 'text-danger', 'text-info'
    ]
    return status_text_color[first_attendance.status - 1]
