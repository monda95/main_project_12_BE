from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from apps.users.models import OAuthAccount


User = get_user_model()


class UserAPITests(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "password123",
            "username": "testuser",
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_signup_success(self):
        """회원가입 성공 테스트"""
        url = reverse("signup")
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "username": "newuser",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=data["email"]).exists())

    def test_signup_duplicate_email(self):
        """중복 이메일로 회원가입 실패 테스트"""
        url = reverse("signup")
        data = {
            "email": self.user_data["email"],
            "password": "password123",
            "username": "anotheruser",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """로그인 성공 및 JWT 토큰 발급 확인 테스트"""
        self.user.email_verified_at = "2024-01-01T00:00:00Z"
        self.user.save()
        url = reverse("login")
        data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_unverified_email(self):
        """이메일 미인증 시 로그인 실패 테스트"""
        with self.settings(AUTH_EMAIL_VERIFICATION_REQUIRED=True):
            url = reverse("login")
            data = {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            }
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data["detail"], "이메일 인증이 필요합니다.")

    def test_login_wrong_password(self):
        """잘못된 비밀번호로 로그인 실패 테스트"""
        url = reverse("login")
        data = {"email": self.user_data["email"], "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        """로그아웃 성공 및 토큰 블랙리스트 확인 테스트"""
        # 1. 로그인하여 refresh 토큰 획득
        self.user.email_verified_at = "2024-01-01T00:00:00Z"
        self.user.save()
        login_url = reverse("login")
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        login_response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        refresh_token = login_response.data["refresh"]

        # 2. 로그아웃 (access token으로 인증 후 refresh token 전달)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )
        logout_url = reverse("logout")
        logout_response = self.client.post(
            logout_url, {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)

        # 3. 블랙리스트에 추가된 refresh 토큰으로 갱신 시도
        refresh_url = reverse("token_refresh")
        refresh_response = self.client.post(
            refresh_url, {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(refresh_response.data["code"], "token_not_valid")

    def test_user_detail_get(self):
        """사용자 정보 조회 테스트"""
        self.client.force_authenticate(user=self.user)
        url = reverse("me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user_data["email"])

    def test_user_detail_update(self):
        """사용자 정보 수정 테스트"""
        self.client.force_authenticate(user=self.user)
        url = reverse("me")
        data = {"username": "updateduser", "nickname": "updatednick"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, data["username"])
        self.assertEqual(self.user.nickname, data["nickname"])

    def test_user_detail_delete(self):
        """회원 탈퇴 (Soft Delete) 테스트"""
        self.client.force_authenticate(user=self.user)
        url = reverse("me")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertIsNotNone(self.user.deactivated_at)

    def test_password_change_success(self):
        """비밀번호 변경 성공 테스트"""
        self.client.force_authenticate(user=self.user)
        url = reverse("password_change")
        data = {
            "current_password": self.user_data["password"],
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(data["new_password"]))

    def test_password_change_wrong_current_password(self):
        """현재 비밀번호 불일치 시 비밀번호 변경 실패 테스트"""
        self.client.force_authenticate(user=self.user)
        url = reverse("password_change")
        data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_mismatched_new_passwords(self):
        """새 비밀번호 불일치 시 비밀번호 변경 실패 테스트"""
        self.client.force_authenticate(user=self.user)
        url = reverse("password_change")
        data = {
            "current_password": self.user_data["password"],
            "new_password": "newpassword123",
            "new_password_confirm": "anotherpassword",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password_confirm", response.data)


class OAuthFlowTests(TestCase):
    @patch("apps.users.views.requests.post")
    @patch("apps.users.views.requests.get")
    def test_github_oauth_exchange_success(self, mock_get, mock_post):
        """GitHub OAuth code 교환이 성공적으로 토큰과 유저 정보를 반환하는지 확인"""
        # Mock GitHub API responses
        mock_post.return_value.json.return_value = {"access_token": "fake_access_token"}
        mock_get.return_value.json.return_value = {
            "id": "12345",
            "email": "test@github.com",
            "login": "testuser",
        }

        url = reverse("github_exchange")
        response = self.client.get(url, {"code": "dummy_code"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertEqual(data["user"]["email"], "test@github.com")

    def test_github_oauth_missing_code(self):
        """code 파라미터가 없을 때 400 에러 발생 확인"""
        url = reverse("github_exchange")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "missing code"})

    @patch("apps.users.views.requests.post")
    def test_github_oauth_exchange_invalid_code(self, mock_post):
        """GitHub 토큰 교환 시 에러가 발생했을 때 테스트"""
        mock_post.return_value.json.return_value = {
            "error": "bad_verification_code",
            "error_description": "The code passed is incorrect or expired.",
        }

        url = reverse("github_exchange")
        response = self.client.get(url, {"code": "dummy_code"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    @patch("apps.users.views.requests.get")
    @patch("apps.users.views.requests.post")
    def test_github_oauth_get_user_info_fails(self, mock_post, mock_get):
        """GitHub 사용자 정보 조회 실패 시 테스트"""
        mock_post.return_value.json.return_value = {"access_token": "fake_access_token"}

        # 사용자 정보 조회 실패 모의
        mock_get.return_value.status_code = 401
        mock_get.return_value.json.return_value = {"message": "Bad credentials"}

        url = reverse("github_exchange")
        response = self.client.get(url, {"code": "dummy_code"})

        self.assertEqual(response.status_code, 401)

    def test_github_oauth_existing_oauth_account(self, mock_post, mock_get):
        """기존에 연동된 소셜 계정으로 로그인하는 경우 테스트"""
        # 1. 기존 유저 및 소셜 계정 생성
        existing_user = User.objects.create_user(
            email="existing@example.com", password="password123"
        )
        OAuthAccount.objects.create(
            user=existing_user,
            provider="github",
            subject="12345",
        )

        # 2. API 모의 응답 설정 (위에서 생성한 subject와 동일하게)
        mock_post.return_value.json.return_value = {"access_token": "fake_access_token"}
        mock_get.return_value.json.return_value = {
            "id": "12345",
            "email": "test@github.com",
            "login": "testuser",
        }

        # 3. API 호출
        url = reverse("github_exchange")
        response = self.client.get(url, {"code": "dummy_code"})

        # 4. 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["id"], existing_user.id)
        self.assertEqual(
            User.objects.count(), 2
        )  # setUp에서 만든 유저 + 여기서 만든 유저
        self.assertEqual(OAuthAccount.objects.count(), 1)


class TemplateRenderTests(TestCase):
    def test_login_page_renders(self):
        resp = self.client.get("/login/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "로그인")

    def test_signup_page_renders(self):
        resp = self.client.get("/signup/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "회원가입")

    def test_dashboard_page_renders(self):
        resp = self.client.get("/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Dashboard")

    def test_conversation_page_renders(self):
        resp = self.client.get("/conversation/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "대화")


class SignupPageViewTests(TestCase):
    def setUp(self):
        self.url = reverse("signup-page")

    @patch("apps.users.views.send_verification_email")
    @patch("apps.users.views.transaction.on_commit")
    def test_signup_page_post_success(self, mock_on_commit, mock_send_email):
        mock_on_commit.side_effect = lambda func: func()

        payload = {
            "email": "pageuser@example.com",
            "password": "password123",
            "password_confirm": "password123",
        }

        response = self.client.post(self.url, payload)

        self.assertRedirects(response, reverse("login-page"))
        self.assertTrue(User.objects.filter(email=payload["email"]).exists())
        mock_on_commit.assert_called_once()
        mock_send_email.assert_called_once()
        created_user = User.objects.get(email=payload["email"])
        _, called_user = mock_send_email.call_args[0]
        self.assertEqual(called_user, created_user)

    def test_signup_page_post_duplicate_email_shows_error(self):
        User.objects.create_user(
            email="duplicate@example.com",
            password="password123",
            username="dupuser",
        )

        payload = {
            "email": "duplicate@example.com",
            "password": "password123",
            "password_confirm": "password123",
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "이미 사용 중인 이메일입니다.")


class EmailVerificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="unverified@example.com", password="password123"
        )

    def test_verify_email_success(self):
        """이메일 인증 성공 테스트"""
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse("verify_email", kwargs={"uidb64": uid, "token": token})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.email_verified_at)
        self.assertEqual(self.user.role, "user")

    def test_verify_email_invalid_token(self):
        """잘못된 토큰으로 이메일 인증 실패 테스트"""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse("verify_email", kwargs={"uidb64": uid, "token": "invalid-token"})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

        self.user.refresh_from_db()
        self.assertIsNone(self.user.email_verified_at)
