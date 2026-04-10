---
phase: 02-web-interface
plan: 01
subsystem: web-app
tags: [flask, jinja2, file-upload, drag-and-drop, tdd, pytest]

# Dependency graph
requires:
  - "process_sales_data() from Phase 1 (src/processor.py)"
provides:
  - "Flask web app: GET / upload view, POST /upload file processing"
  - "Jinja2 template: upload + results replacement layout"
  - "10 integration tests for Flask routes"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: [Flask file upload with tempfile cleanup, Jinja2 conditional rendering, vanilla JS drag-and-drop]

key-files:
  created: [src/app.py, templates/index.html, tests/test_app.py]
  modified: []

key-decisions:
  - "Single-file Flask app (src/app.py) with one template -- appropriate for 2-route application"
  - "Form auto-submit via JS change event instead of separate submit button"
  - "Full-page drag-and-drop target using document-level event listeners"

patterns-established:
  - "Flask test client fixture in test_app.py for integration testing"
  - "Jinja2 custom filter (comma) for number formatting"
  - "Replacement layout pattern: {% if results %} for view switching"

requirements-completed: [UPLD-01, UPLD-02, UPLD-03, DISP-01, DISP-03]

# Metrics
duration: 3min
completed: 2026-04-10
---

# Phase 2 Plan 1: Flask Web Interface Summary

**Flask/Jinja2 웹 앱으로 엑셀 업로드, 결과 테이블 표시, 드래그앤드롭, 로딩 피드백, 에러 처리를 구현 -- TDD로 10개 통합 테스트 선행 작성 후 구현**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-10T07:56:00Z
- **Completed:** 2026-04-10T07:58:34Z
- **Tasks:** 2
- **Files created:** 3

## Accomplishments
- Flask 앱(src/app.py)이 GET / 업로드 뷰와 POST /upload 처리 라우트 제공
- 파일 검증: 확장자 체크(.xlsx만), 빈 파일, 누락 컬럼(ValueError), 파일 크기 초과(413)
- process_sales_data() 통합: tempfile로 안전한 임시 파일 관리, finally에서 삭제
- Jinja2 comma 필터로 천 단위 콤마 포맷, strftime으로 날짜 YYYY-MM-DD 포맷
- 완전한 UI: 교체형 레이아웃, 줄무늬 테이블, 요약 통계, 드래그앤드롭, 로딩 피드백
- 10개 통합 테스트로 UPLD-01~03, DISP-01, DISP-03 요구사항 100% 커버

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Failing integration tests** - `9366816` (test)
2. **Task 1 GREEN: Flask app + minimal template** - `91d062f` (feat)
3. **Task 2: Complete Jinja2 template with full UI** - `45f0962` (feat)

## Files Created/Modified
- `src/app.py` - Flask 애플리케이션 (/ 및 /upload 라우트, comma 필터, 413 핸들러)
- `templates/index.html` - Jinja2 템플릿 (업로드 뷰, 결과 뷰, CSS, JS 드래그앤드롭)
- `tests/test_app.py` - 10개 통합 테스트 (인덱스, 업로드 검증, 결과 테이블, 요약, 콤마 포맷, 413)

## Decisions Made
- Single-file Flask app structure (no blueprints) -- 2-route app에 적합
- Form auto-submit via JS change event -- 별도 업로드 버튼 불필요
- Document-level drag-and-drop events -- 전체 페이지 드롭 타겟 (D-03)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required. Run with `flask --app src.app run --debug`.

## Self-Check: PASSED

- All 3 created files exist on disk (src/app.py, templates/index.html, tests/test_app.py)
- Commit 9366816 (RED) found in git log
- Commit 91d062f (GREEN) found in git log
- Commit 45f0962 (Task 2) found in git log
- 20 tests collected and passing (10 Phase 1 + 10 Phase 2)

---
*Phase: 02-web-interface*
*Completed: 2026-04-10*
