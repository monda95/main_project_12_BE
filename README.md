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

## 📘 서비스 개요 & 핵심 기능 요약

> 플루언트는 인터렉티브 **디지털 휴먼 AI 가상비서 서비스**를 운영 중이며, 이에 필요한 **AI 모델 배포용 API 서버**를 제공합니다.
> 서버는 사용자 요청을 받아 모델을 호출하고(JSON), 결과를 저장/반환하며, 추론 성능과 데이터 파이프라인을 관리합니다.

### 1) 서비스 개요
- 대상 환경: Windows + PyCharm, uv, Docker Compose, PostgreSQL(AWS RDS 가능), Django + DRF, AWS EC2 배포, Google Gemini API 연동  
- 상세 근거: 본문 “개요/환경” 및 기술 스택 참조.

### 2) 주요 기능
- **기능 1: 데이터베이스 설계** *(우선순위: 높음)*
  - 모델 예측 결과, 사용자 입력, **모델 성능 모니터링** 데이터를 저장하는 스키마 설계.  
  - 자세히 보기: **ERD** 및 **테이블 명세**, **추론 모니터링 API(7장)**

- **기능 2: API 서버 설계 및 구현** *(우선순위: 높음)*
  - RESTful API로 모델 호출 및 결과 JSON 반환. JWT 인증/세션, 유효성 검증/에러 처리 강화.  
  - 자세히 보기: **AI 추론 API(5장)**, **유틸/헬스체크(8장)**

- **기능 3: 데이터 전처리 개발** *(우선순위: 중간)*
  - 정규화/중복 제거/결측 처리/텍스트 정규화·토큰화 등 **전처리 파이프라인** 자동화.  
  - 다양한 소스 수집 → **일관 포맷 변환**.  
  - 자세히 보기: **데이터 전처리 API(6장)**

- **기능 4: API 테스트 & 모델 배포/모니터링** *(우선순위: 중간)*
  - 응답 시간/정확성/오류 처리 점검 및 최적화, **로그·모니터링** 구축.  
  - AWS 인프라(EC2, S3, RDS 등)로 안정적 배포 및 확장성 유지.  
  - 자세히 보기: **유틸/헬스체크(8장)** 및 인프라 섹션

### 3) 기술 요구사항
- **서버:** Python(Flask/FastAPI 등 가능) 기반 API *(본 프로젝트는 Django + DRF 채택)*  
- **API:** RESTful  
- **DB:** docker-compose + PostgreSQL  
- **형상관리:** Git  
- **인프라:** AWS(EC2, S3, RDS 등)

> **추적성(Traceability) 빠르게 보기**
> - 모델 호출/응답: *AI 추론* → `POST /api/v1/inference`  
> - 추론 성능 로깅: *추론 모니터링* → `GET /api/v1/inference-runs`  
> - 데이터 수명주기: *데이터 전처리* → `POST /api/v1/datasets`, `GET /api/v1/preprocessing-jobs`  
> - 상세는 아래 **API 명세** 및 **요구사항 표** 참조

```bash
main-project/
├── apps/
│   ├── conversations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── serializers.py
│   ├── core/
│   │   └── permissions.py
│   ├── datasets/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── serializers.py
│   ├── inference/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── services.py
│   └── users/
│       ├── models.py
│       ├── views.py
│       └── serializers.py
└── config/
    ├── urls.py
    └── settings/
        ├── base.py
        ├── dev.py
        └── prod.py
```

## 📑 사용자 요구설명서 (개인 프로젝트)

## 1. 개요
- 서비스: 인터랙티브 **디지털 휴먼 AI 가상비서(Fluent AI Assistant)**를 위한 **AI 모델 배포용 API 서버**.
- 대상 환경: **Windows + PyCharm**, **uv** 패키지, **Docker Compose**, **PostgreSQL(AWS RDS 가능)**, **Django + DRF**, **AWS EC2** 배포, **Google Gemini API** 연동.

## 2. 요구사항 목록

| 요구사항 ID | 요구사항 명 | 구분 | 설명                                            | 중요도 | 비고 |
|---|---|---|-----------------------------------------------|---|---|
| DH_RF01001 | 회원가입(자체) | 기능 | 이메일 중복 검사, 비밀번호 유효성 검사                        | 상 | 운영에선 이메일 인증 필수 | - SimpleJWT (Refresh 회전 + 블랙리스트)
| DH_RF01002 | 로그인/토큰 발급 | 기능 | SimpleJWT (Refresh 회전 + 블랙리스트)), 재발급 지원       | 상 | SimpleSimpleJWT (Refresh 회전 + 블랙리스트)
| DH_RF01003 | 로그아웃 | 기능 | 클라이언트 토큰 삭제, (선택) 서버 Refresh 블랙리스트            | 상 | 블랙리스트 앱 사용 가능 |
| DH_RF01004 | 마이페이지 조회/수정 | 기능 | 닉네임·이미지 등 정보 수정                               | 중 | 개인정보 보호 고려 |
| DH_RF01005 | 비밀번호 변경 | 기능 | 기존 비밀번호 검증 후 변경                               | 상 | OWASP 권고 준수 |
| DH_RF02001 | 대화 관리 | 기능 | 대화 생성/조회/수정/삭제                                | 상 | 사용자 소유권 유지 |
| DH_RF02002 | 메시지 관리 | 기능 | 대화 내 메시지 작성/조회(페이징)                           | 상 | |
| DH_RF02003 | 태그 관리 | 기능 | 태그 CRUD, 대화↔태그 연결/해제                          | 중 | M:N(ConversationTag) |
| DH_RF03001 | AI 추론(Gemini) | 기능 | 프롬프트 전달·응답 저장/반환                              | 상 | 옵션(temperature,max_tokens) |
| DH_RF03002 | **모델 성능 모니터링 데이터 저장** | 기능 | 추론별 latency/status/tokens 저장                  | 중 | `inference_runs` |
| DH_RF02004 | **데이터 전처리 파이프라인** | 기능 | Dataset 등록·전처리 Job 생성/조회                      | 중 | `datasets`, `preprocessing_jobs` |
| DH_RQ04001 | 보안성 | 비기능 | 모든 API는 HTTPS, SimpleJWT (Refresh 회전 + 블랙리스트) 
| DH_RQ04002 | 성능 | 비기능 | **평균 응답 ≤ 2초, 동시 30**(t2.micro 기준)            | 중 | |
| DH_RQ04003 | 개발/배포 | 비기능 | Git 관리, Dev/Prod 차이 최소화                       | 중 | |
| DH_RQ04IDEMP | 멱등성(전처리 한정) | 비기능 | 전처리 생성에 `client_job_id` 지원                    | 중 | UNIQUE(dataset_id, client_job_id) |

## 3. 제약 및 참고
- 인증: **SimpleSimpleJWT (Refresh 회전 + 블랙리스트)).
- 문서화: **drf-spectacular** + Swagger UI(`/api/swagger/`).
- DB: **PostgreSQL**(문서의 모든 타입/제약은 Postgres 기준).
- 배포: **Docker Compose → EC2**, Readiness/Health 엔드포인트 제공.


---

# 📊 ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    User {
        bigint id PK
        string email "UNIQUE NOT NULL; LOWER(email) 인덱스"
        string username "NOT NULL"
        string password "NOT NULL"
        string nickname "NULL"
        string image_url "NULL"
        string phone_number "NULL"
        boolean is_active "NOT NULL DEFAULT true"
        timestamptz email_verified_at "NULL"
        timestamptz created_at "NOT NULL DEFAULT now()"
        timestamptz updated_at "NOT NULL DEFAULT now()"
        timestamptz deactivated_at "NULL"
    }

    Conversation {
        bigint id PK
        bigint owner_id FK "NOT NULL; FK→User.id; ON DELETE CASCADE"
        string title "NOT NULL"
        timestamptz created_at "NOT NULL DEFAULT now()"
        timestamptz updated_at "NOT NULL DEFAULT now()"
    }

    Message {
        bigint id PK
        bigint conversation_id FK "NOT NULL; FK→Conversation.id; ON DELETE CASCADE"
        string role "NOT NULL CHECK IN('user','assistant','system')"
        text content "NOT NULL"
        timestamptz created_at "NOT NULL DEFAULT now()"
    }

    Tag {
        bigint id PK
        string name "UNIQUE NOT NULL (저장 시 lower 변환)"
        timestamptz created_at "NOT NULL DEFAULT now()"
    }

    ConversationTag {
        bigint id PK
        bigint conversation_id FK "NOT NULL; FK→Conversation.id; ON DELETE CASCADE"
        bigint tag_id FK "NOT NULL; FK→Tag.id; ON DELETE CASCADE"
        timestamptz created_at "NOT NULL DEFAULT now()"
        UNIQUE "conversation_id, tag_id"
    }

    Dataset {
        bigint id PK
        bigint owner_id FK "NOT NULL; FK→User.id; ON DELETE CASCADE"
        string name "NOT NULL"
        string source "NULL"
        string uri "NULL"
        timestamptz created_at "NOT NULL DEFAULT now()"
    }

    PreprocessingJob {
        bigint id PK
        bigint dataset_id FK "NOT NULL; FK→Dataset.id; ON DELETE CASCADE"
        string client_job_id "NULL; UNIQUE(dataset_id, client_job_id) WHERE client_job_id IS NOT NULL"
        string status "NOT NULL DEFAULT 'queued' CHECK IN('queued','running','succeeded','failed')"
        jsonb steps "NULL"
        timestamptz created_at "NOT NULL DEFAULT now()"
        timestamptz started_at "NULL"
        timestamptz finished_at "NULL"
    }

    InferenceRun {
        bigint id PK
        bigint conversation_id FK "NOT NULL; FK→Conversation.id; ON DELETE CASCADE"
        bigint message_id FK "NULL; FK→Message.id; ON DELETE SET NULL"
        string model "NOT NULL"
        integer latency_ms "NOT NULL"
        integer prompt_tokens "NULL"
        integer completion_tokens "NULL"
        string status "NOT NULL DEFAULT 'success' CHECK IN('success','error')"
        string error_code "NULL"
        timestamptz created_at "NOT NULL DEFAULT now()"
    }

    %% 관계
    User ||--o{ Conversation : "1:N"
    Conversation ||--o{ Message : "1:N"

    Conversation ||--o{ ConversationTag : "1:N"
    Tag ||--o{ ConversationTag : "1:N"

    Conversation ||--o{ InferenceRun : "1:N"
    Message ||--o{ InferenceRun : "1:N"

    User ||--o{ Dataset : "1:N"
    Dataset ||--o{ PreprocessingJob : "1:N"
```

---

# 🗄️ 테이블 명세서 (PostgreSQL)

## 1. users
| 컬럼                | 타입           | 제약           | 설명                    | 기본값   |
|-------------------|--------------|--------------|-----------------------|-------|
| id                | BIGSERIAL    | PK           | 사용자 ID                | -     |
| email             | VARCHAR(254) | UNIQUE, NOT NULL | 로그인 이메일(인증대상)         | -     |
| username          | VARCHAR(100) | NOT NULL     | 가입자 이름 (동명이인->비고유)    | -     |
| password          | VARCHAR(255) | NOT NULL     | 해시된 비밀번호              | -     |
| nickname          | VARCHAR(25)  | NULL         | 닉네임                   | NULL  |
| image_url         | VARCHAR(500) | NULL         | 프로필 이미지 URL           | NULL  |
| phone_number      | VARCHAR(25)  | NULL         | 전화번호 (정규화 : 숫자만)      | NULL  |
| is_active         | BOOLEAN      | NOT NULL     | 계정 활성화 여부             | true  |
| email_verified_at | TIMESTAMPTZ  | NULL         | 이메일 인증 시각 (인증 전 NULL) | NULL  |
| created_at        | TIMESTAMPTZ  | NOT NULL     | 생성 시각                 | now() |
| updated_at        | TIMESTAMPTZ  | NOT NULL     | 수정 시각                 | now() |
| deactivated_at    | TIMESTAMPTZ  | NULL         | 탈퇴 시각                 | NULL  |

**인덱스**
- `uq_users_email_ci` (LOWER(email))
- idx_users_username(username), idx_users_email(email)

---

## 2. conversations
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 대화 ID | - |
| owner_id | BIGINT | NOT NULL, FK→users(id) ON DELETE CASCADE | 소유자 | - |
| title | VARCHAR(200) | NOT NULL | 대화 제목 | - |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 시각 | now() |
| updated_at | TIMESTAMPTZ | NOT NULL | 수정 시각 | now() |

**인덱스**
- idx_conversations_owner(owner_id), idx_conversations_created(created_at)

---

## 3. messages
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 메시지 ID | - |
| conversation_id | BIGINT | NOT NULL, FK→conversations(id) ON DELETE CASCADE | 소속 대화 | - |
| role | VARCHAR(10) | NOT NULL, CHECK IN('user','assistant','system') | 역할 | - |
| content | TEXT | NOT NULL | 내용 | - |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 시각 | now() |

**인덱스**
- idx_messages_conv(conversation_id), idx_messages_created(created_at), idx_messages_conv_created(conversation_id, created_at)

---

## 4. tags
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 태그 ID | - |
| name | VARCHAR(50) | UNIQUE, NOT NULL | 태그명 (저장 시 소문자로 변환) | - |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 시각 | now() |

**인덱스**
- idx_tags_name(name)

---

## 5. conversation_tags
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 연결 ID | - |
| conversation_id | BIGINT | NOT NULL, FK→conversations(id) ON DELETE CASCADE | 대화 | - |
| tag_id | BIGINT | NOT NULL, FK→tags(id) ON DELETE CASCADE | 태그 | - |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 시각 | now() |

**인덱스 / 제약**
- idx_ct_conv(conversation_id), idx_ct_tag(tag_id)
- UNIQUE(conversation_id, tag_id)

---

## 6. datasets
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 데이터셋 ID | - |
| owner_id | BIGINT | NOT NULL, FK→users(id) ON DELETE CASCADE | 소유자 | - |
| name | VARCHAR(100) | NOT NULL | 데이터셋명 | - |
| source | VARCHAR(100) | NULL | 원천(file/crawl/api 등) | NULL |
| uri | VARCHAR(500) | NULL | 원본 위치(S3 키 등) | NULL |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 시각 | now() |

**인덱스**
- idx_datasets_owner(owner_id), idx_datasets_name(name), idx_datasets_created(created_at)

---

## 7. preprocessing_jobs
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 전처리 작업 ID | - |
| dataset_id | BIGINT | NOT NULL, FK→datasets(id) ON DELETE CASCADE | 대상 데이터셋 | - |
| client_job_id | VARCHAR(64) | NULL | **멱등키(데이터셋별 유일)** | NULL |
| status | VARCHAR(20) | NOT NULL, CHECK IN('queued','running','succeeded','failed') | 상태 | 'queued' |
| steps | JSONB | NULL | 단계 정의 | NULL |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 시각 | now() |
| started_at | TIMESTAMPTZ | NULL | 시작 시각 | NULL |
| finished_at | TIMESTAMPTZ | NULL | 종료 시각 | NULL |

**인덱스 / 제약**
- fk_prejobs_dataset(dataset_id)
- **UNIQUE(dataset_id, client_job_id) WHERE client_job_id IS NOT NULL**
- idx_prejobs_status_created(status, created_at)

---

## 8. inference_runs
| 컬럼 | 타입 | 제약 | 설명 | 기본값 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | 추론 실행 ID | - |
| conversation_id | BIGINT | NOT NULL, FK→conversations(id) ON DELETE CASCADE | 대화 | - |
| message_id | BIGINT | NULL, FK→messages(id) ON DELETE SET NULL | 관련 메시지 | NULL |
| model | VARCHAR(50) | NOT NULL | 모델명 | - |
| latency_ms | INTEGER | NOT NULL | 지연(ms) | - |
| prompt_tokens | INTEGER | NULL | 프롬프트 토큰 | NULL |
| completion_tokens | INTEGER | NULL | 응답 토큰 | NULL |
| status | VARCHAR(20) | NOT NULL, CHECK IN('success','error') | 상태 | 'success' |
| error_code | VARCHAR(50) | NULL | 오류 코드 | NULL |
| created_at | TIMESTAMPTZ | NOT NULL | 생성 시각 | now() |

**인덱스**
- fk_infruns_conversation(conversation_id)
- idx_infruns_created(created_at), idx_infruns_status(status)


---

# 📘 API 명세서  (Django + DRF)

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
| `/api/v1/auth/logout` | `POST` | 로그아웃 (Refresh 토큰 블랙리스트) | **인증된 사용자** |

### 1.1 회원가입 — `POST /api/v1/auth/signup`
**Request Body**
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
**Request Body**
```json
{ "email": "user@example.com", "password": "Str0ngPass!" }
```
**Response (200 OK)**
```json
{ "access": "jwt-access-token", "refresh": "jwt-refresh-token" }
```

### 1.3 토큰 재발급 — `POST /api/v1/auth/refresh`
**Request Body**
```json
{ "refresh": "jwt-refresh-token" }
```
**Response (200 OK)**
```json
{ "access": "new-access-token" }
```

### 1.4 로그아웃 — `POST /api/v1/auth/logout`
**Request Body**
```json
{ "refresh": "jwt-refresh-token" }
```
**Response (204 Reset Content)**

---

## 2. 사용자

| 엔드포인트 | 메서드      | 설명                     | 권한 |
|---|----------|------------------------|---|
| `/api/v1/users/me` | `GET`    | 내 정보 조회                | **인증된 사용자** |
| `/api/v1/users/me` | `PATCH`  | 내 정보 수정 (닉네임, 프로필 이미지) | **인증된 사용자** |
| `/api/v1/users/me` | `DELETE` | 회원 탈퇴                  | **인증된 사용자** |
| `/api/v1/users/me/password` | `POST`   | 비밀번호 변경                | **인증된 사용자** |

### 2.1 내 정보 조회 (`/users/me`)
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

### 2.2 내 정보 수정 (`/users/me`)
**Request Body**
```json
{ "nickname": "새로운 닉네임", "image_url": "https://example.com/avatar.png" }
```
**Response (200 OK)**: 수정된 필드를 포함한 전체 사용자 정보

### 2.3 비밀번호 변경 (`/users/me/password`)
**Request Body**
```json
{ "current_password": "Str0ngPass!", "new_password": "EvenStronger#1" }
```
**Response (204 No Content)**

### 2.4 회원 탈퇴 (/users/me)
| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| /api/v1/users/me | DELETE | 회원 탈퇴 (계정 비활성화) | 인증된 사용자 |

**Response (204 No Content)**

---

## 3. 대화/메시지

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/api/v1/conversations` | `GET`, `POST` | 내 대화 목록 조회, 새 대화 생성 | **인증된 사용자** |
| `/api/v1/conversations/{id}` | `GET`, `PATCH`, `DELETE` | 특정 대화 조회/수정/삭제 | **소유자** |
| `/api/v1/conversations/{id}/messages` | `GET`, `POST` | 대화 내 메시지 목록 조회, 추가 | **소유자** |

### 3.1 대화 목록 조회 — `GET /api/v1/conversations`
**Response (200 OK)**
```json
[
  { "id": 10, "title": "주간 회의록", "owner_id": 1, "created_at": "..." },
  { "id": 11, "title": "새로운 아이디어", "owner_id": 1, "created_at": "..." }
]
```

### 3.2 대화 생성 — `POST /api/v1/conversations`
**Request Body**
```json
{ "title": "새로운 대화" }
```
**Response (201 Created)**
```json
{ "id": 12, "title": "새로운 대화", "owner_id": 1, "created_at": "..." }
```

### 3.3 대화 삭제 — `DELETE /api/v1/conversations/{id}`
**Response (204 No Content)**

### 3.4 메시지 목록 조회 — `GET /api/v1/conversations/{id}/messages`
**Response (200 OK)**: 메시지 목록 (페이지네이션 적용)
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

### 3.5 메시지 추가 — `POST /api/v1/conversations/{id}/messages`
**Request Body**
```json
{ "role": "user", "content": "내일 날씨는?" }
```
**Response (201 Created)**
```json
{ "id": 102, "role": "user", "content": "내일 날씨는?", "created_at": "..." }
```

---

## 4. 태그

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/api/v1/tags` | `GET`, `POST` | 태그 목록 조회, 새 태그 생성 | **인증된 사용자** |
| `/api/v1/tags/{id}` | `GET`, `PATCH`, `DELETE` | 특정 태그 조회/수정/삭제 | **인증된 사용자** |
| `/api/v1/conversations/{id}/tags` | `POST` | 대화에 여러 태그 연결 | **소유자** |
| `/api/v1/conversations/{id}/tags/{tag_id}` | `DELETE` | 대화에서 특정 태그 연결 해제 | **소유자** |

### 4.1 태그 생성 — `POST /api/v1/tags`
**Request Body**
```json
{ "name": "my-new-tag" }
```
**Response (201 Created)**
```json
{ "id": 5, "name": "my-new-tag", "created_at": "..." }
```

### 4.2 대화에 태그 연결 — `POST /api/v1/conversations/{id}/tags`
**Request Body**
```json
{ "tag_ids": [1, 2, 3] }
```
**Response (200 OK)**: 연결된 전체 태그 목록
```json
[
  { "id": 1, "name": "work" },
  { "id": 2, "name": "idea" },
  { "id": 3, "name": "project-x" }
]
```

### 4.3 대화에서 태그 연결 해제 — `DELETE /api/v1/conversations/{id}/tags/{tag_id}`
**Response (204 No Content)**

---

## 5. AI 추론

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/api/v1/inference` | `POST` | Gemini 호출 및 응답 생성 | **인증된 사용자** |

### 5.1 Gemini 호출 — `POST /api/v1/inference`
**Request Body**
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

## 6. 데이터 전처리 (관리자 기능)

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/api/v1/datasets` | `GET`, `POST` | 데이터셋 목록/생성 | **관리자** |
| `/api/v1/datasets/{id}` | `GET`, `PATCH`, `DELETE` | 특정 데이터셋 조회/수정/삭제 | **관리자** |
| `/api/v1/datasets/{id}/preprocess` | `POST` | 데이터셋 전처리 작업 생성 | **관리자** |
| `/api/v1/preprocessing-jobs` | `GET` | 모든 전처리 작업 목록 조회 | **관리자** |
| `/api/v1/preprocessing-jobs/{job_id}` | `GET` | 특정 전처리 작업 조회 | **관리자** |

### 6.1 데이터셋 등록 — `POST /api/v1/datasets`
```json
{ "name": "news_corpus_v1", "source": "file", "uri": "s3://bucket/raw/news_v1.csv" }
```
**201**
```json
{ "id": 1, "name": "news_corpus_v1", "source": "file", "uri": "s3://bucket/raw/news_v1.csv", "created_at": "2025-09-09T12:00:00Z" }
```

### 6.2 전처리 작업 생성 — `POST /api/v1/datasets/{id}/preprocess`
> 멱등키 정책(동일 dataset+client_job_id 재시도=기존 Job 반환),
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

```
**Response (202 Accepted)**
```json
{ "job_id": 101, "status": "queued" }
```

---

## 7. 추론 모니터링 (관리자 기능)

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/api/v1/inference-runs` | `GET` | 모든 추론 기록 조회 | **관리자** |
| `/api/v1/inference-runs/{id}` | `GET` | 특정 추론 기록 조회 | **관리자** |

### 7.1 추론 기록 목록 조회 — `GET /api/v1/inference-runs`
**Response (200 OK)**
```json
[
  {
    "id": 1, 
    "conversation_id": 10, 
    "message_id": 101, 
    "model": "gemini-1.5",
    "latency_ms": 420, 
    "prompt_tokens": 123, 
    "completion_tokens": 456,
    "status": "success", 
    "created_at": "..."
  }
]
```
### 7.2 상세 — `GET /api/v1/inference-runs/{id}`

---

## 8. 유틸

| 엔드포인트 | 메서드 | 설명 | 권한 |
|---|---|---|---|
| `/healthz` | `GET` | 앱 가동 확인 | 누구나 |
| `/readiness` | `GET` | 의존성(DB 등) 점검 | 누구나 |
### 8.1 Health Check (`/healthz`)
**Response (200 OK)**
```
OK
```

### 8.2 Readiness Check (`/readiness`)
**Response (200 OK)**
```
OK
```
**Response (503 Service Unavailable)**
```
Service Unavailable
```