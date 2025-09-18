# 📘 API 명세서 (Django + DRF)

## 공통
- **인증**: `Authorization: Bearer <access_token>` (SimpleJWT - Refresh Token Rotation 및 Blacklist 활성화)
- **응답 형식**: 순수 JSON(래핑 없음) — `{"data": ...}` 형태가 아닌, 리소스/컬렉션 자체를 그대로 반환.
- **API 문서**:
  - `GET /api/schema/` (OpenAPI 스키마)
  - `GET /api/swagger/` (Swagger UI)

---

## 1. 인증/권한

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/api/v1/auth/signup` | `POST` | 회원가입 | 누구나 |
| `/api/v1/auth/login` | `POST` | 로그인 (토큰 발급) | 누구나 |
| `/api/v1/auth/refresh` | `POST` | Access 토큰 재발급 | 누구나 |
| `/api/v1/auth/logout` | `POST` | 로그아웃 (Refresh 토큰 블랙리스트) | 인증된 사용자 |

### 1.1 회원가입 — `POST /api/v1/auth/signup`
```json
{ 
  "email": "user@example.com",
  "password": "Str0ngPass!",
  "username": "홍길동",
  "nickname": "kildong"
}
```
**Response (201 Created)**
```json
{ 
  "id": 1, 
  "email": "user@example.com",
  "username": "홍길동",
  "nickname": "kildong",
  "image_url": null,
  "phone_number": null
}
```

### 1.2 로그인 — `POST /api/v1/auth/login`
```json
{ "email": "user@example.com", "password": "Str0ngPass!" }
```
**Response (200 OK)**
```json
{ "access": "jwt-access-token", "refresh": "jwt-refresh-token" }
```

### 1.3 토큰 재발급 — `POST /api/v1/auth/refresh`
```json
{ "refresh": "jwt-refresh-token" }
```
**Response (200 OK)**
```json
{ "access": "new-access-token" }
```

### 1.4 로그아웃 — `POST /api/v1/auth/logout`
```json
{ "refresh": "jwt-refresh-token" }
```
**Response (204 No Content)**

---

---

## 1.5 부가 인증 기능

### 이메일 인증 시스템
**운영 정책**
- `AUTH_EMAIL_VERIFICATION_REQUIRED=True` 설정 시 미인증 사용자 로그인 차단
- 에러 응답: `400 Bad Request` — `{"detail": "이메일 인증이 필요합니다."}`
- 이메일 주소는 서버에서 자동으로 소문자 정규화 처리

**이메일 인증 링크**
```
GET /api/v1/auth/verify/{uidb64}/{token}/
```
- 회원가입 시 발송된 인증 이메일의 링크 처리
- 성공: `200 OK` — "이메일 인증이 완료되었습니다."
- 실패: `400 Bad Request` — "잘못된 인증 링크입니다."

> **참고**: 브라우저 전용 콜백 URL로 OpenAPI 스키마에서 제외됩니다.

### OAuth2 소셜 로그인

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/api/v1/oauth2/exchange` | `POST` | 인가 코드 → JWT 토큰 교환 | 누구나 |
| `/api/v1/oauth2/link` | `POST` | 소셜 계정 연결 | 인증된 사용자 |
| `/api/v1/oauth2/link/{provider}` | `DELETE` | 소셜 계정 연결 해제 | 인증된 사용자 |

**권장 플로우**: Authorization Code + PKCE

#### 1.5.1 인가 코드 교환 — `POST /api/v1/oauth2/exchange`
```json
{
  "provider": "google",
  "code": "<authorization_code>",
  "code_verifier": "<pkce_verifier>",
  "redirect_uri": "https://app.example.com/oauth/callback"
}
```
**Response (200 OK)**
```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "is_new": false,
  "user": { "id": 1, "email": "user@example.com" }
}
```

#### 1.5.2 소셜 계정 연결 — `POST /api/v1/oauth2/link`
로그인된 사용자가 추가 소셜 계정을 연결할 때 사용
```json
{
  "provider": "google",
  "code": "<authorization_code>",
  "code_verifier": "<pkce_verifier>",
  "redirect_uri": "https://app.example.com/oauth/callback"
}
```
**Response (204 No Content)**

#### 1.5.3 소셜 계정 해제 — `DELETE /api/v1/oauth2/link/{provider}`
**Response (204 No Content)**
> **주의**: 마지막 로그인 수단인 경우 해제를 제한하는 것이 권장됩니다.

**OAuth2 콜백 URL (브라우저 전용)**
```
GET /api/v1/auth/oauth2/{provider}/callback
```
- 소셜 로그인 공급자의 리다이렉트를 받는 엔드포인트
- 받은 인가 코드를 클라이언트에서 `/api/v1/oauth2/exchange`로 전달
- OpenAPI 스키마에서 제외되는 브라우저 전용 콜백

---

## 2. 사용자

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/api/v1/users/me` | `GET` | 내 정보 조회 | 인증된 사용자 |
| `/api/v1/users/me` | `PATCH` | 내 정보 수정 (닉네임, 프로필 이미지) | 인증된 사용자 |
| `/api/v1/users/me` | `DELETE` | 회원 탈퇴 | 인증된 사용자 |
| `/api/v1/users/me/password` | `PUT` | 비밀번호 변경 | 인증된 사용자 |

### 2.1 내 정보 조회
**Response (200 OK)**
```json
{ 
  "id": 1, 
  "email": "user@example.com",
  "username": "홍길동",
  "nickname": "kildong",
  "image_url": null,
  "phone_number": null,
  "created_at": "...",
  "updated_at": "..."
}
```

### 2.2 내 정보 수정
```json
{ "nickname": "새로운 닉네임", "image_url": "https://example.com/avatar.png" }
```
**Response (200 OK)**: 수정된 전체 사용자 정보

### 2.3 비밀번호 변경
```json
{ "current_password": "Str0ngPass!", "new_password": "EvenStronger#1" }
```
**Response (204 No Content)**

### 2.4 회원 탈퇴
**Response (204 No Content)**

---

# 3. 대화/메시지 API 명세서

## 3.1 대화 목록 조회
**Response (200 OK)**
```json
[
  { "id": 10, "title": "주간 회의록", "owner": "user@example.com", "created_at": "..." },
  { "id": 11, "title": "새로운 아이디어", "owner": "user@example.com", "created_at": "..." }
]
```

**Errors**
- 401 Unauthorized: 인증 실패 시
---

## 3.2 대화 생성
**Request**
```json
{ "title": "새로운 대화" }
```
**Response (201 Created)**
```json
{ "id": 12, "title": "새로운 대화", "owner": "user@example.com", "created_at": "..." }
```

**Errors**
- 400 Bad Request: 잘못된 입력 데이터
- 401 Unauthorized: 인증 실패 시
---

## 3.3 대화 삭제
**Response (204 No Content)**

**Errors**
- 401 Unauthorized: 인증 실패 시
- 403 Forbidden: 소유자가 아님
- 404 Not Found: 존재하지 않는 대화
---

## 3.4 메시지 목록 조회
**Response (200 OK)**
```json
{
  "count": 120,
  "next": "/api/v1/conversations/10/messages?page=2",
  "previous": null,
  "results": [
    { "id": 100, "role": "user", "content": "오늘 날씨 알려줘", "created_at": "..." },
    { "id": 101, "role": "assistant", "content": "오늘 서울의 날씨는...", "created_at": "..." }
  ]
}
```

**Errors**
- 401 Unauthorized: 인증 실패 시
- 403 Forbidden: 소유자가 아님
- 404 Not Found: 존재하지 않는 대화
---

## 3.5 메시지 추가
**Request**
```json
{ "role": "user", "content": "내일 날씨는?" }
```
**Response (201 Created)**
```json
{ "id": 102, "conversation": 10, "role": "user", "content": "내일 날씨는?", "created_at": "..." }
```

**Errors**
- 400 Bad Request: 잘못된 입력 데이터
- 401 Unauthorized: 인증 실패 시
- 403 Forbidden: 소유자가 아님
- 404 Not Found: 존재하지 않는 대화

---

## 4. AI 추론

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/api/v1/inference` | `POST` | Gemini 호출 및 응답 생성 | 인증된 사용자 |

### 4.1 Gemini 호출
```json
{
  "conversation_id": 10,
  "prompt": "회의록 요약해줘",
  "options": { "temperature": 0.3, "max_output_tokens": 1024 }
}
```
**Response (200 OK)**
```json
{
  "message_id": 101,
  "role": "assistant",
  "content": "회의록 주요 내용은...",
  "usage": { "prompt_tokens": 123, "completion_tokens": 456 }
}
```

---

## 5. 데이터 전처리 (관리자 기능)

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/api/v1/datasets` | `GET`, `POST` | 데이터셋 목록/생성 | 관리자 |
| `/api/v1/datasets/{id}` | `GET`, `PATCH`, `DELETE` | 특정 데이터셋 조회/수정/삭제 | 관리자 |
| `/api/v1/datasets/{id}/preprocess` | `POST` | 데이터셋 전처리 작업 생성 | 관리자 |
| `/api/v1/preprocessing-jobs` | `GET` | 모든 전처리 작업 목록 조회 | 관리자 |
| `/api/v1/preprocessing-jobs/{job_id}` | `GET` | 특정 전처리 작업 조회 | 관리자 |

### 5.1 데이터셋 등록
```json
{ "name": "news_corpus_v1", "source": "file", "uri": "s3://bucket/raw/news_v1.csv" }
```
**Response (201 Created)**
```json
{ "id": 1, "name": "news_corpus_v1", "source": "file", "uri": "s3://bucket/raw/news_v1.csv", "created_at": "2025-09-09T12:00:00Z" }
```

### 5.2 전처리 작업 생성
```json
{
  "steps": [{"op":"normalize"},{"op":"dedupe"},{"op":"fillna"},{"op":"tokenize"}],
  "client_job_id": "optional-unique-key-per-dataset"
}
```
**Response (202 Accepted)**
```json
{ "job_id": 101, "status": "queued", "idempotent": true }
```

### 5.3 전처리 작업 조회
```json
{ "id": 101, "dataset_id": 1, "status": "running", "started_at": "2025-09-09T12:01:00Z", "finished_at": null }
```

### 5.4 전처리 작업 목록
```json
[
  {
    "id": 101,
    "dataset_id": 1,
    "status": "running",
    "started_at": "2025-09-09T12:01:00Z",
    "finished_at": null
  }
]
```

---
## 6. 추론 모니터링 (관리자 기능)

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/api/v1/inference-runs` | `GET` | 모든 추론 기록 조회 | 관리자 |
| `/api/v1/inference-runs/{id}` | `GET` | 특정 추론 기록 조회 | 관리자 |

### 6.1 추론 기록 목록 조회 (예시)
```json
[
  {
    "id": 1,
    "conversation": "주간 회의록", 
    "message": "요약: ...",
    "model": "gemini-flash",
    "latency_ms": 420,
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "status": "success",
    "error_code": null,
    "error_message": null,
    "created_at": "2025-09-18T05:00:00Z"
  }
]
```

### 6.2 추론 기록 상세 (예시)
```json
{
  "id": 1,
  "conversation": "주간 회의록", 
  "message": "요약: ...",
  "model": "gemini-flash",
  "latency_ms": 420,
  "prompt_tokens": 123,
  "completion_tokens": 456,
  "status": "error",
  "error_code": "HTTP_503",
  "error_message": "upstream timeout ...",
  "created_at": "2025-09-18T05:00:00Z"
}
```

---

## 7. 유틸

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/healthz` | `GET` | 앱 가동 확인 | 누구나 |
| `/readiness` | `GET` | 의존성(DB 등) 점검 | 누구나 |

### 7.1 Health Check
```
OK
```

### 7.2 Readiness Check
**Response (200 OK)**
```
OK
```
**Response (503 Service Unavailable)**
```
Service Unavailable
```

---

### 메서드 정책 업데이트 (2025-09-18)
- 전역적으로 **PUT 미지원**(전체 업데이트로 인한 데이터유실 원천차단), **부분 수정은 `PATCH`만 허용**
- **비밀번호 변경**(`/api/v1/users/me/password`)은 **`PUT`** 사용이 필수적이라 유지
