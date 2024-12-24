from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간 (자동 설정)
    updated_at = models.DateTimeField(auto_now=True)     # 수정 시간 (자동 갱신)

    def __str__(self):
        return self.username

