import datetime
import json

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import render

from lesson_app.models import Lesson
from lesson_app.templatetags.lesson_extras import get_attendance_info_type3
from lesson_app.views import LessonForm, ATTENDANCE_STATUS_WITH_COLOR
from studio_app.models import Studio


@login_required
def index(request):
    context = {}

    lessons = Lesson.objects.filter(
        teacher=request.user,
        lesson_date=datetime.date.today()
    )
    context['lessons'] = lessons

    lesson_form = LessonForm(user=request.user)
    context['lesson_form'] = lesson_form

    context['ATTENDANCE_STATUS_WITH_COLOR'] = ATTENDANCE_STATUS_WITH_COLOR

    return render(
        request,
        'dashboard_app/dashboard.html',
        context
    )


# -------------------------------------------------------------------------------- Dashboard Ajax
# 대표인 경우 소유하고 있는 모든 지점에 대한 스케쥴
# 강사인 경우 일하고 있는 모든 지점에 대한 스케쥴
@login_required
def get_dashboard_resources(request):
    # 대표 혹은 관리자인 경우
    if request.user.user_type <= 2:
        studios = Studio.objects.filter(owner=request.user)
    # 강사인 경우
    elif request.user.user_type == 3:
        studios = request.user.StudioTeachers.all()

    resources = []
    for studio in studios:
        for teacher in studio.teachers.all():
            row = {
                'id': str(studio.id) + '_' + str(teacher.id),
                'title': studio.name + '-' + teacher.name
            }
            resources.append(row)

    response_json = json.dumps(resources, cls=DjangoJSONEncoder)
    return JsonResponse(response_json, safe=False)


@login_required
def get_dashboard_events(request):
    #   수업예정: #198754 / 수업완료: #0d6dfd / 사전취소: #ffc107 / 당일취소: #dc3546 / 홀딩: #0dcaf0
    color_array = ['#198754', '#0d6dfd', '#ffc107', '#dc3546', '#0dcaf0']

    # 대표 혹은 관리자인 경우
    if request.user.user_type <= 2:
        studios = Studio.objects.filter(owner=request.user)
    # 강사인 경우
    elif request.user.user_type == 3:
        studios = request.user.StudioTeachers.all()

    resources = []
    for studio in studios:
        for teacher in studio.teachers.all():
            for lesson in teacher.lesson_set.all():
                attendance = lesson.lesson_related_attendance.first()
                row = {
                    'id': str(lesson.id),
                    'resourceId': str(studio.id) + '_' + str(teacher.id),
                    'title': get_attendance_info_type3(lesson),
                    'start': datetime.datetime.strptime(
                        str(lesson.lesson_date) + ' ' + str(lesson.lesson_time),
                        "%Y-%m-%d %H:%M:%S"
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    # 'end': '2022-04-06 16:10:00',
                    'color': color_array[attendance.status - 1],
                    'url': '#',
                }
                resources.append(row)

    response_json = json.dumps(resources, cls=DjangoJSONEncoder)
    return JsonResponse(response_json, safe=False)
