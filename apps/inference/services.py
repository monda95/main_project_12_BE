import time
import requests
import logging
import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.conversations.models import Conversation, Message
from apps.search.models import SearchLog
from .models import InferenceRun
from apps.users.models import User

logger = logging.getLogger(__name__)

# DB 제약과 일치시키기
ERROR_CODE_MAX = 128
ERROR_MESSAGE_MAX = 8192


def _truncate(s: str | None, limit: int) -> str | None:
    if s is None:
        return None
    return s if len(s) <= limit else (s[: limit - 3] + "...")


class InferenceService:
    """Gemini API 호출 및 Inference 파이프라인"""

    @staticmethod
    def call_gemini_api(prompt_content: str, options: dict = None) -> dict:
        if options is None:
            options = {}

        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return {
                "ai_content": "설정 오류",
                "latency_ms": 0,
                "prompt_tokens": None,
                "completion_tokens": None,
                "status": "error",
                "error_code": "ConfigError",
                "error_message": _truncate(
                    "GEMINI_API_KEY가 설정되지 않았습니다.", ERROR_MESSAGE_MAX
                ),
            }

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.GEMINI_MODEL_NAME}:generateContent?key={api_key}"
        )
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt_content}]}],
            "generationConfig": options,
        }

        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            latency_ms = int((time.time() - start_time) * 1000)
            data = response.json()

            ai_content = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            ) or "API 응답을 받지 못했습니다."

            usage = data.get("usageMetadata", {}) or {}
            return {
                "ai_content": ai_content,
                "latency_ms": latency_ms,
                "prompt_tokens": usage.get("prompt_token_count"),
                "completion_tokens": usage.get("candidates_token_count"),
                "status": "success",
                "error_code": None,
                "error_message": None,
            }

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            error_code = f"HTTP_{status_code}"
            try:
                body_text = e.response.json().get("error", {}).get("message") or str(
                    e.response.json()
                )
            except Exception:
                body_text = e.response.text or str(e)
            return {
                "ai_content": "API 호출 중 오류 발생",
                "latency_ms": int((time.time() - start_time) * 1000),
                "prompt_tokens": None,
                "completion_tokens": None,
                "status": "error",
                "error_code": _truncate(error_code, ERROR_CODE_MAX),
                "error_message": _truncate(body_text, ERROR_MESSAGE_MAX),
            }

        except requests.exceptions.RequestException as e:
            return {
                "ai_content": "API 호출 중 오류 발생",
                "latency_ms": int((time.time() - start_time) * 1000),
                "prompt_tokens": None,
                "completion_tokens": None,
                "status": "error",
                "error_code": _truncate(e.__class__.__name__, ERROR_CODE_MAX),
                "error_message": _truncate(str(e), ERROR_MESSAGE_MAX),
            }

    @staticmethod
    @transaction.atomic
    def run_inference(
        conversation_id: int | None,
        prompt: str,
        user: User | None,
        options: dict = None,
    ) -> dict:
        """전체 파이프라인 실행"""
        if options is None:
            options = {}

        # 1. 대화 조회 or 생성
        if conversation_id:
            conversation = Conversation.objects.select_for_update().get(
                id=conversation_id
            )
            if user and conversation.owner and conversation.owner != user:
                raise PermissionDenied("이 대화에 접근할 권한이 없습니다.")
        else:
            conversation = Conversation.objects.create(
                owner=user if user and user.is_authenticated else None,
                title=_truncate(prompt, 200),
            )

        # 2. 검색 로그 기록
        SearchLog.objects.create(
            user=user if user and user.is_authenticated else None,
            query=prompt,
            normalized_query=prompt.lower(),
            result_count=0,
        )

        # 3. 사용자 메시지 저장
        Message.objects.create(conversation=conversation, role="user", content=prompt)

        # 4. Gemini API 호출
        gemini = InferenceService.call_gemini_api(prompt, options)

        ai_content = gemini.get("ai_content") or "API 응답을 받지 못했습니다."
        if isinstance(ai_content, dict):
            ai_content = json.dumps(ai_content, ensure_ascii=False)

        # 5. AI 메시지 저장
        ai_msg = Message.objects.create(
            conversation=conversation, role="assistant", content=ai_content
        )

        # 6. 실행 로그 저장 (추가 필드 포함)
        InferenceRun.objects.create(
            conversation=conversation,
            model=settings.GEMINI_MODEL_NAME,
            latency_ms=gemini.get("latency_ms") or 0,
            prompt_tokens=gemini.get("prompt_tokens") or 0,
            completion_tokens=gemini.get("completion_tokens") or 0,
            status=gemini.get("status"),
            error_code=_truncate(gemini.get("error_code"), ERROR_CODE_MAX),
            error_message=_truncate(gemini.get("error_message"), ERROR_MESSAGE_MAX),
            check_pass=gemini.get("check_pass"),
            retry_used=gemini.get("retry_used"),
            violations=gemini.get("violations"),
        )

        # 7. 최종 결과 반환
        return {
            "message_id": ai_msg.id,
            "role": ai_msg.role,
            "content": ai_msg.content,
            "usage": {
                "prompt_tokens": gemini.get("prompt_tokens") or 0,
                "completion_tokens": gemini.get("completion_tokens") or 0,
            },
            "status": gemini.get("status"),
            "error_code": gemini.get("error_code"),
            "error_message": gemini.get("error_message"),
        }
