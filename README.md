# 🤖 디지털 휴먼 AI 가상비서 (Fluent AI Assistant)

> **디지털 휴먼 AI 가상비서**를 위한 API 서버  
> Google Gemini API 연동으로 대화형 AI 서비스 제공 및 성능 모니터링 시스템  
> 
> 본 문서는 개인 프로젝트로 진행 중이며 **배포 가능한 최소기능(MVP)**을 우선으로 하되, 
> 추후 확장을 고려한 표준/일관성 확보를 위한 설계를 정리한 문서입니다.

---
## 📚 설계 문서

* [📋 사용자 요구사항](docs/01_사용자요구사항.md)
* [🗄️ ERD](docs/02_ERD.md)
* [📊 테이블 명세서](docs/03_테이블명세서.md)
* [🔌 API 명세서](docs/04_API명세서.md)

---

## 🎯 서비스 개요

**인터렉티브 디지털 휴먼 AI 가상비서 서비스**를 위한 백엔드 API 서버입니다. 사용자 요청을 받아 AI 모델을 호출하고, 결과를 저장/반환하며, 추론 성능과 데이터 파이프라인을 관리합니다.


### 핵심 기능

| 기능          | 우선순위  | 설명                              |
| ----------- | ----- | ------------------------------- |
| **API 서버**  | 🔴 높음 | RESTful API, JWT 인증, JSON 응답 처리 |
| **데이터베이스**  | 🔴 높음 | 대화 기록, 추론 결과, 성능 모니터링           |
| **데이터 전처리** | 🟡 중간 | 정규화, 토큰화, 자동 파이프라인              |
| **배포/모니터링** | 🟡 중간 | AWS 인프라, 성능 최적화                 |

---

## 🛠️ 기술 스택

| 영역           | 기술                      |
| ------------ | ----------------------- |
| **Backend**  | Django + DRF            |
| **Database** | PostgreSQL (AWS RDS)    |
| **AI**       | Google Gemini API       |
| **Infra**    | Docker Compose, AWS EC2 |
| **Dev**      | PyCharm, uv (패키지 관리)    |
| **Auth**     | JWT + OAuth             |

---

## 📁 프로젝트 구조

```bash
main-project/
├── apps/                    # Django 앱들
│   ├── 💬 conversations/   # 대화 관리 (대화방, 메시지)
│   │   ├── models.py
│   │   ├── views.py
│   │   └── serializers.py
│   ├── 🤖 inference/       # AI 추론 처리 (모델 호출, 성능 모니터링)  
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── services.py
│   ├── 📊 datasets/        # 데이터셋 관리 (전처리, 파이프라인)
│   │   ├── models.py
│   │   ├── views.py
│   │   └── serializers.py
│   ├── 👤 users/           # 사용자 인증 (계정, OAuth)
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── utils.py
│   └── 🔧 core/            # 공통 유틸리티 (권한, 미들웨어)
│       └── permissions.py
└── config/                  # Django 설정
    ├── urls.py
    └── settings/
        ├── base.py
        ├── dev.py
        └── prod.py
```

---

## 🗄️ 데이터베이스 설계

### 핵심 엔티티
- **User**: 사용자 계정 및 OAuth 연동 관리
- **Conversation**: 대화방 및 메시지 이력 관리  
- **InferenceRun**: AI 추론 성능 모니터링 및 로깅
- **Dataset**: 데이터셋 관리 및 전처리 작업 추적

### ERD 다이어그램 (요약)

```mermaid
erDiagram
    User {
        bigint id PK
        string email "UK, NOT NULL, lowercase"
        string username "NOT NULL"
        string password "NOT NULL"
        string nickname "NULL"
        string image_url "NULL"
        string phone_number "NULL"
        boolean is_active "DEFAULT true"
        timestamptz email_verified_at "NULL"
        timestamptz created_at "auto_now_add"
        timestamptz updated_at "auto_now"
        timestamptz deactivated_at "NULL"
    }

    OAuthAccount {
        bigint id PK
        bigint user_id FK
        string provider "NOT NULL"
        string subject "NOT NULL"
        string email "NULL"
        boolean email_verified "DEFAULT false"
        timestamptz created_at "auto_now_add"
        UK (provider, subject)
    }

    Conversation {
        bigint id PK
        bigint owner_id FK
        string title "NOT NULL"
        timestamptz created_at "auto_now_add"
        timestamptz updated_at "auto_now"
    }

    Message {
        bigint id PK
        bigint conversation_id FK
        string role "user/assistant/system"
        text content "NOT NULL"
        timestamptz created_at "auto_now_add"
    }

    Dataset {
        bigint id PK
        bigint owner_id FK
        string name "NOT NULL"
        string source "NULL"
        string uri "NULL"
        timestamptz created_at "auto_now_add"
    }

    PreprocessingJob {
        bigint id PK
        bigint dataset_id FK
        string client_job_id "NULL"
        string status "queued/running/succeeded/failed"
        timestamptz created_at "auto_now_add"
    }

    InferenceRun {
        bigint id PK
        bigint conversation_id FK
        bigint message_id FK "nullable"
        string model "NOT NULL"
        integer latency_ms "NOT NULL"
        string status "success/error"
        string error_code "NULL"
        text error_message "NULL"
        timestamptz created_at "auto_now_add"
    }

    %% --- 관계 ---
    User ||--o{ Conversation : "1:N"
    Conversation ||--o{ Message : "1:N"
    Conversation ||--o{ InferenceRun : "1:N"
    Message ||--o{ InferenceRun : "1:N"
    User ||--o{ Dataset : "1:N"
    Dataset ||--o{ PreprocessingJob : "1:N"

```

> 📌 상세 스키마는 [ERD](docs/02_ERD.md), [테이블 명세서](docs/03_테이블명세서.md)를 참고

---

## ⚡ Quick Start

```bash
git clone <repo-url>
cd main-project
uv venv && uv sync
cp .env.example .env   # 환경변수 설정

docker-compose up -d --build
docker-compose exec uv run manage.py migrate
```

---

## 🔐 보안 & 인증

* JWT 토큰 인증
* OAuth 소셜 로그인(Google, Github 등)
* HTTPS 통신 암호화
* 입력 데이터 유효성 검증