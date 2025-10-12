# 🖼️ CSS 스냅샷 (2025-10-12)

## 0. 검증 현황 (2025-10-12 11:10 UTC)
- `static/css/style.css`의 전역 토큰 선언과 다크 모드 재정의 블록을 재확인했으며, 포커스 링·중립 버튼·사이드바/채팅용 변수 등이 추가 정의된 것을 확인함.【F:static/css/style.css†L1-L120】
- 헤더 인증 버튼, 사이드바 배경, 채팅 버블·어시스턴트 카드가 전역 토큰 기반으로 갱신돼 라이트/다크 모드 간 색상 동기화 상태를 확보했음.【F:static/css/style.css†L140-L408】【F:static/css/chat.css†L1-L188】
- `.app-shell` 레이아웃과 사이드바 트랜지션 구조는 기존 서술과 동일하게 유지됨.【F:static/css/style.css†L310-L347】
- `templates/base.html` 중복 마크업 문제는 여전히 존재하므로 후속 구조 정리가 필요함.【F:templates/base.html†L1-L210】
- 부가 확인: 이전에 남아 있던 diff 마커는 모두 제거돼 CSS 파싱 위험 요소가 해소됨.【F:static/css/style.css†L1-L120】

## 1. 전역 토큰 정의 현황
- `:root`에서 컬러·섀도·배경 토큰이 기본/다크 테마에 맞춰 선언되어 있으며, 이번 업데이트로 버튼 중립 상태와 사이드바/채팅/어시스턴트 카드 전용 토큰이 추가됨.【F:static/css/style.css†L1-L120】
- 다크 테마 전환 시 `body[data-theme='dark']` 블록에서 동일한 토큰을 재정의하고 있어 구조가 유지되며, 포커스 링 변수도 함께 재정의됨.【F:static/css/style.css†L41-L120】

## 2. 하드코딩 잔여 구간
- 헤더 인증 버튼(`.header-auth-btn--login`)과 포커스 상태가 토큰 기반으로 치환됐으며, 남은 하드코딩은 QA 대상 아님으로 정리됨.【F:static/css/style.css†L174-L236】
- 사이드바와 대화 목록(`.app-sidebar`, `.conversation-item`)은 배경/테두리/호버 상태가 토큰화됐고, 실제 페이지 Tailwind 충돌 여부는 QA 필요.【F:static/css/style.css†L260-L408】
- 채팅 버블, 어시스턴트 카드 역시 전역 토큰을 사용하도록 교체됨. 추가적인 명칭 정리 및 도트/그림자 강도 튜닝은 후속 작업으로 분리 예정.【F:static/css/chat.css†L1-L188】

## 3. 레이아웃 구조 스냅샷
- `.app-shell` 기준으로 고정 헤더 + 사이드바 + 콘텐츠 3단 구성이며, 사이드바는 슬라이드 인/아웃을 위한 `transform` 전환이 남아 있다.【F:static/css/style.css†L310-L347】
- `templates/base.html` 내부에 헤더·메뉴 마크업이 중복 렌더링 돼 있어 CSS가 동일 구조를 두 번 타겟팅하는 상황이므로, 마크업 정리가 선행돼야 스타일 적용이 안정된다.【F:templates/base.html†L1-L120】【F:templates/base.html†L121-L210】

## 4. TODO 싱크
- 위 스냅샷에서 확인된 하드코딩/중복 문제는 `docs/ui_style_gap_analysis.md`의 1~3번 항목과 그대로 일치하므로, 먼저 토큰 치환과 마크업 정리를 끝낸 뒤 QA 로그를 적재하는 순서를 유지한다.【F:docs/ui_style_gap_analysis.md†L1-L45】
- 새로 추가된 사이드바/레이아웃 클래스는 요구사항 QA 전에 라이트·다크 모드 스냅샷을 각각 확보해 대비/그림자 값을 점검한다.【F:static/css/style.css†L330-L379】

