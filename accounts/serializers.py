from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at', 'updated_at']  # 포함할 필드 목록
        read_only_fields = ['created_at', 'updated_at']  # 읽기 전용 필드
