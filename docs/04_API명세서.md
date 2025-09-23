
### 검색 (Search / Stats 연계)

- `GET /api/v1/search-logs/autocomplete?prefix=...` — 검색 자동완성
- `GET /api/v1/queries/recent` — 최근 검색
- `GET /api/v1/queries/recommended` — 개인화 추천 질문 (Gemini 기반)
- `GET /api/v1/search-logs/popular` — 인기 검색어 (관리자 전용, stats 앱 제공)

## 인증
- `POST /api/v1/auth/signup` — 회원가입
- `POST /api/v1/auth/login` — 로그인(JWT)
- `POST /api/v1/auth/refresh` — 토큰 재발급
- `POST /api/v1/auth/logout` — 로그아웃
- `POST /api/v1/auth/oauth2/exchange` — OAuth 교환

---

## 대화/메시지
- `POST   /api/v1/conversations` — 새 대화 생성 (비로그인 허용: owner_id=NULL)
- `GET    /api/v1/conversations/{id}` — 특정 대화 조회
- `PATCH  /api/v1/conversations/{id}` — 대화 제목 수정
- `DELETE /api/v1/conversations/{id}` — 대화 삭제 : ⚠️  대화 삭제 시 연결된 **메시지(Message)** 및 **추론 로그(InferenceRun)** 도 함께 삭제됨 (ON DELETE CASCADE)
- `POST   /api/v1/conversations/{id}/messages` — 메시지 생성 (role=user)
- `GET    /api/v1/conversations/{id}/messages` — 대화 내 메시지 목록 조회

---

## AI 추론 (Self-Check 메타 포함)
- `POST /api/v1/inference`
  - **요청**:  
    ```json
    { "conversation_id": 123, "prompt": "..." }
    ```
  - **처리**: 모델 호출 → **Self-Check** 규칙 검사 → (필요 시 1회 보정) → 최종 저장(messages, inference_runs)
  - **응답**:  
    ```json
    {
      "conversation_id": 123,
      "message_id": 456,
      "role": "assistant",
      "content": {
        "nutrition": "...",
        "allergy": "...",
        "storage": "...",
        "processing": "...",
        "source": "..."
      },
      "usage": { "prompt_tokens": 123, "completion_tokens": 456 },
      "latency_ms": 789,
      "self_check": {
        "check_pass": true,
        "retry_used": false,
        "violations": []
      }
    }
    ```
  - **DB 반영**: `inference_runs.check_pass|retry_used|violations` (Nullable)

---

## 검색 로그 / 추천(통계 기반)
- `POST /api/v1/search-logs` — `{ "query": "원문" }` (서버가 `normalized_query` 생성)
- `GET  /api/v1/queries/suggest?prefix=...` — **자동완성** (정규화/코오커런스 기반)
- `GET  /api/v1/queries/recent` — **최근 질의** (사용자/익명 기준)
- `GET  /api/v1/queries/recommended` — **추천 질문은 Celery beat + Gemini API를 통한 배치 생성으로 관리**
- `GET  /api/v1/search-logs/popular?window=day|week` — **인기 Top-N** (사전집계, 관리자 전용)

### 응답 스키마(예)
```json
// suggest
{ "suggestions": [ { "text": "순두부 100g 영양", "reason": "co-occur" } ], "source": "stats" }

// popular
{ "items": [ { "text": "단백질 많은 간식", "score": 0.87, "window": "day" } ], "source": "stats" }

// recommended
{ "results": [ "다이어트용 고단백 음식은?", "두부 조리법 추천?" ] }
