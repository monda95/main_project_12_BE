"""공통 미들웨어 모음."""


class ForceHttpSchemeMiddleware:
    """모든 요청을 HTTP 스킴으로 강제한다.

    일부 프록시나 브라우저 캐시는 `X-Forwarded-Proto` 값을 HTTPS로 유지한 채
    전달해 Django가 `request.is_secure()`를 True로 판단하게 만든다. 이렇게 되면
    내부적으로 생성되는 절대 URL이나 리다이렉트가 HTTPS를 가리키며, 브라우저가
    다시 HTTPS로 접근하려 시도한다. 프로덕션 환경은 HTTP 전용이므로, 미들웨어에서
    관련 헤더와 WSGI 스킴을 확실히 HTTP로 고정한다.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # X-Forwarded-Proto 헤더는 완전히 제거해서 Django가 참고하지 않게 한다.
        request.META.pop("HTTP_X_FORWARDED_PROTO", None)
        # WSGI 스킴도 HTTP로 덮어써 절대경로 계산 시 HTTPS가 등장하지 않도록 한다.
        request.META["wsgi.url_scheme"] = "http"
        # 혹시 이전 미들웨어에서 override된 값이 남아 있다면 False로 재설정한다.
        setattr(request, "_is_secure_override", False)

        return self.get_response(request)


class DisableHSTSMiddleware:
    """브라우저에 저장된 HSTS 캐시를 즉시 비활성화한다.

    과거 HTTPS 환경에서 `Strict-Transport-Security` 헤더가 발급된 경우,
    브라우저는 일정 기간 동안 자동으로 HTTPS로 업그레이드한다. 현재 서비스는
    HTTP 전용으로 동작하므로 모든 응답에 `max-age=0; includeSubDomains`를
    명시적으로 내려 기존 캐시를 제거해 준다.
    """

    header_name = "Strict-Transport-Security"
    header_value = "max-age=0; includeSubDomains"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response[self.header_name] = self.header_value
        return response
