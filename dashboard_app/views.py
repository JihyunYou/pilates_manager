from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from studio_app.models import Studio


@login_required
def index(request):
    context = {}

    studios = Studio.objects.filter(owner=request.user)
    context['studios'] = studios

    return render(
        request,
        'dashboard_app/dashboard.html',
        context
    )
