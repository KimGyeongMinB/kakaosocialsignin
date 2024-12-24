from django.urls import path
from .views import kakao_login, Kakaocallback  # views에서 함수와 클래스를 임포트하세요

app_name = 'accounts'

urlpatterns = [
    # 카카오 로그인 페이지로 리다이렉트
    path('kakao/login/', kakao_login, name='kakao-login'),
    
    # 카카오 로그인 콜백 처리
    path('kakao/callback/', Kakaocallback.as_view(), name='kakao-callback'),
]
