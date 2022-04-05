from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from studio_app.models import Studio


@login_required
def index(request):
    context = {}

    # 대표인 경우
    if request.user.user_type == 2:
        studios = Studio.objects.filter(owner=request.user)
    # 강사인 경우
    elif request.user.user_type == 3:
        studios = request.user.StudioTeachers.all()

    context['studios'] = studios

    return render(
        request,
        'dashboard_app/dashboard.html',
        context
    )
