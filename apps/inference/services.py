import time
import requests
from django.conf import settings


def call_gemini_api(prompt_content: str, options: dict = None) -> dict:
    """
    Google Gemini API를 호출하고 응답을 처리합니다.
    - prompt_content: 사용자 입력 텍스트
    - options: 생성 옵션 (응답의 창의성, 최대 토큰 등)
    """
    if options is None:
        options = {}

    # 1. GEMINI_API_KEY 확인
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

    # 2. Gemini API URL
    gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json",
    }

    # 3. 요청 본문 구성 (payload)
    payload = {
        "contents": [{"parts": [{"text": prompt_content}]}],
        "generationConfig": options,
    }

    start_time = time.time()
    try:
        # 4. API 요청
        response = requests.post(
            gemini_api_url, headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # 5. 응답 파싱
        response_data = response.json()

        ai_content = (
            response_data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        # 6. 토큰 사용량 파싱
        usage_metadata = response_data.get("usageMetadata", {})
        prompt_tokens = usage_metadata.get("prompt_token_count")
        completion_tokens = usage_metadata.get(
            "candidates_token_count"
        )  # candidates_token_count를 completion_tokens로 사용

        return {
            "ai_content": ai_content if ai_content else "API 응답을 받지 못했습니다.",
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "status": "success",
            "error_code": None,
        }

    except requests.exceptions.RequestException as e:
        # 요청 실패 시 응답 반환
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)
        return {
            "ai_content": "API 호출 중 오류 발생",
            "latency_ms": latency_ms,
            "prompt_tokens": None,  # API 호출 실패 시 토큰 정보는 알 수 없음
            "completion_tokens": None,  # API 호출 실패 시 토큰 정보는 알 수 없음
            "status": "error",
            "error_code": str(e),
        }

    except ValueError as e:
        # 설정 오류 시 응답 반환
        return {
            "ai_content": "설정 오류",
            "latency_ms": 0,
            "prompt_tokens": None,  # 설정 오류 시 토큰 정보는 알 수 없음
            "completion_tokens": None,  # 설정 오류 시 토큰 정보는 알 수 없음
            "status": "error",
            "error_code": str(e),
        }
