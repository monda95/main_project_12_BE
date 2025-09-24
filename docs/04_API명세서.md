# 📘 API 명세서 (MVP 버전)

> EC2 **t2.micro** 제약 환경 + 1개월 개발 범위.  
> 전역 스로틀: 익명 20/min, 인증 60/min.

---

## 🔎 검색 (Search / Stats)
- `GET /api/v1/search?query=...` — Gemini 기반 음식/영양 검색  
  - 내부적으로 **InferenceService 위임**  
  - DB에는 `SearchLog`만 기록 (Food DB 확장은 미래 계획)

- `GET /api/v1/search-logs/autocomplete?prefix=...` — 자동완성  
- `GET /api/v1/queries/recent` — 최근 검색  
- `GET /api/v1/queries/recommended` — 추천 질문 (MV 기반)  
  - 현재: **management command 수동 갱신**  
  - 향후: Celery Beat 자동화 가능  
- `GET /api/v1/search-logs/popular?window=day|week` — 인기 검색어 (MV 기반, 관리자 전용)

---

## 🔐 인증 (Auth)
- `POST /api/v1/auth/signup` — 회원가입  
- `POST /api/v1/auth/login` — 로그인 (JWT)  
- `POST /api/v1/auth/refresh` — 토큰 재발급  
- `POST /api/v1/auth/logout` — 로그아웃  
- `POST /api/v1/auth/oauth2/exchange` — OAuth 교환 (GitHub 등)

---

## 💬 대화/메시지
- `POST   /api/v1/conversations` — 새 대화 생성 (비로그인 허용)  
- `GET    /api/v1/conversations/{id}` — 대화 조회  
- `PATCH  /api/v1/conversations/{id}` — 제목 수정  
- `DELETE /api/v1/conversations/{id}` — 대화 삭제 (메시지·추론 로그 CASCADE 삭제)  

- `POST   /api/v1/conversations/{id}/messages` — 메시지 생성 (항상 role=user)  
- `GET    /api/v1/conversations/{id}/messages` — 메시지 목록 조회  

---

## 🤖 AI 추론 (Inference + Self-Check)
- `POST /api/v1/inference`  
  - 요청:  
    ```json
    { "conversation_id": 123, "prompt": "..." }
    ```  
  - 처리: Gemini 호출 → **Self-Check** (형식/상충/출처) → 필요(실패) 시 1회 보정 → 저장  
  - 응답:  
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
      "self_check": { "check_pass": true, "retry_used": false, "violations": [] }
    }
    ```  
  - DB 반영:  
    - `messages` — AI 응답 저장  
    - `inference_runs` — latency, tokens, status + Self-Check 결과

---

## 📊 검색 로그 / 통계
- `POST /api/v1/search-logs` — `{ "query": "원문" }` → `normalized_query` 자동 생성  
- `GET  /api/v1/queries/suggest?prefix=...` — 자동완성  
- `GET  /api/v1/queries/recent` — 최근 질의 (user/guest 구분)  
- `GET  /api/v1/queries/recommended` — 추천 질문 (MV 기반, 수동 갱신)  
- `GET  /api/v1/search-logs/popular?window=day|week` — 인기 검색어 (MV 기반, 관리자 전용)

**응답 예시**
```json
// suggest
{ "suggestions": [ { "text": "순두부 100g 영양" } ] }

// popular
{ "items": [ { "text": "단백질 많은 간식", "score": 0.87 } ] }

// recommended
{ "results": [ "다이어트용 고단백 음식은?", "두부 조리법 추천?" ] }
