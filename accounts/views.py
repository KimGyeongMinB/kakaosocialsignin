import uuid
from django.shortcuts import redirect, render
import requests
from accounts.models import User
from config import settings
from rest_framework.views import APIView
from rest_framework.response import Response

# kakao social sign_in

# 백엔드에서 해야할 순서
# 인가 코드발급
# 토큰 발급
# 요청 검증 및 처리 
KAKAO_CALLBACK_URI = 'http://127.0.0.1:8000/accounts/kakao/callback' # 프론트 배포 페이지의 callback uri


# 인증 및 동의 요청
# REST_API_KEY == 원래는 .env 등에 보관해야함
def kakao_login(request):
    rest_api_key = settings.KAKAO_REST_API_KEY
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )


# 1. ---인가 코드 발급---
class Kakaoauthorize(APIView):
    def get(self, request):
        try :
            client_id = settings.KAKAO_REST_API_KEY 
            redirect_uri = 'http://127.0.0.1:8000/accounts/kakao/callback'
            # scope = 추가 동의 항목
            response_type = 'code'
            # state 랜덤생성
            # Cross-Site Request Forgery(CSRF) 공격으로부터 카카오 로그인 요청을 보호하기 위해 사용
            state = str(uuid.uuid4())
            
            # 카카오 인증 URL 생성 
            # 기본 uri https://kauth.kakao.com/oauth/authorize
            kakao_auth_url = ( 
            f"https://kauth.kakao.com/oauth/authorize?" 
            f"client_id={client_id}&redirect_uri={redirect_uri}"
            f"&response_type={response_type}&state={state}" 
            )

            # 생성한 state 값을 세션에 저장하여 나중에 검증 시 사용 
            request.session['kakao_state'] = state

            # 카카오 인증 uri 로 리다이렉트
            return redirect(kakao_auth_url)

        # 실패할 경우
        except Exception as e: 
            return requests.Response({"error": str(e)}, status=500)

# kakao callback 단계       
# 인가 코드로 토큰 발급을 요청합니다.
#  인가 코드 받기만으로는 카카오 로그인이 완료되지 않으며, 
# 토큰 받기까지 마쳐야 카카오 로그인을 정상적으로 완료할 수 있습니다.
# 필수 파라미터를 포함해 POST로 요청합니다. 요청 성공 시 응답은 토큰과 토큰 정보를 포함합니다.

# 2. ---token 발급---
class Kakaocallback(APIView):
    def get(self, request):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        # grant_type 은 authorization_code 로 고정
        grant_type = "authorization_code"
        client_id = settings.KAKAO_REST_API_KEY
        redirect_uri = 'http://127.0.0.1:8000/accounts/kakao/callback'
        # 인가코드 받기에서 얻은 코드 가져오기
        code = request.GET.get('code')

        data = {
            'grant_type': grant_type,
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'code': code,
        }

        # 사용자가 요청 보낼 url 주소
        token_url = "https://kauth.kakao.com/oauth/token"
        
        try:
            # post 요청
            token_posts = requests.post(token_url, data=data, headers=headers)
            token_req_json = token_posts.json()

            # access_token 및 refresh_token 추출
            access_token = token_req_json.get('access_token')
            # refresh_token = token_req_json.get('refresh_token')

            if not access_token:
                return Response({"error": "access_token이 없습니다.", "details": token_req_json}, status=400)
            
            # 사용자 정보 가져오기
            user_info_url = "https://kapi.kakao.com/v2/user/me"
            user_headers = {
                "Authorization": f"Bearer {access_token}"
            }
            user_info_response = requests.get(user_info_url, headers=user_headers)
            user_info = user_info_response.json()

            # 사용자 정보에서 필요한 데이터 추출
            kakao_account = user_info.get("kakao_account", {})
            profile = kakao_account.get("profile", {})
            nickname = profile.get('nickname')


        # 3. ---사용자 인증---
            #사용자 정보로 로그인 처리 또는 사용자 생성
            user, created = User.objects.get_or_create(username=f"kakao_{user_info['id']}")
            if created:
                user.first_name = nickname
                user.save()

            #성공 응답
            return Response({
                "message": "카카오 로그인 성공",
                "user": {
                    "username": user.username,
                    "nickname": user.first_name,
                },
            })

        except requests.exceptions.RequestException as e:
            return Response({"error": "카카오 API 요청 실패", "details": str(e)}, status=500)

        





