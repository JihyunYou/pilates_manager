import json

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import ModelForm, inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect

from common_app.models import User
from lesson_app.models import Lesson, Attendance
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

    msg = ''

    try:
        attendance = Attendance.objects.get(pk=attendance_id)
    except ObjectDoesNotExist:
        msg = '잘못된 출석 설정입니다.'

    attendance.status = set_status
    attendance.save()

    msg = ATTENDANCE_STATUS_WITH_COLOR[int(attendance.status) - 1][1] + ' 로 변경되었습니다'

    data = []
    row = {
        'msg': msg
    }
    data.append(row)

    response_json = json.dumps(data, cls=DjangoJSONEncoder)
    return JsonResponse(msg,safe=False)


