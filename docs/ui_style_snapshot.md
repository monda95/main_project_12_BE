# 🖼️ CSS 스냅샷 (2025-10-12)

## 0. 검증 현황 (2025-10-12 07:30 UTC)
- `static/css/style.css`의 전역 토큰 선언과 다크 모드 재정의 블록을 직접 확인해, 토큰 네이밍이 색상군 기준으로 유지되고 있음을 검증함. 포커스·outline 토큰 부재 역시 동일하게 남아 있음.【F:static/css/style.css†L1-L77】
- 헤더 인증 버튼, 사이드바 배경 등 하드코딩 색상이 그대로 존재하는지 확인했으며, Hex 값과 직접 지정된 배경/테두리가 남아 있어 토큰 치환 필요성이 유효함.【F:static/css/style.css†L200-L352】
- `.app-shell` 레이아웃과 사이드바 트랜지션 구조가 스냅샷 서술과 일치하는지 확인 완료. 여전히 사이드바는 기본적으로 숨겨진 상태에서 `transform`으로 동작하도록 구성돼 있음.【F:static/css/style.css†L310-L347】
- `templates/base.html` 중복 마크업이 아직 정리되지 않았고, Tailwind 유틸 클래스와 커스텀 클래스가 함께 존재해 스타일 충돌 가능성이 남아 있음을 재확인함.【F:templates/base.html†L1-L210】
- 부가 발견: `static/css/style.css`에 남은 diff 마커(`@@ ...`)가 실제 파일에도 존재하므로, CSS 정합성 확보를 위해 후속 정리가 필요함.【F:static/css/style.css†L284-L305】

## 1. 전역 토큰 정의 현황
- `:root`에서 컬러·섀도·배경 토큰이 기본/다크 테마에 맞춰 선언되어 있으나, 네이밍이 색상군 기반이라 컴포넌트 의미 맵핑이 부족함. 추후 `--btn-primary-*`, `--sidebar-*` 등 역할 중심 토큰 확장이 필요함.【F:static/css/style.css†L1-L62】
- 다크 테마 전환 시 `body[data-theme='dark']` 블록에서 토큰을 재정의하고 있어 구조는 적절하나, 포커스·outline 계열 토큰이 분리돼 있지 않아 공통 포커스 스타일 관리가 어려움.【F:static/css/style.css†L41-L75】

## 2. 하드코딩 잔여 구간
- 헤더 인증 버튼(`.header-auth-btn--login`)과 호버 상태가 여전히 Hex 값으로 지정돼 토큰 일관성이 깨져 있음.【F:static/css/style.css†L194-L233】
- 사이드바와 레이아웃 계열(`.app-sidebar`, `.app-sidebar-logo`)에서도 배경/테두리 색상이 토큰 대신 직접 지정돼 있어 라이트·다크 전환 시 보정이 어려움.【F:static/css/style.css†L310-L379】
- 채팅 버블, 어시스턴트 카드 전반이 하드코딩된 색상·그라데이션을 사용하고 있어 전역 토큰 치환 필요성이 여전히 존재함.【F:static/css/chat.css†L1-L132】【F:static/css/chat.css†L133-L210】

## 3. 레이아웃 구조 스냅샷
- `.app-shell` 기준으로 고정 헤더 + 사이드바 + 콘텐츠 3단 구성이며, 사이드바는 슬라이드 인/아웃을 위한 `transform` 전환이 남아 있다.【F:static/css/style.css†L310-L347】
- `templates/base.html` 내부에 헤더·메뉴 마크업이 중복 렌더링 돼 있어 CSS가 동일 구조를 두 번 타겟팅하는 상황이므로, 마크업 정리가 선행돼야 스타일 적용이 안정된다.【F:templates/base.html†L1-L120】【F:templates/base.html†L121-L210】

## 4. TODO 싱크
- 위 스냅샷에서 확인된 하드코딩/중복 문제는 `docs/ui_style_gap_analysis.md`의 1~3번 항목과 그대로 일치하므로, 먼저 토큰 치환과 마크업 정리를 끝낸 뒤 QA 로그를 적재하는 순서를 유지한다.【F:docs/ui_style_gap_analysis.md†L1-L45】
- 새로 추가된 사이드바/레이아웃 클래스는 요구사항 QA 전에 라이트·다크 모드 스냅샷을 각각 확보해 대비/그림자 값을 점검한다.【F:static/css/style.css†L330-L379】

