# 📝 최근 PR 후속 조치 요약 (2025-10-12)

## 1. 헤더 · 사이드바 인터랙션 마무리
- 새 CSS 레이아웃에 맞춰 헤더 토글 요소를 재점검하고, `[data-sidebar-toggle]` 버튼을 추가해 모바일 사이드바를 열 수 있도록 해야 함.【F:static/js/main.js†L415-L520】【F:templates/includes/header.html†L1-L60】
- 사이드바 접힘/확장 상태는 `[data-sidebar-collapse]` 버튼이 담당하므로, DOM 구조와 ARIA 속성을 정리해 두 역할이 겹치지 않도록 QA 필요.【F:static/js/main.js†L471-L520】【F:templates/base.html†L1-L80】

## 2. CSS 경량화 검증
- Tailwind 빌드 파이프라인을 제거했으므로, 정적 자산은 `static/css/style.css`·`static/css/chat.css`만으로 유지되는지 배포 전 점검이 필요함.【F:templates/base.html†L1-L60】【F:static/css/style.css†L1-L200】
- 헤더·테마 드롭다운 등 기존 Tailwind 의존 UI가 새 CSS 클래스로 정상 동작하는지 라이트/다크 모드에서 교차 검증해야 함.【F:static/css/style.css†L300-L420】【F:templates/includes/header.html†L1-L60】

## 3. 테마 토큰 · 대비 QA
- 전역 토큰과 라이트/다크 재정의는 `static/css/style.css`에 정리돼 있으므로, 실제 화면 대비·포커스 상태를 QA 로그로 남겨야 함.【F:static/css/style.css†L1-L200】【F:docs/ui_style_gap_analysis.md†L50-L78】
- 테마 전환 JS는 라이트 모드 표시 색상을 하드코딩된 Hex(`#f59e0b`)로 사용 중이므로 토큰 기반으로 치환하거나 디자인 시스템 기준으로 정리 필요.【F:static/js/main.js†L203-L218】

## 4. QA 로그 · 배포 준비 체크
- 스타일 구조 변경 후 기능 QA, 접근성 테스트, 인프라 체크리스트 실행 기록을 `docs/logs/` 경로에 남기고 README 진행 현황을 업데이트해야 함.【F:docs/release_readiness_plan.md†L1-L80】
