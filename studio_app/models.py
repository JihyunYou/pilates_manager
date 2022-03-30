from django.db import models
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
