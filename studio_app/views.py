import json

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.forms import ModelForm
from django.http import JsonResponse
from django.shortcuts import render, redirect

from common_app.models import User
from common_app.utils import permission_required
from common_app.views import check_permission, permission_warning
from studio_app.models import Studio


# 로그인한 사용자가 대표(user_type == 2) 인 경우만 진입 가능
# 진입 사용자의 소유 지점들만 출력
@login_required
@permission_required
def studio_index(request):
    context = {}

    # 대표가 소유하고 있는 지점만 조회
    studios = Studio.objects.filter(owner=request.user)
    context['studios'] = studios

    return render(
        request,
        'studio_app/studio_index.html',
        context
    )


# 지점 등록 폼
# 지점 입력시 소속 강사는 대표 자기자신 or 자신이 고용주인 강사만 선택 가능
class StudioForm(ModelForm):
    teachers = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        label='소속 강사',
    )

    class Meta:
        model = Studio
        fields = [
            'name', 'address', 'teachers'  # 이 때 여기 fields 에 teachers 를 안 넣어주면 save_m2m 안 먹는다
        ]
        labels = {
            'name': '지점명',
            'address': '주소',
        }

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner')
        super(StudioForm, self).__init__(*args, **kwargs)
        self.fields['teachers'].queryset = User.objects.filter(
            Q(user_type=3, employer=owner.id) | Q(pk=owner.id)
        )
        self.fields['address'].required = False


# 지점 추가
@login_required
@permission_required
def studio_add(request):
    context = {}
    studio_form = StudioForm(owner=request.user)

    if request.POST:
        studio_form = StudioForm(request.POST, owner=request.user)
        if studio_form.is_valid():
            studio = studio_form.save(commit=False)

            # 지점 소유자는 생성 엑션 수행자로 설정
            studio.owner = request.user
            studio.created_by = request.user
            studio.updated_by = request.user

            studio.save()
            studio_form.save_m2m()

            return redirect(studio_index)

    context['studio_form'] = studio_form

    return render(
        request,
        'studio_app/studio_add.html',
        context
    )


# 지점 정보 수정
@login_required
@permission_required
def studio_chg(request, studio_id):
    context = {}

    try:
        studio = Studio.objects.get(pk=studio_id)
        # 만약 센터 소유자와 접속한 사람이 다르다면 화면 진입 막기
        if studio.owner != request.user:
            return redirect('/permission-warning/')
    except ObjectDoesNotExist:
        return redirect('/access-warning/')

    studio_form = StudioForm(instance=studio, owner=request.user)

    if request.POST:
        studio_form = StudioForm(request.POST, instance=studio, owner=request.user)
        if studio_form.is_valid():
            studio = studio_form.save(commit=False)
            studio.updated_by = request.user
            studio.save()
            studio_form.save_m2m()

            return redirect(studio_index)

    context['studio_form'] = studio_form

    return render(
        request,
        'studio_app/studio_chg.html',
        context
    )


@login_required
@permission_required
def studio_del(request, studio_id):
    context = {}

    try:
        studio = Studio.objects.get(pk=studio_id)

        # 만약 센터 소유자와 접속한 사람이 다르다면 화면 진입 막기
        if studio.owner != request.user:
            return redirect('/permission-warning/')

        context['studio'] = studio

    except ObjectDoesNotExist:
        # 이미 삭제된(없는) 지점인 경우[뒤로가기 버튼으로 다시 돌아온 경우] 에러 메세지 출력
        context['error'] = '이미 삭제된 지점입니다'

        return render(
            request,
            'studio_app/studio_del.html',
            context
        )

    if request.POST:
        studio.delete()
        return redirect(studio_index)

    return render(
        request,
        'studio_app/studio_del.html',
        context
    )


@login_required
@permission_required
def get_teachers_of_selected_studio(request):
    studio = request.GET.get('studio')
    teachers = Studio.objects.get(pk=studio).teachers.all()

    data = []
    for teacher in teachers:
        row = {
            'name': teacher.name,
            'email': teacher.email,
            'user_type': teacher.get_user_type_display(),
        }
        data.append(row)

    response_json = json.dumps(data, cls=DjangoJSONEncoder)

    return JsonResponse(response_json, safe=False)


# 고용 강사 메인화면
@login_required
@permission_required
def teacher_index(request):
    context = {}

    teachers = User.objects.filter(employer=request.user)
    context['teachers'] = teachers

    return render(
        request,
        'studio_app/teacher_index.html',
        context
    )


class DateInput(forms.DateInput):
    input_type = 'date'


# 센터 대표가 강사 추가할 경우 비밀번호는 기본값으로 자동 설정되도록 함
class TeacherForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'name', 'email', 'lesson_fee', 'employment_start_date', 'employment_end_date'
        ]
        labels = {
            'name': '이름',
            'email': '이메일',
            'lesson_fee': '회당 강습비',
            'employment_start_date': '계약 시작일',
            'employment_end_date': '계약 종료일',
        }
        widgets = {
            # niceadmin 과 javascript 충돌이 일어나 bootstrap-datepicker를 쓰지 못함
            'employment_start_date': DateInput(),
            'employment_end_date': DateInput()
            # 'employment_start_date': forms.TextInput(
            #     attrs={'type': 'date'}
            # )
            # 'employment_start_date': DatePickerInput(
            #     options={
            #         'format': 'YYYY-MM-DD',
            #         'locale': 'ko',
            #     }
            # ),
            # 'employment_end_date': DatePickerInput(
            #     options={
            #         'format': 'YYYY-MM-DD',
            #         'locale': 'ko',
            #     }
            # )
        }

    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        self.fields['employment_start_date'].widget.attrs.update({'type': 'date'})


# 강사 추가 화면
@login_required
@permission_required
def teacher_add(request):
    context = {}
    teacher_form = TeacherForm()

    if request.POST:
        teacher_form = TeacherForm(request.POST)
        if teacher_form.is_valid():

            email = teacher_form.cleaned_data.get('email')
            name = teacher_form.cleaned_data.get('name')
            password = 'fkdlfql'

            # create_user 에서 이미 존재하는 이메일인지 체크 하고 있음
            teacher = User.objects.create_user(
                email=email,
                name=name,
                password=password
            )

            # 강사 고용주는 생성 엑션 수행자로 설정
            teacher.employer = request.user
            # 유저 타입(권한) 은 기본이 강사로 설정되어 있음(common_app/views.py)

            # 고용 정보
            teacher.lesson_fee = teacher_form.cleaned_data.get('lesson_fee')
            teacher.employment_start_date = teacher_form.cleaned_data.get('employment_start_date')
            teacher.employment_end_date = teacher_form.cleaned_data.get('employment_end_date')

            teacher.save()

            return redirect(teacher_index)

    context['teacher_form'] = teacher_form

    return render(
        request,
        'studio_app/teacher_set.html',
        context
    )


# 강사 정보 수정
@login_required
@permission_required
def teacher_chg(request, teacher_id):
    context = {}

    try:
        teacher = User.objects.get(pk=teacher_id)
        # 만약 강사 고용주와 접속한 사람이 다르다면 화면 진입 막기
        if teacher.employer != request.user:
            return redirect('/permission-warning/')
    except ObjectDoesNotExist:
        return redirect('/access-warning/')

    teacher_form = TeacherForm(instance=teacher)

    if request.POST:
        teacher_form = TeacherForm(request.POST, instance=teacher)
        if teacher_form.is_valid():
            teacher = teacher_form.save(commit=False)
            teacher.updated_by = request.user
            teacher.save()

            return redirect(teacher_index)

    context['teacher_form'] = teacher_form

    return render(
        request,
        'studio_app/teacher_set.html',
        context
    )


@login_required
@permission_required
def teacher_del(request, teacher_id):
    context = {}

    try:
        teacher = User.objects.get(pk=teacher_id)
        # 만약 강사 고용주와 접속한 사람이 다르다면 화면 진입 막기
        if teacher.employer != request.user:
            return redirect('/permission-warning/')
    except ObjectDoesNotExist:
        return redirect('/access-warning/')

    context['teacher'] = teacher

    if request.POST:
        teacher.is_active = False
        teacher.save()
        return redirect(teacher_index)

    return render(
        request,
        'studio_app/teacher_del.html',
        context
    )


@login_required
@permission_required
def member_index(request):

    return render(
        request,
        'studio_app/member_index.html'
    )


@login_required
@permission_required
def report_index(request):

    return render(
        request,
        'studio_app/report_index.html'
    )