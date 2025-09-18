# apps/inference/services.py
import time
import requests
from django.conf import settings

# DB 제약과 일치시키기: error_code ≤ 128, error_message는 TextField지만 운영 안전을 위해 상한 유지
ERROR_CODE_MAX = 128
ERROR_MESSAGE_MAX = 8192  # 필요 시 조정


def _truncate(s: str | None, limit: int) -> str | None:
    if s is None:
        return None
    return s if len(s) <= limit else (s[: limit - 3] + "...")


def call_gemini_api(prompt_content: str, options: dict = None) -> dict:
    """
    Google Gemini API를 호출하고 응답을 처리합니다.
    - prompt_content: 사용자 입력 텍스트
    - options: 생성 옵션 (응답의 창의성, 최대 토큰 등)
    - 성공: status=success, error_code=None, error_message=None
    - 실패: status=error, error_code=짧은코드, error_message=상세원문(절단)
    """
    if options is None:
        options = {}

    # 1. GEMINI_API_KEY 확인
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        # 설정 오류는 코드와 메시지 분리
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

    # 2. Gemini API URL
    gemini_api_url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-flash:generateContent?key={api_key}"
    )
    headers = {"Content-Type": "application/json"}

    # 3. 요청 본문 구성 (payload)
    payload = {
        "contents": [{"parts": [{"text": prompt_content}]}],
        "generationConfig": options,
    }

    start_time = time.time()
    try:
        response = requests.post(
            gemini_api_url, headers=headers, json=payload, timeout=30
        )
        # 4. API 요청, HTTP 에러를 명시적으로 구분
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            status_code = response.status_code
            # 짧은 코드 / 긴 메시지
            error_code = f"HTTP_{status_code}"
            # 응답 본문 원문을 최대한 살리되 상한 적용
            body_text = None
            try:
                j = response.json()
                # 구글 계열 에러는 보통 { "error": { "code": ..., "message": "...", ... } }
                body_text = j.get("error", {}).get("message") or str(j)
            except Exception:
                body_text = response.text or str(e)
            return {
                "ai_content": "API 호출 중 오류 발생",
                "latency_ms": latency_ms,
                "prompt_tokens": None,
                "completion_tokens": None,
                "status": "error",
                "error_code": _truncate(error_code, ERROR_CODE_MAX),
                "error_message": _truncate(body_text, ERROR_MESSAGE_MAX),
            }

        # 성공 경로
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # 5. 응답 파싱
        data = response.json()

        ai_content = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        ) or "API 응답을 받지 못했습니다."

        # 6. 토큰 사용량 파싱
        usage = data.get("usageMetadata", {}) or {}
        prompt_tokens = usage.get("prompt_token_count")
        completion_tokens = usage.get("candidates_token_count")

        return {
            "ai_content": ai_content,
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "status": "success",
            "error_code": None,
            "error_message": None,
        }

    except requests.exceptions.RequestException as e:
        # 네트워크/타임아웃 등
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)
        error_code = e.__class__.__name__  # 예: ConnectTimeout, ConnectionError
        return {
            "ai_content": "API 호출 중 오류 발생",
            "latency_ms": latency_ms,
            "prompt_tokens": None,  # API 호출 실패 시 토큰 정보는 알 수 없음
            "completion_tokens": None,  # API 호출 실패 시 토큰 정보는 알 수 없음
            "status": "error",
            "error_code": _truncate(error_code, ERROR_CODE_MAX),
            "error_message": _truncate(str(e), ERROR_MESSAGE_MAX),
        }
