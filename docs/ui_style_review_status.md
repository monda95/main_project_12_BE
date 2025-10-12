# UI 스타일 문서 리뷰 요약 (2025-10-12)

## 진행 현황
- 배포 전 점검 로드맵에서 스타일 정밀 마감, 기능 QA, EC2 배포 준비까지 세부 작업 순서와 우선순위가 정의돼 있음. 각 단계는 한글 로그를 남기도록 규정돼 있어 진행 추적 체계가 마련됨.【F:docs/release_readiness_plan.md†L1-L44】
- 전역 테마 및 CSS 점검 문서는 토큰 치환, 컴포넌트별 상태, 세부 체크리스트와 실행 순서를 정리해 현재 전역 토큰 적용과 diff 정리가 완료됐음을 기록함.【F:docs/ui_style_gap_analysis.md†L1-L49】【F:docs/ui_style_gap_analysis.md†L50-L78】
- CSS 스냅샷 문서는 토큰 정의, 하드코딩 잔여 구간, 레이아웃 구조를 2025-10-12 기준으로 업데이트해 최신 상태를 확인할 수 있도록 함.【F:docs/ui_style_snapshot.md†L1-L38】【F:docs/ui_style_snapshot.md†L39-L66】
- 헤더/배너 마크업을 `templates/includes/header.html`로 분리해 `base.html`에서 include하도록 통합했으며, 공통 레이아웃 구조가 한 곳에서만 유지되도록 정리함.【F:templates/includes/header.html†L1-L59】【F:templates/base.html†L1-L210】
- 사용되지 않던 `static/css/style.fixed.css`를 제거해 헤더·버튼·입력 관련 토큰 선언을 `static/css/style.css` 하나로 집중시켰음.【F:static/css/style.css†L1-L120】
- Tailwind 의존은 CDN 대신 로컬/CI 빌드에서 처리하고, 생성된 정적 자산만 EC2(t2.micro)에 배치해 Nginx로 서빙하는 전략을 확정함. 런타임 빌드는 금지하도록 명문화했음.【F:docs/release_readiness_plan.md†L32-L44】

## 보완 필요 항목
- 스타일 작업은 전역 토큰 치환 이후 실제 화면 QA가 남아 있으므로 라이트/다크 모드 대비와 포커스 상태를 수동 검증해야 함.【F:docs/ui_style_gap_analysis.md†L50-L78】
- 테마 전환 및 인증 버튼 동작이 include 분리 후에도 정상인지 화면 QA 스크립트와 캡처 로그를 보강해야 함.【F:templates/includes/header.html†L1-L59】
- Tailwind 결과물은 로컬/CI 빌드 산출물만 배포하기로 했으므로, 파이프라인에 정적 빌드와 검증 단계를 추가하고 산출물 업로드 과정을 문서화해야 함.【F:docs/release_readiness_plan.md†L32-L44】
- 배포 준비 문서에서 제시한 기능 QA, 인프라 체크리스트, 접근성 테스트는 수행 기록이 없어 추후 실제 실행 및 로그 남김이 요구됨.【F:docs/release_readiness_plan.md†L14-L43】
