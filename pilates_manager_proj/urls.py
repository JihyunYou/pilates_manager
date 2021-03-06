"""pilates_manager_proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

import common_app.views
import dashboard_app.views
import lesson_app.views
import studio_app.views
from pilates_manager_proj import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    # Profile
    path('profile/', common_app.views.profile),
    path('profile/<int:user_id>/chg/', common_app.views.profile_chg),

    # Dashboard
    path('', dashboard_app.views.index),
    path('get_dashboard_resources/', dashboard_app.views.get_dashboard_resources),
    path('get_dashboard_events/', dashboard_app.views.get_dashboard_events),

    path('add_lesson_by_schedule/', lesson_app.views.add_lesson_by_schedule),
    path('add_weekly_lesson_by_schedule/', lesson_app.views.add_weekly_lesson_by_schedule),
    path('set_attendance_by_schedule/', lesson_app.views.set_attendance_by_schedule),

    # common_app
    path('log-in/', common_app.views.login),
    path('log-out/', common_app.views.logout),
    path('permission-warning/', common_app.views.permission_warning),
    path('access-warning/', common_app.views.access_warning),

    # studio_app
    path('studio/', studio_app.views.studio_index),
    path('studio/add/', studio_app.views.studio_add),
    path('studio/<int:studio_id>/chg/', studio_app.views.studio_chg),
    path('studio/<int:studio_id>/del/', studio_app.views.studio_del),

    path('get_teachers_of_selected_studio/', studio_app.views.get_teachers_of_selected_studio),
    path('get_members_of_selected_studio/', studio_app.views.get_members_of_selected_studio),

    path('teacher/', studio_app.views.teacher_index),
    path('teacher/add/', studio_app.views.teacher_add),
    path('teacher/<int:teacher_id>/chg/', studio_app.views.teacher_chg),
    path('teacher/<int:teacher_id>/del/', studio_app.views.teacher_del),

    path('get_lesson_of_selected_teacher/', studio_app.views.get_lesson_of_selected_teacher),

    path('member/', studio_app.views.member_index),
    path('member/add/', studio_app.views.member_add),
    path('member/<int:member_id>/chg/', studio_app.views.member_chg),
    path('member/<int:member_id>/del/', studio_app.views.member_del),

    path('get_membership_of_selected_member/', studio_app.views.get_membership_of_selected_member),

    path('member/<int:member_id>/membership/add/', studio_app.views.membership_add),
    path('member/<int:member_id>/membership/<int:membership_id>/chg/', studio_app.views.membership_chg),
    path('member/<int:member_id>/membership/<int:membership_id>/del/', studio_app.views.membership_del),

    # ?????? ??????
    path('report/', studio_app.views.report_index),
    path('get_year_report/', studio_app.views.get_year_report),

    # ?????? ?????? ?????? ??????
    path('admin_lesson/', common_app.views.develop_page),

    # F.A.Q
    path('f_a_q/', common_app.views.develop_page),

    # lesson_app
    path('teaching_member/', lesson_app.views.member_index),

    path('lesson/', lesson_app.views.lesson_index),
    path('lesson/add/', lesson_app.views.lesson_add),
    path('lesson/<int:lesson_id>/chg/', lesson_app.views.lesson_chg),
    path('lesson/<int:lesson_id>/del/', lesson_app.views.lesson_del),

    path('get_attendance_of_selected_lesson/', lesson_app.views.get_attendance_of_selected_lesson),
    path('set_attendance/', lesson_app.views.set_attendance),
    path('del_lesson_by_schedule/', lesson_app.views.del_lesson_by_schedule),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)