"""공통 미들웨어 모음."""


class DisableHSTSMiddleware:
    """브라우저에 저장된 HSTS 캐시를 즉시 비활성화한다.

    과거 HTTPS 환경에서 `Strict-Transport-Security` 헤더가 발급된 경우,
    브라우저는 일정 기간 동안 자동으로 HTTPS로 업그레이드한다. 현재 서비스는
    HTTP 전용으로 동작하므로 모든 응답에 `max-age=0`을 명시적으로 내려 기존
    캐시를 제거해 준다.
    """

    header_name = "Strict-Transport-Security"
    header_value = "max-age=0"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers[self.header_name] = self.header_value
        return response
