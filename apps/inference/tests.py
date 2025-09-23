import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.conversations.models import Conversation, Message
from .models import InferenceRun

User = get_user_model()


@pytest.mark.django_db
class TestInferenceAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.auth_conversation = Conversation.objects.create(
            owner=self.user, title="Authenticated Conversation"
        )
        self.unauth_conversation = Conversation.objects.create(
            owner=None, title="Unauthenticated Conversation"
        )
        self.mock_api_success_response = {
            "ai_content": "This is a mock AI response.",
            "latency_ms": 123,
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "status": "success",
            "error_code": None,
            "error_message": None,
        }

    @patch("apps.inference.views.call_gemini_api")
    def test_inference_success_authenticated(self, mock_call_gemini):
        """인증된 사용자의 성공적인 추론 요청 테스트"""
        mock_call_gemini.return_value = self.mock_api_success_response
        self.client.force_authenticate(user=self.user)

        payload = {
            "conversation_id": self.auth_conversation.id,
            "prompt": "Hello AI",
        }
        response = self.client.post("/api/v1/inference/", payload)

        assert response.status_code == 201
        assert "message_id" in response.data
        assert response.data["content"] == "This is a mock AI response."
        assert Message.objects.filter(role="user", content="Hello AI").exists()
        assert Message.objects.filter(role="assistant").exists()
        assert InferenceRun.objects.filter(
            conversation=self.auth_conversation, status="success"
        ).exists()

    @patch("apps.inference.views.call_gemini_api")
    def test_inference_success_unauthenticated(self, mock_call_gemini):
        """미인증 사용자의 성공적인 추론 요청 테스트"""
        mock_call_gemini.return_value = self.mock_api_success_response

        payload = {
            "conversation_id": self.unauth_conversation.id,
            "prompt": "Hello AI from guest",
        }
        response = self.client.post("/api/v1/inference/", payload)

        assert response.status_code == 201
        assert InferenceRun.objects.filter(
            conversation=self.unauth_conversation, status="success"
        ).exists()

    @patch("apps.inference.views.call_gemini_api")
    def test_inference_wrong_user_fails(self, mock_call_gemini):
        """다른 사용자의 대화에 추론 요청 시 실패 테스트"""
        another_user = User.objects.create_user(
            email="another@example.com", password="password123"
        )
        self.client.force_authenticate(user=another_user)

        payload = {
            "conversation_id": self.auth_conversation.id,
            "prompt": "Trying to use other's conversation",
        }
        response = self.client.post("/api/v1/inference/", payload)

        assert response.status_code == 404

    @patch("apps.inference.views.call_gemini_api")
    def test_inference_api_call_failure(self, mock_call_gemini):
        """API 호출 실패 시 에러 처리 테스트"""
        mock_call_gemini.return_value = {
            "ai_content": "API 호출 중 오류 발생",
            "latency_ms": 50,
            "prompt_tokens": None,
            "completion_tokens": None,
            "status": "error",
            "error_code": "HTTP_500",
            "error_message": "Internal Server Error",
        }
        self.client.force_authenticate(user=self.user)

        payload = {
            "conversation_id": self.auth_conversation.id,
            "prompt": "This will fail",
        }
        response = self.client.post("/api/v1/inference/", payload)

        assert response.status_code == 201  # The view itself succeeds
        assert response.data["content"] == "API 호출 중 오류 발생"

        run_log = InferenceRun.objects.get(conversation=self.auth_conversation)
        assert run_log.status == "error"
        assert run_log.error_code == "HTTP_500"
