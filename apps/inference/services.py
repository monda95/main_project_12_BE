import time
import requests
import logging
import json
import re

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

    # Nutrient helper
    @staticmethod
    def _parse_nutrient(value) -> float | None:
        "'10g', '120 kcal' 같은 문자열에서 숫자만 파싱합니다."
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            match = re.search(r"[\d.]+", value)
            if match:
                try:
                    return float(match.group())
                except (ValueError, TypeError):
                    return None
        return None

    # Self-check logic
    @staticmethod
    def _self_check(ai_content: str) -> dict:
        """
        LLM 1차 응답을 검사하는 Self-Check 로직입니다.
        - 형식: JSON 파싱, 5대 섹션(영양/알레르기/보관/가공법/출처) 존재 여부
        - 내용: 칼로리 상충, 출처 내용 누락 등
        """
        violations = []
        required_sections = ["nutrition", "allergy", "storage", "processing", "source"]

        try:
            data = json.loads(ai_content)
            if not isinstance(data, dict):
                raise TypeError("응답이 JSON 객체 형식이 아닙니다.")

            # 필수 섹션 검사
            for section in required_sections:
                if section not in data:
                    violations.append(
                        {
                            "code": "MISSING_SECTION",
                            "detail": f"'{section}' 섹션이 누락되었습니다.",
                        }
                    )

            # 출처 검사
            if not data.get("source") or not str(data["source"]).strip():
                violations.append(
                    {
                        "code": "MISSING_SOURCE",
                        "detail": "'source' 섹션의 내용이 비어있습니다.",
                    }
                )

            # 칼로리 계산 검증
            nutrition = data.get("nutrition")
            if isinstance(nutrition, dict):
                calories = InferenceService._parse_nutrient(nutrition.get("calories"))
                carbs = InferenceService._parse_nutrient(nutrition.get("carbohydrates"))
                protein = InferenceService._parse_nutrient(nutrition.get("protein"))
                fat = InferenceService._parse_nutrient(nutrition.get("fat"))

                if all(v is not None for v in [calories, carbs, protein, fat]):
                    calculated_calories = (carbs * 4) + (protein * 4) + (fat * 9)
                    if abs(calories - calculated_calories) > (calories * 0.15):
                        violations.append(
                            {
                                "code": "CALORIE_CONFLICT",
                                "detail": f"명시된 칼로리({calories}kcal)와 계산된 칼로리({calculated_calories:.1f}kcal)가 15% 이상 차이납니다.",
                            }
                        )

        except (json.JSONDecodeError, TypeError) as e:
            violations.append(
                {
                    "code": "INVALID_FORMAT",
                    "detail": f"응답이 유효한 JSON이 아닙니다. {e}",
                }
            )

        # Self-check 결과 로그 남김
        if violations:
            logger.warning(f"Self-check violations: {violations}")

        return {"check_pass": not violations, "violations": violations}

    # Gemini API Call
    @staticmethod
    def call_gemini_api(prompt_content: str, options: dict = None) -> dict:
        if options is None:
            options = {}

        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.error("GEMINI_API_KEY is not set in the environment.")
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
            f"https://generativelanguage.googleapis.com/v1/models/"
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
                "prompt_tokens": usage.get(
                    "prompt_token_count"
                ),  # ✅ 일관된 snake_case
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

            logger.error(f"Gemini API HTTPError: {status_code} - {body_text}")
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
            logger.error(f"Gemini API RequestException: {e}")
            return {
                "ai_content": "API 호출 중 오류 발생",
                "latency_ms": int((time.time() - start_time) * 1000),
                "prompt_tokens": None,
                "completion_tokens": None,
                "status": "error",
                "error_code": _truncate(e.__class__.__name__, ERROR_CODE_MAX),
                "error_message": _truncate(str(e), ERROR_MESSAGE_MAX),
            }

    # Full pipeline
    @staticmethod
    @transaction.atomic
    def run_inference(
        conversation_id: int | None,
        prompt: str,
        user: User | None,
        options: dict = None,
    ) -> dict:
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
        gemini_result = InferenceService.call_gemini_api(prompt, options)

        # 5. Self-check + 필요시 재시도
        retry_used = False
        if gemini_result["status"] == "success":
            check_result = InferenceService._self_check(gemini_result["ai_content"])
            if not check_result["check_pass"]:
                retry_used = True
                correction_prompt = (
                    f"Previous Answer (failed validation):\n{gemini_result['ai_content']}\n\n"
                    f"Validation Errors: {json.dumps(check_result['violations'], ensure_ascii=False)}\n\n"
                    f"Original_Prompt: {prompt}\n\n"
                    f"Instructions: Please regenerate the answer. "
                    f"It MUST be a valid JSON object containing all required sections: "
                    f"'nutrition', 'allergy', 'storage', 'processing', and 'source'. "
                    f"The 'source' must not be empty."
                )
                gemini_result = InferenceService.call_gemini_api(
                    correction_prompt, options
                )
                if gemini_result["status"] == "success":
                    check_result = InferenceService._self_check(
                        gemini_result["ai_content"]
                    )
        else:
            check_result = {
                "check_pass": False,
                "violations": [
                    {
                        "code": "API_CALL_FAILED",
                        "detail": gemini_result.get("error_message"),
                    }
                ],
            }

        # 6. AI 메시지 저장
        ai_content = gemini_result.get("ai_content") or "API 응답을 받지 못했습니다."
        ai_msg = Message.objects.create(
            conversation=conversation, role="assistant", content=ai_content
        )

        # 7. 실행 로그 저장
        InferenceRun.objects.create(
            conversation=conversation,
            model=settings.GEMINI_MODEL_NAME,
            latency_ms=gemini_result.get("latency_ms") or 0,
            prompt_tokens=gemini_result.get("prompt_tokens") or 0,
            completion_tokens=gemini_result.get("completion_tokens") or 0,
            status=gemini_result.get("status"),
            error_code=_truncate(gemini_result.get("error_code"), ERROR_CODE_MAX),
            error_message=_truncate(
                gemini_result.get("error_message"), ERROR_MESSAGE_MAX
            ),
            check_pass=check_result.get("check_pass"),
            retry_used=retry_used,
            violations=check_result.get("violations"),
        )

        # 8. 최종 결과 반환
        return {
            "message_id": ai_msg.id,
            "role": ai_msg.role,
            "content": ai_msg.content,
            "usage": {
                "prompt_tokens": gemini_result.get("prompt_tokens") or 0,
                "completion_tokens": gemini_result.get("completion_tokens") or 0,
            },
            "status": gemini_result.get("status"),
            "error_code": gemini_result.get("error_code"),
            "error_message": gemini_result.get("error_message"),
            "self_check": {
                "check_pass": check_result.get("check_pass"),
                "retry_used": retry_used,
                "violations": check_result.get("violations"),
            },
        }
