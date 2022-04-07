from django.db import models

from common_app.const_info.const_info import LESSON_TYPE, REGISTRATION_TYPE, PAYMENT_METHOD
from pilates_manager_proj import settings


class Studio(models.Model):
    name = models.CharField(
        max_length=30,
        null=False
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    address = models.CharField(
        max_length=100,
        null=True
    )

    # 강사와 센터는 다대다 관계
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='StudioTeachers',
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='StudioCreatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='StudioUpdatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


MEMBER_STATUS = [
    (1, '활성'), (2, '일시중지'), (3, '만료')
]


class Member(models.Model):
    name = models.CharField(max_length=10)
    # 소속 지점
    studio = models.ForeignKey(
        Studio,
        on_delete=models.SET_NULL,
        null=True
    )
    # 담당 강사
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='MemberTeacher',
        on_delete=models.SET_NULL,
        null=True
    )
    # 회원권 상태
    status = models.IntegerField(
        choices=MEMBER_STATUS,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='MemberCreatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='MemberUpdatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


DAY_OF_WEEK = [
    (1, '월요일'), (2, '화요일'), (3, '수요일'), (4, '목요일'), (5, '금요일'), (6, '토요일'), (7, '일요일'),
]


# 회원별 기본 강습 스케쥴
class MemberDefaultSchedule(models.Model):
    # 회원 삭제시 함께 삭제
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE
    )
    # 요일
    day_of_week = models.IntegerField(
        choices=DAY_OF_WEEK,
        null=True
    )
    # 시간
    lesson_time = models.TimeField(
        null=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='MemberDefaultScheduleCreatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='MemberDefaultScheduleUpdatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'day_of_week', 'lesson_time'],
                name='unique_member_default_schedule'
            )
        ]
        ordering = ['member', 'day_of_week']


class Membership(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE
    )
    # 등록 구분
    reg_type = models.IntegerField(
        choices=REGISTRATION_TYPE
    )
    # 수업 구분
    lesson_type = models.IntegerField(
        choices=LESSON_TYPE
    )
    # 재등록 횟수
    reg_seq = models.IntegerField(null=True)
    # 등록한 수업 횟수
    number_of_lesson = models.IntegerField(null=True)
    # 결제 금액
    reg_amount = models.IntegerField(null=True)
    # 결제일
    reg_date = models.DateField(null=True)
    # 결제 수단
    payment_method = models.IntegerField(
        choices=PAYMENT_METHOD,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='MembershipCreatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='MembershipUpdatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['member', 'reg_seq']