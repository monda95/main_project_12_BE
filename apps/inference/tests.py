import pytest
import json
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.conversations.models import Conversation, Message
from .models import InferenceRun
from .services import InferenceService

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
            "ai_content": json.dumps(
                {
                    "nutrition": {
                        "calories": 200,
                        "carbohydrates": 20,
                        "protein": 10,
                        "fat": 9,
                    },
                    "allergy": "None",
                    "storage": "Store in a cool place",
                    "processing": "Cook well",
                    "source": "Internal data",
                }
            ),
            "latency_ms": 123,
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "status": "success",
            "error_code": None,
            "error_message": None,
        }

    @patch("apps.inference.services.InferenceService.call_gemini_api")
    def test_inference_success_authenticated(self, mock_call_gemini):
        """인증된 사용자의 성공적인 추론 요청 테스트"""
        mock_call_gemini.return_value = self.mock_api_success_response
        self.client.force_authenticate(user=self.user)

        payload = {
            "conversation_id": self.auth_conversation.id,
            "prompt": "Hello AI",
        }
        response = self.client.post("/api/v1/inference/", payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "message_id" in response.data
        assert Message.objects.filter(role="user", content="Hello AI").exists()
        assert Message.objects.filter(role="assistant").exists()
        assert InferenceRun.objects.filter(
            conversation=self.auth_conversation, status="success", check_pass=True
        ).exists()

    @patch("apps.inference.services.InferenceService.call_gemini_api")
    def test_inference_api_call_failure(self, mock_call_gemini):
        """API 호출 실패 시 502 에러 처리 테스트"""
        mock_call_gemini.return_value = {
            "status": "error",
            "error_code": "HTTP_500",
            "error_message": "Internal Server Error",
        }
        self.client.force_authenticate(user=self.user)

        payload = {
            "conversation_id": self.auth_conversation.id,
            "prompt": "This will fail",
        }
        response = self.client.post("/api/v1/inference/", payload, format="json")

        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        run_log = InferenceRun.objects.get(conversation=self.auth_conversation)
        assert run_log.status == "error"
        assert run_log.error_code == "HTTP_500"

    @patch("apps.inference.services.InferenceService.call_gemini_api")
    def test_inference_self_check_retry_success(self, mock_call_gemini):
        """Self-Check 실패 후 재시도 성공 테스트"""
        failed_response = self.mock_api_success_response.copy()
        failed_response["ai_content"] = json.dumps(
            {"nutrition": "missing other fields"}
        )

        mock_call_gemini.side_effect = [
            failed_response,  # 1st call fails self-check
            self.mock_api_success_response,  # 2nd call passes
        ]

        self.client.force_authenticate(user=self.user)
        payload = {"prompt": "Give me data"}
        response = self.client.post("/api/v1/inference/", payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert mock_call_gemini.call_count == 2
        run_log = InferenceRun.objects.latest("created_at")
        assert run_log.retry_used is True
        assert run_log.check_pass is True


class TestSelfCheckLogic:
    def test_self_check_pass(self):
        content = json.dumps(
            {
                "nutrition": {
                    "calories": 209,
                    "carbohydrates": 20,
                    "protein": 10,
                    "fat": 9,
                },
                "allergy": "None",
                "storage": "...",
                "processing": "...",
                "source": "USDA",
            }
        )
        result = InferenceService._self_check(content)
        assert result["check_pass"] is True

    def test_self_check_missing_section(self):
        content = json.dumps({"nutrition": {}, "allergy": "None"})
        result = InferenceService._self_check(content)
        assert result["check_pass"] is False
        assert any(v["code"] == "MISSING_SECTION" for v in result["violations"])

    def test_self_check_calorie_conflict(self):
        # (20*4) + (10*4) + (9*9) = 80 + 40 + 81 = 201. 명시된 300과 15% 이상 차이
        content = json.dumps(
            {
                "nutrition": {
                    "calories": 300,
                    "carbohydrates": 20,
                    "protein": 10,
                    "fat": 9,
                },
                "allergy": "None",
                "storage": "...",
                "processing": "...",
                "source": "USDA",
            }
        )
        result = InferenceService._self_check(content)
        assert result["check_pass"] is False
        assert any(v["code"] == "CALORIE_CONFLICT" for v in result["violations"])

    def test_self_check_invalid_json(self):
        content = "not a valid json"
        result = InferenceService._self_check(content)
        assert result["check_pass"] is False
        assert any(v["code"] == "INVALID_FORMAT" for v in result["violations"])
