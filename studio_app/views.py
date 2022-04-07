import json

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Sum
from django.forms import ModelForm, inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect

from common_app.models import User
from common_app.utils import permission_required
from common_app.views import check_permission, permission_warning
from lesson_app.templatetags.lesson_extras import get_attendance_info_type2
from studio_app.models import Studio, Member, Membership, MemberDefaultSchedule


# -------------------------------------------------------------------------------- 센터(지점)
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
        self.fields['teachers'].required = False


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


# 센터 메인 화면에서 센터 선택 시 해당 센터의 강사들 반환
@login_required
@permission_required
def get_teachers_of_selected_studio(request):
    studio = request.GET.get('studio')
    teachers = Studio.objects.get(pk=studio).teachers.all()

    data = []
    for teacher in teachers:
        row = {
            'name': teacher.name,
            'user_type': teacher.get_user_type_display(),
            'lesson_fee': '{:,}'.format(teacher.lesson_fee or 0) + ' 원',
        }
        data.append(row)

    response_json = json.dumps(data, cls=DjangoJSONEncoder)

    return JsonResponse(response_json, safe=False)


# 센터 메인 화면에서 센터 선택 시 해당 샌터의 회원들 반환
@login_required
@permission_required
def get_members_of_selected_studio(request):
    studio = request.GET.get('studio')
    members = Member.objects.filter(studio=studio)

    data = []
    for member in members:
        row = {
            'name': member.name,
            'status': member.get_status_display(),
            'sum': '{:,}'.format(member.membership_set.all().aggregate(total=Sum('reg_amount')).get('total') or 0) + ' 원',
            'count': '{:,}'.format(member.membership_set.all().count()) + ' 회',
        }
        data.append(row)

    response_json = json.dumps(data, cls=DjangoJSONEncoder)

    return JsonResponse(response_json, safe=False)


# -------------------------------------------------------------------------------- 강사
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
def get_lesson_of_selected_teacher(request):
    teacher_id = request.GET.get('teacher')
    teacher = User.objects.get(pk=teacher_id)

    data = []
    for lesson in teacher.lesson_set.all():
        row = {
            'lesson_date': lesson.lesson_date.strftime("%Y-%m-%d"),
            'studio': lesson.studio.name,
            'member': get_attendance_info_type2(lesson),
        }
        data.append(row)

    response_json = json.dumps(data, cls=DjangoJSONEncoder)

    return JsonResponse(response_json, safe=False)


# -------------------------------------------------------------------------------- 회원
# 회원 폼
class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = [
            'name', 'studio', 'status', 'teacher'
        ]
        labels = {
            'name': '이름',
            'studio': '소속지점',
            'status': '회원권',
            'teacher': '담당 강사'
        }

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner')
        super(MemberForm, self).__init__(*args, **kwargs)
        self.fields['studio'].queryset = Studio.objects.filter(owner=owner.id)
        self.fields['teacher'].queryset = User.objects.filter(
            Q(employer=owner.id) | Q(id=owner.id)
        )
        self.fields['teacher'].required = False


class TimeInput(forms.TimeInput):
    input_type = 'time'


# 회원 기본 일정 폼
class MemberDefaultScheduleForm(ModelForm):
    class Meta:
        model = MemberDefaultSchedule
        fields = [
            'day_of_week', 'lesson_time'
        ]
        labels = {
            'day_of_week': '요일',
            'lesson_time': '시간'
        }
        widgets = {
            'lesson_time': TimeInput()
        }


MemberDefaultScheduleFormset = inlineformset_factory(
        Member,
        MemberDefaultSchedule,
        form=MemberDefaultScheduleForm,
        min_num=0,
        max_num=2,
    )


@login_required
@permission_required
def member_index(request):
    context = {}

    active_members = Member.objects.filter(studio__owner=request.user, status=1)
    deactive_members = Member.objects.filter(studio__owner=request.user, status__gt=1)
    total_members = Member.objects.filter(studio__owner=request.user)
    context['active_members'] = active_members
    context['deactive_members'] = deactive_members
    context['total_members'] = total_members

    return render(
        request,
        'studio_app/member_index.html',
        context
    )


# 회원 추가 화면
@login_required
@permission_required
def member_add(request):
    context = {}

    member_form = MemberForm(owner=request.user)
    member_default_schedule_formset = MemberDefaultScheduleFormset()

    if request.POST:
        member_form = MemberForm(request.POST, owner=request.user)
        if member_form.is_valid():
            member = member_form.save(commit=False)
            member.created_by = request.user
            member.updated_by = request.user
            member.save()

            member_default_schedule_formset = MemberDefaultScheduleFormset(request.POST, instance=member)
            if member_default_schedule_formset.is_valid():
                member_default_schedule_formset.save()

                return redirect(member_index)

    context['member_form'] = member_form
    context['member_default_schedule_formset'] = member_default_schedule_formset

    return render(
        request,
        'studio_app/member_set.html',
        context
    )


# 회원 정보 수정 화면
@login_required
@permission_required
def member_chg(request, member_id):
    context = {}

    try:
        member = Member.objects.get(pk=member_id)

        # 만약 회원 소속 지점의 대표와 접속한 사람이 다르다면 화면 진입 막기
        if member.studio.owner != request.user:
            return redirect('/permission-warning/')

        context['member'] = member

    except ObjectDoesNotExist:
        # 이미 삭제된(없는) 회원인 경우 잘못된 접근 화면으로 redirect
        return redirect('/access-warning/')

    member_form = MemberForm(instance=member, owner=request.user)
    member_default_schedule_formset = MemberDefaultScheduleFormset(instance=member)

    if request.POST:
        member_form = MemberForm(request.POST, instance=member, owner=request.user)
        if member_form.is_valid():
            member = member_form.save(commit=False)
            member.updated_by = request.user
            member.save()

            member_default_schedule_formset = MemberDefaultScheduleFormset(request.POST, instance=member)
            if member_default_schedule_formset.is_valid():
                member_default_schedule_formset.save()

                return redirect(member_index)

    context['member_form'] = member_form
    context['member_default_schedule_formset'] = member_default_schedule_formset

    return render(
        request,
        'studio_app/member_set.html',
        context
    )


# 회원 삭제 화면
@login_required
@permission_required
def member_del(request, member_id):
    context = {}

    try:
        member = Member.objects.get(pk=member_id)

        # 만약 회원 소속 지점의 대표와 접속한 사람이 다르다면 화면 진입 막기
        if member.studio.owner != request.user:
            return redirect('/permission-warning/')

        context['member'] = member

    except ObjectDoesNotExist:
        # 이미 삭제된(없는) 회원인 경우 잘못된 접근 화면으로 redirect
        return redirect('/access-warning/')

    if 'delete' in request.POST:
        member.delete()
        return redirect(member_index)
    elif 'disable' in request.POST:
        # 삭제 대신 회원권 만료로 변경
        member.status = 3
        member.save()
        return redirect(member_index)

    return render(
        request,
        'studio_app/member_del.html',
        context
    )


@login_required
@permission_required
def get_membership_of_selected_member(request):
    member_id = request.GET.get('member')
    member = Member.objects.get(pk=member_id)

    data = []
    for membership in member.membership_set.all():
        row = {
            'reg_date': membership.reg_date,
            'reg_amount': '{:,}'.format(membership.reg_amount or 0) + ' 원',
            'payment_method': membership.get_payment_method_display(),
            'number_of_lesson': '{:,}'.format(membership.number_of_lesson or 0) + ' 회',
            'action': '<a href="' + str(member.id) + '/membership/' + str(membership.id) + '/chg/"><span class="badge bg-warning btn">회원권수정</span></a>' +
                      '<a href="' + str(member.id) + '/membership/' + str(membership.id) + '/del/"><span class="badge bg-danger btn">회원권삭제</span></a> '
        }
        data.append(row)

    response_json = json.dumps(data, cls=DjangoJSONEncoder)

    return JsonResponse(response_json, safe=False)


# -------------------------------------------------------------------------------- 회원권(결제)
class MembershipForm(ModelForm):
    class Meta:
        model = Membership
        fields = [
            'reg_date', 'reg_type', 'lesson_type', 'reg_amount', 'number_of_lesson', 'payment_method'
        ]
        labels = {
            'reg_date': '결제일',
            'reg_type': '결제구분',
            'lesson_type': '수업구분',
            'reg_amount': '결제금액',
            'number_of_lesson': '결제횟수',
            'payment_method': '결제수단'
        }
        widgets = {
            'reg_date': DateInput(),
        }


# 회원권 등록 화면
@login_required
@permission_required
def membership_add(request, member_id):
    context = {}

    try:
        member = Member.objects.get(pk=member_id)

        # 만약 회원 소속 지점의 대표와 접속한 사람이 다르다면 화면 진입 막기
        if member.studio.owner != request.user:
            return redirect('/permission-warning/')

        context['member'] = member

    except ObjectDoesNotExist:
        # 이미 삭제된(없는) 회원인 경우 잘못된 접근 화면으로 redirect
        return redirect('/access-warning/')

    membership_form = MembershipForm()

    if request.POST:
        membership_form = MembershipForm(request.POST)
        if membership_form.is_valid():
            membership = membership_form.save(commit=False)
            membership.member = member

            # reg_seq 계산
            membership.reg_seq = member.membership_set.all().count() + 1

            membership.created_by = request.user
            membership.updated_by = request.user
            membership.save()

            return redirect(member_index)

    context['membership_form'] = membership_form

    return render(
        request,
        'studio_app/membership_set.html',
        context
    )


# 회원권 수정 화면
@login_required
@permission_required
def membership_chg(request, member_id, membership_id):
    context = {}

    try:
        member = Member.objects.get(pk=member_id)

        # 만약 회원 소속 지점의 대표와 접속한 사람이 다르다면 화면 진입 막기
        if member.studio.owner != request.user:
            return redirect('/permission-warning/')

        context['member'] = member

        membership = Membership.objects.get(pk=membership_id)
        context['membership'] = membership

    except ObjectDoesNotExist:
        # 이미 삭제된(없는) 회원인 경우 잘못된 접근 화면으로 redirect
        return redirect('/access-warning/')

    membership_form = MembershipForm(instance=membership)

    if request.POST:
        membership_form = MembershipForm(request.POST, instance=membership)
        if membership_form.is_valid():
            membership = membership_form.save(commit=False)
            membership.updated_by = request.user
            membership.save()

            return redirect(member_index)

    context['membership_form'] = membership_form

    return render(
        request,
        'studio_app/membership_set.html',
        context
    )


@login_required
@permission_required
def membership_del(request, member_id, membership_id):
    context = {}

    try:
        member = Member.objects.get(pk=member_id)

        # 만약 회원 소속 지점의 대표와 접속한 사람이 다르다면 화면 진입 막기
        if member.studio.owner != request.user:
            return redirect('/permission-warning/')

        membership = Membership.objects.get(pk=membership_id)

    except ObjectDoesNotExist:
        # 이미 삭제된(없는) 회원 혹은 회원권인 경우 잘못된 접근 화면으로 redirect
        return redirect('/access-warning/')

    # 삭제
    if request.POST:
        # 삭제하고자 하는 회원권보다 seq가 큰 값들 1씩 줄이기
        for temp_membership in Membership.objects.filter(member=member, reg_seq__gt=membership.reg_seq):
            temp_membership.reg_seq = temp_membership.reg_seq - 1
            temp_membership.save()

        membership.delete()
        return redirect(member_index)

    context['member'] = member
    context['membership'] = membership

    return render(
        request,
        'studio_app/membership_del.html',
        context
    )


# -------------------------------------------------------------------------------- 통계(현황)
@login_required
@permission_required
def report_index(request):
    return render(
        request,
        'studio_app/report_index.html'
    )
