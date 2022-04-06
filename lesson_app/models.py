from django.db import models

from pilates_manager_proj import settings
from studio_app.models import Member, Studio


LESSON_TYPE = [
    (1, '싱글'), (2, '듀엣')
]


class Lesson(models.Model):
    lesson_date = models.DateField()
    lesson_time = models.TimeField()

    studio = models.ForeignKey(
        Studio,
        on_delete=models.SET_NULL,
        null=True
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    lesson_type = models.IntegerField(
        choices=LESSON_TYPE,
        null=True
    )

    members = models.ManyToManyField(Member, through='Attendance')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='LessonCreatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='LessonUpdatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['lesson_date', 'lesson_time', 'teacher'],
                name='unique_lesson',
            )
        ]
        ordering = ['-lesson_date', 'lesson_time']


ATTENDANCE_STATUS = [
    (1, '수업 예정'), (2, '수업 완료'), (3, '사전 취소'), (4, '당일 취소'), (5, '일시 중지')
]


class Attendance(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='lesson_related_attendance', on_delete=models.CASCADE)
    member = models.ForeignKey(Member, related_name='lesson_related_attendance', on_delete=models.CASCADE)

    status = models.IntegerField(
        choices=ATTENDANCE_STATUS,
        default=1
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='AttendanceCreatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='AttendanceUpdatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    updated_at = models.DateTimeField(auto_now=True)
