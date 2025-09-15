import time

import requests
from django.conf import settings


def call_gemini_api(prompt_content: str, options: dict = None) -> dict:
    """
    Google Gemini API를 호출하고 응답을 처리합니다.
    """
    if options is None:
        options = {}

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

    # Gemini API 엔드포인트
    # 실제 Gemini API URL은 공식 문서를 참조하여 정확히 입력해야 합니다.
    # 예시용 더미 URL은 아래값처럼
    # 예: https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY
    gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash:generateContent?key={api_key}"  # 실제 URL로 변경완료

    headers = {
        "Content-Type": "application/json",
    }

    # Gemini API 요청 본문 구성 (예시)
    # 실제 요청 본문은 Gemini API 문서에 따라 달라집니다.
    payload = {
        "contents": [{"parts": [{"text": prompt_content}]}],
        "generationConfig": options,
    }

    start_time = time.time()
    try:
        response = requests.post(
            gemini_api_url, headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        response_data = response.json()

        # 실제 Gemini 응답 구조에 따라 파싱 필요
        # 여기서는 예시를 위해 더미 데이터 사용
        ai_content = (
            response_data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        # 토큰 사용량은 실제 API 응답에서 파싱해야 합니다.
        # 여기서는 임시로 계산
        prompt_tokens = len(prompt_content.split())  # 임시
        completion_tokens = len(ai_content.split())  # 임시

        return {
            "ai_content": ai_content if ai_content else "API 응답을 받지 못했습니다.",
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "status": "success",
            "error_code": None,
        }
    except requests.exceptions.RequestException as e:
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)
        return {
            "ai_content": "API 호출 중 오류 발생",
            "latency_ms": latency_ms,
            "prompt_tokens": len(prompt_content.split()),
            "completion_tokens": 0,
            "status": "error",
            "error_code": str(e),
        }
    except ValueError as e:
        return {
            "ai_content": "설정 오류",
            "latency_ms": 0,
            "prompt_tokens": len(prompt_content.split()),
            "completion_tokens": 0,
            "status": "error",
            "error_code": str(e),
        }
