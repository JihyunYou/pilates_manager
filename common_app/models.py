from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        user = self.model(
            email=email,
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(
            email,
            name=name,
            password=password,
        )

        user.is_admin = True
        user.save(using=self._db)
        return user


USER_TYPE = [
    (1, '관리자'),
    (2, '대표'),
    (3, '강사'),
    (4, '회원'),
]


class User(AbstractBaseUser, PermissionsMixin):
    # Custom 헬퍼 클래스를 사용하도록 설정
    objects = UserManager()

    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    USERNAME_FIELD = 'email'  # Username을 email로 명시

    name = models.CharField(
        verbose_name='name',
        max_length=10,
        null=False
    )

    user_type = models.IntegerField(
        choices=USER_TYPE,
        default=3,
    )

    # 강사만 가지는 컬럼
    # 고용주
    employer = models.ForeignKey(
        'self',
        related_name='Employer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True  # Admin 페이지에서 입력 필수 해제
    )
    # 회당 강습비
    lesson_fee = models.IntegerField(null=True, blank=True)
    # 고용 시작일 / 종료일
    employment_start_date = models.DateField(null=True, blank=True)
    employment_end_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        'self',
        related_name='UserCreatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        'self',
        related_name='UserUpdatedBy',
        on_delete=models.SET_NULL,
        null=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    # REQUIRED_FIELDS 안 쓰면 createsuperuser 할 때 안 나타남
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name

    # 커스텀 유저 모델을 기본 유저 모델로 사용하기 위해 구현한 부분
    #   True를 반환하여 권한이 있음을 알림
    def has_perm(self, perm, obj=None):
        return True

    #   True를 반환하여 주어진 App의 모델에 접근 가능하도록 함
    def has_module_perms(self, app_label):
        return True

    #   True 가 반환되면 관리자 화면에 로그인 가능
    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        ordering = ['user_type', 'name']