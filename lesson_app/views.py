import datetime
import json

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from django.forms import ModelForm, inlineformset_factory
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from common_app.models import User
from lesson_app.models import Lesson, Attendance
from lesson_app.templatetags.lesson_extras import get_attendance_info_type1
from studio_app.models import Member


# -------------------------------------------------------------------------------- 담당 회원
@login_required
def member_index(request):
    context = {}

    members = Member.objects.filter(teacher=request.user)
    context['members'] = members

    return render(
        request,
        'lesson_app/member_index.html',
        context
    )


# -------------------------------------------------------------------------------- 수업 공통 함수
# 시간 계산은 dummy 일자를 붙여 계산한 후 시간 추출하는 방식 사용
def cal_end_time(start_time):
    # 수업 시작 시간에 49분 후를 종료시간으로 설정
    end_time = datetime.datetime(100, 1, 1, start_time.hour, start_time.minute, start_time.second)
    end_time = end_time + datetime.timedelta(minutes=49)
    return end_time.time()


# 수업 중복 체크
# 같은 강사의 수업 중 수업 시작 ~ 종료 시간 사이에 수업이 겹치는 경우 체크
def check_lesson_schedule(lesson_teacher, lesson_date, lesson_time):
    current_lessons = Lesson.objects.filter(
        teacher=lesson_teacher,
        lesson_date=lesson_date,
    )

    result = True

    for ex_lesson in current_lessons:
        print('기존 수업: ' + ex_lesson.lesson_time.strftime("%Y-%m-%d %H:%M:%S") + ' ~ ' + cal_end_time(ex_lesson.lesson_time).strftime("%Y-%m-%d %H:%M:%S"))
        if ex_lesson.lesson_time < lesson_time < cal_end_time(ex_lesson.lesson_time):
            result = False

        if ex_lesson.lesson_time < cal_end_time(lesson_time) < cal_end_time(ex_lesson.lesson_time):
            result = False

    return result


# -------------------------------------------------------------------------------- 수업
# 수업 폼
class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class LessonForm(ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        label='회원'
    )

    class Meta:
        model = Lesson
        fields = [
            'studio', 'lesson_date', 'lesson_time', 'lesson_type', 'members'
        ]
        labels = {
            'studio': '센터',
            'lesson_date': '수업일',
            'lesson_time': '수업시간',
            'lesson_type': '싱글/듀엣',
        }
        widgets = {
            'lesson_date': DateInput(),
            'lesson_time': TimeInput()
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(LessonForm, self).__init__(*args, **kwargs)
        # 강습 일정을 생성하려는 사용자가 근무하는 지점만 가져온다
        self.fields['studio'].queryset = User.objects.get(pk=user.id).StudioTeachers.all()
        # 강습 일정을 생성하려는 사용자가 근무하는 지점의 회원들만 가져온다
        inner_qs = User.objects.get(pk=user.id).StudioTeachers.all().values('id')
        self.fields['members'].queryset = Member.objects.filter(
            status=1,
            studio__id__in=inner_qs
        )


# LessonFormset = inlineformset_factory(
#     Attendance,
#     Lesson.members.through
# )


@login_required
def lesson_index(request):
    context = {}

    lessons = Lesson.objects.filter(teacher=request.user)
    context['lessons'] = lessons

    # lesson_formset = LessonFormset()
    # context['lesson_formset'] = lesson_formset

    return render(
        request,
        'lesson_app/lesson_index.html',
        context
    )


@login_required
def lesson_add(request):
    context = {}

    lesson_form = LessonForm(user=request.user)

    if request.POST:
        lesson_form = LessonForm(request.POST, user=request.user)
        if lesson_form.is_valid():
            lesson = lesson_form.save(commit=False)
            lesson.teacher = request.user

            if not check_lesson_schedule(lesson.teacher, lesson.lesson_date, lesson.lesson_time):
                context['lesson_form'] = lesson_form
                context['error'] = '설정하신 시간에 이미 수업 일정이 존재합니다'
                return render(
                    request,
                    'lesson_app/lesson_set.html',
                    context
                )

            lesson.created_by = request.user
            lesson.updated_by = request.user
            lesson.save()

            lesson_form.save_m2m()

            return redirect(lesson_index)

    context['lesson_form'] = lesson_form

    return render(
        request,
        'lesson_app/lesson_set.html',
        context
    )


@login_required
def lesson_chg(request, lesson_id):
    context = {}

    try:
        lesson = Lesson.objects.get(pk=lesson_id)
        # 만약 수업 담당자와 접속한 사람이 다르다면 화면 진입 막기
        if lesson.teacher != request.user:
            return redirect('/permission-warning/')
    except ObjectDoesNotExist:
        return redirect('/access-warning/')

    lesson_form = LessonForm(instance=lesson, user=request.user)

    if request.POST:
        lesson_form = LessonForm(request.POST, instance=lesson, user=request.user)
        if lesson_form.is_valid():
            lesson = lesson_form.save(commit=False)
            lesson.updated_by = request.user
            lesson.save()

            lesson_form.save_m2m()

            return redirect(lesson_index)

    context['lesson_form'] = lesson_form

    return render(
        request,
        'lesson_app/lesson_set.html',
        context
    )


@login_required
def lesson_del(request, lesson_id):
    context = {}

    try:
        lesson = Lesson.objects.get(pk=lesson_id)
        # 만약 수업 담당자와 접속한 사람이 다르다면 화면 진입 막기
        if lesson.teacher != request.user:
            return redirect('/permission-warning/')
    except ObjectDoesNotExist:
        return redirect('/access-warning/')

    if request.POST:
        lesson.delete()
        return redirect(lesson_index)

    context['lesson'] = lesson

    return render(
        request,
        'lesson_app/lesson_del.html',
        context
    )


ATTENDANCE_STATUS_WITH_COLOR = [
    (1, '수업 예정', 'bg-success'),
    (2, '수업 완료', 'bg-primary'),
    (3, '사전 취소', 'bg-warning'),
    (4, '당일 취소', 'bg-danger'),
    (5, '일시 중지', 'bg-info')
]


@login_required
def get_attendance_of_selected_lesson(request):
    lesson_id = request.GET.get('lesson')

    data = []
    for attendance in Lesson.objects.get(pk=lesson_id).lesson_related_attendance.all():
        row = {
            'member': attendance.member.name,
            'attendance': attendance.get_status_display(),
            'action': ''.join([
                '<a href="#" onclick="setAttendance('
                + str(attendance.id) + ', ' + str(attendance_status[0]) +
                ')"><span class="badge ' + attendance_status[2] + ' btn me-1">'
                + attendance_status[1]
                + '</span></a>'
                for attendance_status in ATTENDANCE_STATUS_WITH_COLOR
            ])
        }
        data.append(row)

    response_json = json.dumps(data, cls=DjangoJSONEncoder)

    return JsonResponse(response_json, safe=False)


@login_required
def set_attendance(request):
    attendance_id = request.GET.get('attendance')
    set_status = request.GET.get('status')

    try:
        attendance = Attendance.objects.get(pk=attendance_id)
    except ObjectDoesNotExist:
        messages.error(request, '잘못된 입력입니다. 다시 시도해주세요')
        response = {'result': False}
        return HttpResponse(json.dumps(response))

    attendance.status = set_status
    attendance.save()

    msg = ATTENDANCE_STATUS_WITH_COLOR[int(attendance.status) - 1][1] + ' 로 변경되었습니다'
    messages.success(request, msg)
    response = {'result': True}
    return HttpResponse(json.dumps(response))


@login_required
def add_lesson_by_schedule(request):
    if request.POST:
        lesson_form = LessonForm(request.POST, user=request.user)
        if lesson_form.is_valid():
            print("유니크 제약조건 체크")
            lesson = lesson_form.save(commit=False)
            lesson.teacher = request.user

            if not check_lesson_schedule(lesson.teacher, lesson.lesson_date, lesson.lesson_time):
                response = {
                    'result': False,
                    'msg': '설정하신 시간에 이미 수업 일정이 존재합니다'
                }
                messages.error(request, '설정하신 시간에 이미 수업 일정이 존재합니다')
                return HttpResponse(json.dumps(response))

            lesson.created_by = request.user
            lesson.updated_by = request.user

            try:
                lesson.save()
                lesson_form.save_m2m()
            except IntegrityError:
                response = {'result': False}
                messages.error(request, '설정하신 시간에 이미 수업 일정이 존재합니다')
                return HttpResponse(json.dumps(response))

        else:
            context = {'lesson_form': lesson_form}

            return render(
                request,
                'dashboard_app/add_one_lesson_modal.html',
                context
            )

    response = {'result': True,}
    messages.success(
        request,
        '[ ' + lesson.lesson_date.strftime("%Y-%m-%d") + ' ' + lesson.lesson_time.strftime("%H:%M") + ' ] ' + '수업 일정이 등록되었습니다'
    )
    return HttpResponse(json.dumps(response))
    # response_json = json.dumps(response, cls=DjangoJSONEncoder)
    # return JsonResponse(response_json, safe=False)


@login_required
def add_weekly_lesson_by_schedule(request):

    if request.POST:
        try:
            input_date = request.POST.get('input-date')
            input_date = datetime.datetime.strptime(input_date, '%Y-%m-%d').date()
            start_date = input_date + datetime.timedelta(days=-1 * input_date.weekday())
            end_date = start_date + datetime.timedelta(days=5)
        except:
            response = {'result': False}
            messages.error(request, '주간 일정을 생성할 날짜를 제대로 입력해주세요')
            return HttpResponse(json.dumps(response))

        try:
            for member in request.user.MemberTeacher.filter(status=1):
                for schedule in member.memberdefaultschedule_set.all():
                    lesson_date = start_date + datetime.timedelta(days=schedule.day_of_week - 1)

                    # 겹치는 시간 체크
                    if not check_lesson_schedule(
                            request.user, lesson_date, schedule.lesson_time
                    ):
                        continue

                    lesson, created = Lesson.objects.get_or_create(
                        lesson_date=lesson_date,
                        lesson_time=schedule.lesson_time,
                        studio=member.studio,
                        teacher=request.user
                    )

                    attendance, created = Attendance.objects.get_or_create(
                        lesson=lesson,
                        member=member,
                    )
        except Exception as e:
            messages.error(request, e)
            response = {'result': False}
            return HttpResponse(json.dumps(response))

    messages.success(
        request,
        '[ ' + start_date.strftime("%Y-%m-%d") + ' ~ ' + end_date.strftime("%Y-%m-%d") + ' ] ' + '주간 수업 일정이 등록되었습니다'
    )

    response = {'result': True}
    return HttpResponse(json.dumps(response))


@login_required
def set_attendance_by_schedule(request):
    lesson_id = request.GET.get('lesson')
    attendance_status = request.GET.get('attendance')

    try:
        lesson = Lesson.objects.get(pk=lesson_id)
    except ObjectDoesNotExist:
        messages.error(request, '잘못된 입력입니다.')
        response = {'result': False}
        response_json = json.dumps(response, cls=DjangoJSONEncoder)
        return JsonResponse(response_json, safe=False)

    if lesson.teacher != request.user:
        messages.error(request, '담당 수업의 출석만 변경할 수 있습니다')
        response = {'result': False}
        response_json = json.dumps(response, cls=DjangoJSONEncoder)
        return JsonResponse(response_json, safe=False)

    for attendance in lesson.lesson_related_attendance.all():
        attendance.status = attendance_status
        attendance.save()

    messages.success(
        request,
        '[ ' + lesson.lesson_time.strftime("%H:%M") + ' ] ' + get_attendance_info_type1(lesson) + ' 수업 출석 정보가 변경되었습니다'
    )

    response = {'result': True}
    response_json = json.dumps(response, cls=DjangoJSONEncoder)
    return JsonResponse(response_json, safe=False)