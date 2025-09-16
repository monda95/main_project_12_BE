import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestUserAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "Str0ngPass!",
            "new_password": "EvenStronger#1",
        }

    def test_signup_success(self):
        """회원가입 성공 테스트"""
        response = self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": self.user_data["email"],
                "username": self.user_data["username"],
                "password": self.user_data["password"],
            },
        )
        assert response.status_code == 201
        assert User.objects.filter(email=self.user_data["email"]).exists()

    def test_signup_duplicate_email_fails(self):
        """이메일 중복 시 회원가입 실패 테스트"""
        # 첫 번째 사용자 생성
        User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            username=self.user_data["username"],
        )
        # 동일한 이메일로 가입 시도
        response = self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": self.user_data["email"],
                "username": "anotheruser",
                "password": self.user_data["password"],
            },
        )
        assert response.status_code == 400
        assert response.json()["email"][0] == "이미 사용 중인 이메일입니다."

    def test_login_success_and_get_tokens(self):
        """로그인 성공 및 토큰 발급 테스트"""
        User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            username=self.user_data["username"],
        )
        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
        )
        assert response.status_code == 200
        assert "access" in response.json()
        assert "refresh" in response.json()

    def test_get_user_me_success(self):
        """인증된 사용자의 내 정보 조회 테스트"""
        user = User.objects.create_user(
            email=self.user_data["email"], password=self.user_data["password"]
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/v1/users/me/")
        assert response.status_code == 200
        assert response.json()["email"] == self.user_data["email"]

    def test_password_change_success(self):
        """비밀번호 변경 성공 테스트"""
        user = User.objects.create_user(
            email=self.user_data["email"], password=self.user_data["password"]
        )
        self.client.force_authenticate(user=user)

        response = self.client.put(
            "/api/v1/users/me/password/",
            {
                "current_password": self.user_data["password"],
                "new_password": self.user_data["new_password"],
                "new_password_confirm": self.user_data["new_password"],
            },
        )
        assert response.status_code == 200
        assert response.json()["detail"] == "비밀번호가 변경되었습니다."

        # 변경된 비밀번호로 로그인 테스트
        login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": self.user_data["email"],
                "password": self.user_data["new_password"],
            },
        )
        assert login_response.status_code == 200

    def test_password_change_wrong_current_password_fails(self):
        """현재 비밀번호 불일치 시 변경 실패 테스트"""
        user = User.objects.create_user(
            email=self.user_data["email"], password=self.user_data["password"]
        )
        self.client.force_authenticate(user=user)

        response = self.client.put(
            "/api/v1/users/me/password/",
            {
                "current_password": "wrongpassword",
                "new_password": self.user_data["new_password"],
                "new_password_confirm": self.user_data["new_password"],
            },
        )
        assert response.status_code == 400
        assert (
            "현재 비밀번호가 일치하지 않습니다." in response.json()["current_password"]
        )

    def test_logout_success(self):
        """로그아웃 성공 (refresh 토큰 블랙리스트) 테스트"""
        user = User.objects.create_user(
            email=self.user_data["email"], password=self.user_data["password"]
        )
        self.client.force_authenticate(user=user)

        # 로그인해서 refresh 토큰 받기
        login_resp = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
        )
        refresh_token = login_resp.json()["refresh"]

        # 로그아웃
        logout_resp = self.client.post(
            "/api/v1/auth/logout/", {"refresh": refresh_token}
        )
        assert logout_resp.status_code == 204

        # 블랙리스트 처리된 토큰으로 refresh 시도 시 실패해야 함
        refresh_resp = self.client.post(
            "/api/v1/auth/refresh/", {"refresh": refresh_token}
        )
        assert refresh_resp.status_code == 401
