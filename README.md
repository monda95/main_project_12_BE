# 📘 디지털 휴먼 AI 가상비서 (Fluent AI Assistant) 

> 본 문서는 **배포 가능한 최소기능(MVP)**을 우선으로 하되, 
추후 확장을 고려해서 **표준/일관성**을 확보하기위한 설계를 정리한 문서입니다.  

## 🏗️ 기술 스택
- **백엔드**: Django + Django REST Framework
- **패키지 관리**: uv
- **IDE**: PyCharm
- **컨테이너**: Docker Compose
- **데이터베이스**: **PostgreSQL (AWS RDS)**
- **배포**: AWS EC2
- **AI**: **Google Gemini API**

## 📑 사용자 요구설명서 (개인 프로젝트)

## 1. 개요
- 서비스: 인터랙티브 **디지털 휴먼 AI 가상비서(Fluent AI Assistant)**를 위한 **AI 모델 배포용 API 서버**.
- 대상 환경: **Windows + PyCharm**, **uv** 패키지, **Docker Compose**, **PostgreSQL(AWS RDS 가능)**, **Django + DRF**, **AWS EC2** 배포, **Google Gemini API** 연동.

## 2. 요구사항 목록

| 요구사항 ID | 요구사항 명 | 구분 | 설명 | 중요도 | 비고 |
|---|---|---|---|---|---|
| DH_RF01001 | 회원가입(자체) | 기능 | 이메일·아이디 중복 검사, 비밀번호 유효성 검사 | 상 | 운영에선 이메일 인증 필수 | - SimpleJWT (Refresh 회전 + 블랙리스트)
| DH_RF01002 | 로그인/토큰 발급 | 기능 | SimpleJWT (Refresh 회전 + 블랙리스트)), 재발급 지원 | 상 | SimpleSimpleJWT (Refresh 회전 + 블랙리스트)
| DH_RF01003 | 로그아웃 | 기능 | 클라이언트 토큰 삭제, (선택) 서버 Refresh 블랙리스트 | 상 | 블랙리스트 앱 사용 가능 |
| DH_RF01004 | 마이페이지 조회/수정 | 기능 | 닉네임·이미지·이메일 등 수정 | 중 | 개인정보 보호 고려 |
| DH_RF01005 | 비밀번호 변경 | 기능 | 기존 비밀번호 검증 후 변경 | 상 | OWASP 권고 준수 |
| DH_RF02001 | 대화 관리 | 기능 | 대화 생성/조회/수정/삭제 | 상 | 사용자 소유권 유지 |
| DH_RF02002 | 메시지 관리 | 기능 | 대화 내 메시지 작성/조회(페이징) | 상 | |
| DH_RF02003 | 태그 관리 | 기능 | 태그 CRUD, 대화↔태그 연결/해제 | 중 | M:N(ConversationTag) |
| DH_RF03001 | AI 추론(Gemini) | 기능 | 프롬프트 전달·응답 저장/반환 | 상 | 옵션(temperature,max_tokens) |
| DH_RF03002 | **모델 성능 모니터링 데이터 저장** | 기능 | 추론별 latency/status/tokens 저장 | 중 | `inference_runs` |
| DH_RF02004 | **데이터 전처리 파이프라인** | 기능 | Dataset 등록·전처리 Job 생성/조회 | 중 | `datasets`, `preprocessing_jobs` |
| DH_RQ04001 | 보안성 | 비기능 | 모든 API는 HTTPS, SimpleJWT (Refresh 회전 + 블랙리스트)
| DH_RQ04002 | 성능 | 비기능 | **평균 응답 ≤ 2초, 동시 30**(t2.micro 기준) | 중 | |
| DH_RQ04003 | 개발/배포 | 비기능 | Git 관리, Dev/Prod 차이 최소화 | 중 | |
| DH_RQ04IDEMP | 멱등성(전처리 한정) | 비기능 | 전처리 생성에 `client_job_id` 지원 | 중 | UNIQUE(dataset_id, client_job_id) |

## 3. 제약 및 참고
- 인증: **SimpleSimpleJWT (Refresh 회전 + 블랙리스트)).
- 문서화: **drf-spectacular** + Swagger UI(`/api/docs/`).
- DB: **PostgreSQL**(문서의 모든 타입/제약은 Postgres 기준).
- 배포: **Docker Compose → EC2**, Readiness/Health 엔드포인트 제공.


---

# 📊 ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    User {
        bigint id PK
        string username UK
        string email UK
        string (Django Auth에서 관리)
        string nickname
        string image_url
        timestamptz created_at
        timestamptz updated_at
    }

    Conversation {
        bigint id PK
        bigint owner_id FK
        string title
        timestamptz created_at
        timestamptz updated_at
    }

    Message {
        bigint id PK
        bigint conversation_id FK
        string role  "user/assistant/system"
        text content
        timestamptz created_at
    }

    Tag {
        bigint id PK
        string name UK
        timestamptz created_at
    }

    ConversationTag {
        bigint id PK
        bigint conversation_id FK
        bigint tag_id FK
        timestamptz created_at
    }

    Dataset {
        bigint id PK
        bigint owner_id FK
        string name
        string source   "file/crawl/api 등"
        string uri      "S3 키 등"
        timestamptz created_at
    }

    PreprocessingJob {
        bigint id PK
        bigint dataset_id FK
        string status   "queued/running/succeeded/failed"
        jsonb steps     "전처리 단계 정의"
        string client_job_id  "멱등키"
        timestamptz created_at
        timestamptz started_at
        timestamptz finished_at
    }

    InferenceRun {
        bigint id PK
        bigint conversation_id FK
        bigint message_id FK
        string model
        integer latency_ms
        integer prompt_tokens
        integer completion_tokens
        string status    "success/error"
        string error_code
        timestamptz created_at
    }

    %% 관계
    User ||--o{ Conversation : "1:N"
    Conversation ||--o{ Message : "1:N"
    Conversation }o--o{ Tag : "M:N"
    Conversation ||--o{ InferenceRun : "1:N"
    Message ||--o{ InferenceRun : "1:N"

    User ||--o{ Dataset : "1:N"
    Dataset ||--o{ PreprocessingJob : "1:N"
```


---

# 🗄️ 테이블 명세서 (PostgreSQL)

## 1. users
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 사용자 | - |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 로그인 아이디 | - |
| email | VARCHAR(100) | UNIQUE, NOT NULL | 이메일 | - |
| (Django Auth에서 관리) | VARCHAR(255) | NOT NULL | 해시된 비밀번호 | - |
| nickname | VARCHAR(100) | NULL | 닉네임 | NULL |
| image_url | VARCHAR(500) | NULL | 프로필 이미지 URL | NULL |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 | now() |
| updated_at | TIMESTAMPTZ | NOT NULL | 수정 | now() |

**인덱스**
- idx_users_username(username), idx_users_email(email)

---

## 2. conversations
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 대화 | - |
| owner_id | BIGINT | NOT NULL, FK→users(id) ON DELETE CASCADE | 소유자 | - |
| title | VARCHAR(200) | NOT NULL | 대화 제목 | - |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 | now() |
| updated_at | TIMESTAMPTZ | NOT NULL | 수정 | now() |

**인덱스**
- idx_conversations_owner(owner_id), idx_conversations_created(created_at)

---

## 3. messages
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 메시지 | - |
| conversation_id | BIGINT | NOT NULL, FK→conversations(id) ON DELETE CASCADE | 소속 대화 | - |
| role | VARCHAR(10) | NOT NULL, CHECK IN('user','assistant','system') | 역할 | - |
| content | TEXT | NOT NULL | 내용 | - |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 | now() |

**인덱스**
- idx_messages_conv(conversation_id), idx_messages_created(created_at), idx_messages_conv_created(conversation_id, created_at)

---

## 4. tags
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 태그 | - |
| name | VARCHAR(50) | UNIQUE, NOT NULL | 태그명 | - |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 | now() |

**인덱스**
- idx_tags_name(name)

---

## 5. conversation_tags
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 연결 | - |
| conversation_id | BIGINT | NOT NULL, FK→conversations(id) ON DELETE CASCADE | 대화 | - |
| tag_id | BIGINT | NOT NULL, FK→tags(id) ON DELETE CASCADE | 태그 | - |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 | now() |

**인덱스 / 제약**
- idx_ct_conv(conversation_id), idx_ct_tag(tag_id)
- UNIQUE(conversation_id, tag_id)

---

## 6. datasets
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 데이터셋 | - |
| owner_id | BIGINT | NOT NULL, FK→users(id) ON DELETE CASCADE | 소유자 | - |
| name | VARCHAR(100) | NOT NULL | 데이터셋명 | - |
| source | VARCHAR(100) | NULL | 원천(file/crawl/api 등) | NULL |
| uri | VARCHAR(500) | NULL | 원본 위치(S3 키 등) | NULL |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 | now() |

**인덱스**
- idx_datasets_owner(owner_id), idx_datasets_name(name), idx_datasets_created(created_at)

---

## 7. preprocessing_jobs
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 전처리 작업 | - |
| dataset_id | BIGINT | NOT NULL, FK→datasets(id) ON DELETE CASCADE | 대상 데이터셋 | - |
| client_job_id | VARCHAR(64) | NULL | **멱등키(데이터셋별 유일)** | NULL |
| status | VARCHAR(20) | NOT NULL, CHECK IN('queued','running','succeeded','failed') | 상태 | 'queued' |
| steps | JSONB | NULL | 단계 정의 | NULL |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 | now() |
| started_at | TIMESTAMPTZ | NULL | 시작 | NULL |
| finished_at | TIMESTAMPTZ | NULL | 종료 | NULL |

**인덱스 / 제약**
- fk_prejobs_dataset(dataset_id)
- **UNIQUE(dataset_id, client_job_id)**
- idx_prejobs_status_created(status, created_at)

---

## 8. inference_runs
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 추론 실행 | - |
| conversation_id | BIGINT | NOT NULL, FK→conversations(id) ON DELETE CASCADE | 대화 | - |
| message_id | BIGINT | NULL, FK→messages(id) ON DELETE SET NULL | 관련 메시지 | NULL |
| model | VARCHAR(50) | NOT NULL | 모델명 | - |
| latency_ms | INTEGER | NOT NULL | 지연(ms) | - |
| prompt_tokens | INTEGER | NULL | 프롬프트 토큰 | NULL |
| completion_tokens | INTEGER | NULL | 응답 토큰 | NULL |
| status | VARCHAR(20) | NOT NULL, CHECK IN('success','error') | 상태 | 'success' |
| error_code | VARCHAR(50) | NULL | 오류 코드 | NULL |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 | now() |

**인덱스**
- fk_infruns_conversation(conversation_id)
- idx_infruns_created(created_at), idx_infruns_status(status)


---

# 📘 API 명세서  (Django + DRF)

## 공통
- 인증: `Authorization: Bearer <access_token>` (SimpleJWT (Refresh 회전 + 블랙리스트), SimpleSimpleJWT (Refresh 회전 + 블랙리스트))
- 응답: **순수 JSON(래핑 없음)** — 단일 리소스/컬렉션 그대로 반환
- 문서화: **drf-spectacular** —
  - `GET /api/schema/` (OpenAPI)
  - `GET /api/docs/` (Swagger UI)
  - `GET /api/redoc/` (ReDoc)

### 보안/성능 목표
- 쓰로틀: 익명 `20/min`, 사용자 `60/min`
- 성능 목표(t2.micro): **평균 응답 ≤ 2초, 동시 30**

---

## 1. 인증/권한 - SimpleJWT (Refresh 회전 + 블랙리스트)
### 1.1 회원가입 — `POST /api/v1/auth/signup`
```json
{ "username": "damon", "email": "d@m.com", "password": "Str0ngPass!" }
```
**201**
```json
{ "id": 1, "username": "damon", "email": "d@m.com", "created_at": "2025-09-09T12:00:00Z" }
```

### 1.2 로그인 — `POST /api/v1/auth/login`
```json
{ "username": "damon", "password": "Str0ngPass!" }
```
**200**
```json
{ "access": "jwt-access", "refresh": "jwt-refresh", "token_type": "Bearer", "expires_in": 3600 }
```

### 1.3 토큰 재발급 — `POST /api/v1/auth/refresh`
```json
{ "refresh": "jwt-refresh" }
```
**200**
```json
{ "access": "new-access", "expires_in": 3600 }
```

### 1.4 로그아웃 — `POST /api/v1/auth/logout`
- 설명: 클라이언트 토큰 삭제 + (선택) 서버에 Refresh 블랙리스트
**204 No Content**

---

## 2. 사용자
### 2.1 내 정보 — `GET /api/v1/users/me`
**200**
```json
{ "id": 1, "username": "damon", "nickname": "다몬", "email": "d@ex.com", "image_url": null }
```

### 2.2 수정 — `PATCH /api/v1/users/me`
```json
{ "nickname": "새닉", "image_url": "https://example.com/avatar.png" }
```

### 2.3 비밀번호 변경 — `POST /api/v1/users/me/password`
```json
{ "current_password": "Str0ngPass!", "new_password": "EvenStronger#1" }
```

---

## 3. 대화/메시지
### 3.1 대화 생성 — `POST /api/v1/conversations`
```json
{ "title": "주간 회의록" }
```
**201**
```json
{ "id": 10, "title": "주간 회의록", "owner_id": 1, "created_at": "2025-09-09T12:00:00Z" }
```

### 3.2 대화 조회/수정/삭제
- `GET /api/v1/conversations/{id}`
- `PATCH /api/v1/conversations/{id}`
- `DELETE /api/v1/conversations/{id}`

### 3.3 메시지 추가 — `POST /api/v1/conversations/{id}/messages`
```json
{ "role": "user", "content": "오늘 날씨 알려줘" }
```
**201**
```json
{ "id": 100, "role": "user", "content": "오늘 날씨 알려줘", "created_at": "2025-09-09T12:00:00Z" }
```

### 3.4 메시지 목록 — `GET /api/v1/conversations/{id}/messages`

---

## 4. 태그
### 4.1 태그 CRUD
- `POST /api/v1/tags`
- `GET /api/v1/tags`
- `PATCH /api/v1/tags/{id}`
- `DELETE /api/v1/tags/{id}`

### 4.2 대화↔태그 연결/해제
- `POST /api/v1/conversations/{id}/tags`
```json
{ "tag_ids": [1,2,3] }
```
**200**
```json
{ "added": [1,2,3] }
```
- `DELETE /api/v1/conversations/{id}/tags/{tag_id}` → **204**

---

## 5. AI 추론
### 5.1 Gemini 호출 — `POST /api/v1/inference`
```json
{
  "conversation_id": 10,
  "prompt": "회의록 요약해줘",
  "options": { "temperature": 0.3, "max_output_tokens": 1024 }
}
```
**200**
```json
{
  "message_id": 101,
  "role": "assistant",
  "content": "회의록 주요 내용은...",
  "usage": { "prompt_tokens": 123, "completion_tokens": 456 }
}
```

---

## 6. 데이터 전처리
### 6.1 데이터셋 등록 — `POST /api/v1/datasets`
```json
{ "name": "news_corpus_v1", "source": "file", "uri": "s3://bucket/raw/news_v1.csv" }
```
**201**
```json
{ "id": 1, "name": "news_corpus_v1", "source": "file", "uri": "s3://bucket/raw/news_v1.csv", "created_at": "2025-09-09T12:00:00Z" }
```

### 6.2 전처리 작업 생성 — `POST /api/v1/datasets/{id}/preprocess`
> 같은 `client_job_id`로 재시도 시, 기존 작업을 반환하거나 동일 결과를 200으로 제공합니다(멱등).
```json
{
  "steps": [{"op":"normalize"},{"op":"dedupe"},{"op":"fillna"},{"op":"tokenize"}],
  "client_job_id": "optional-unique-key-per-dataset"
}
```
**202**
```json
{ "job_id": 101, "status": "queued", "idempotent": true }
```

### 6.3 전처리 작업 조회 — `GET /api/v1/preprocessing-jobs/{job_id}`
**200**
```json
{ "id": 101, "dataset_id": 1, "status": "running", "started_at": "2025-09-09T12:01:00Z", "finished_at": null }
```

### 6.4 전처리 작업 목록 — `GET /api/v1/preprocessing-jobs?dataset_id=1&status=running`

---

## 7. 추론 모니터링
### 7.1 목록 — `GET /api/v1/inference-runs?conversation_id=10&status=success`
**200**
```json
[{
  "id": 1, "conversation_id": 10, "message_id": 101, "model": "gemini-1.5",
  "latency_ms": 420, "prompt_tokens": 123, "completion_tokens": 456,
  "status": "success", "created_at": "2025-09-09T12:00:00Z"
}]
```

### 7.2 상세 — `GET /api/v1/inference-runs/{id}`

---

## 8. 유틸
### 8.1 Health/Readiness
- `GET /healthz` — 앱 가동 확인(무인증, 200) SimpleJWT (Refresh 회전 + 블랙리스트)
- `GET /readiness` — 의존성(DB 등) 점검(200/503)

### 8.2 OpenAPI/Swagger
- `GET /api/schema/`, `GET /api/docs/`, `GET /api/redoc/`