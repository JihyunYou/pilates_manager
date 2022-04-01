from django.contrib import auth
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect


def login(request):
    print('로그인 창 진입')
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect(index)
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
    return redirect(index)


def check_permission(request):
    if not request.user.user_type <= 2:
        return False
    else:
        return True
