import re


def normalize_phone(raw: str | None) -> str | None:
    """
    입력 예:
      "+82 010-1234-5678" -> "01012345678"
      "0082-10-1234-5678" -> "01012345678"
      "010-1234-5678"     -> "01012345678"
    규칙:
      - 숫자만 남긴다.
      - 국제표기(+82 / 0082)는 제거하고 국내형 선두 '0'이 없으면 붙인다.
      - 그 외에는 사용자가 준 국번의 '0'은 제거하지 않는다.
    """
    if not raw:
        return raw
    raw_stripped = raw.strip()
    digits = re.sub(r"\D", "", raw_stripped)

    # 국제 접두 처리
    if raw_stripped.startswith("+82") or raw_stripped.startswith("0082"):
        # "+82" 또는 "0082" 제거
        digits = re.sub(r"^(?:82|0082)", "", digits)
        if not digits.startswith("0"):
            digits = "0" + digits

    # 숫자 검증 (3~25 자리)
    if not (3 <= len(digits) <= 25):
        raise ValueError("전화번호 길이가 올바르지 않습니다.")
    return digits
