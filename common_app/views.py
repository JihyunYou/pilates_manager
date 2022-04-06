from django import forms
from django.contrib import auth, messages
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm
from django.shortcuts import render, redirect

from common_app.models import User


def login(request):
    print('로그인 창 진입')
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            print('로그인 실패')
            return render(
                request,
                'common_app/log-in.html',
                {
                    'error': '로그인 정보가 잘못되었습니다'
                }
            )

    return render(
        request,
        'common_app/log-in.html'
    )


def permission_warning(request):
    return render(
        request,
        'common_app/warning.html',
        context={
            'error_msg': '권한이 없습니다'
        }
    )


def access_warning(request):
    return render(
        request,
        'common_app/warning.html',
        context={
            'error_msg': '잘못된 접근입니다'
        }
    )


def logout(request):
    auth.logout(request)
    return redirect('/')


def check_permission(request):
    if not request.user.user_type <= 2:
        return False
    else:
        return True


# -------------------------------------------------------------------------------- 프로필
# class ProfileForm(UserChangeForm):
#     class Meta:
#         model = User
#         fields = [
#             'password', 'password1', 'password2'
#         ]
#         labels = {
#
#             'password': '기존 비밀번호',
#         }


@login_required
def profile(request):
    return render(
        request,
        'common_app/profile.html'
    )


@login_required
def profile_chg(request, user_id):
    context = {}

    try:
        user = User.objects.get(pk=user_id)
        # 만약 프로필 수정페이지와 접속한 사람이 다르다면 화면 진입 막기
        if user != request.user:
            return redirect('/permission-warning/')
    except ObjectDoesNotExist:
        return redirect('/access-warning/')

    profile_form = PasswordChangeForm(user)

    if request.POST:
        profile_form = PasswordChangeForm(user, request.POST)
        if profile_form.is_valid():
            user = profile_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')

            return redirect(profile)
        else:
            messages.error(request, '잘못된 입력입니다')

    context['profile_form'] = profile_form

    return render(
        request,
        'common_app/profile_chg.html',
        context
    )