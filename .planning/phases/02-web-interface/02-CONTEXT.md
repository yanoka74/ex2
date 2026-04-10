# Phase 2: Web Interface - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Flask 웹 앱으로 엑셀 파일(.xlsx) 업로드와 처리 결과 HTML 테이블 표시. 파일 업로드(버튼+드래그앤드롭), 에러 처리, 결과 테이블 렌더링, 처리 건수 요약을 포함한다.

</domain>

<decisions>
## Implementation Decisions

### 페이지 레이아웃
- **D-01:** 교체형 레이아웃 — 초기 화면에 업로드 영역만 표시, 업로드 후 결과 테이블로 화면 교체. 다시 업로드하려면 '새 파일 업로드' 버튼 클릭.
- **D-02:** 색상 포인트 있는 디자인 — 헤더나 버튼에 브랜드 색상 적용. 순수 미니멀이 아닌 시각적으로 구분되는 느낌.

### 드래그 앤 드롭 UX
- **D-03:** 콤팩트 업로드 버튼 — 안내 텍스트 + 파일 선택 버튼 구성. 드래그는 페이지 전체에서 받음 (별도 넓은 드롭존 없음).
- **D-04:** 버튼 로딩 피드백 — 파일 선택 후 버튼이 '처리 중...' 상태로 변경. 600건 수준이라 거의 즉시 완료될 것.

### 테이블 스타일
- **D-05:** 줄무늬 적용 — 짝수/홀수 행 배경색 교대로 행 구분 용이하게.
- **D-06:** 요약 정보는 테이블 위에 표시 — "전체 N건 → 중복 제거 후 M건, K개 고유코드" 형태.
- **D-07:** 숫자(주문수량 합계)는 천 단위 콤마 구분 (예: 1,234).
- **D-08:** 날짜(최근 주문일)는 YYYY-MM-DD 포맷.

### Claude's Discretion
- 에러 메시지 표시 위치 및 스타일 (사용자가 논의 대상에서 제외)
- 구체적인 색상 팔레트 선택
- CSS 프레임워크 사용 여부 (순수 CSS vs Bootstrap 등)
- Flask 앱 구조 (단일 파일 vs 모듈 분리)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

No external specs — requirements fully captured in decisions above and project files:
- `.planning/REQUIREMENTS.md` — UPLD-01~03, DISP-01, DISP-03 요구사항 정의
- `.planning/PROJECT.md` — 엑셀 컬럼 목록, 데이터 규모(600건), 제약조건
- `CLAUDE.md` — 기술 스택 (Flask 3.1.x, pandas 2.2.x, openpyxl, Jinja2)
- `.planning/phases/01-core-processing-pipeline/01-CONTEXT.md` — Phase 1 결정사항 (집계 키, 결과 컬럼)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/processor.py`: `process_sales_data(file_path)` → `(DataFrame, summary_dict)` — Phase 1에서 완성된 데이터 처리 모듈. Flask 라우트에서 직접 호출.
- `REQUIRED_COLUMNS`, `RESULT_COLUMNS` 상수 — 에러 메시지에서 참조 가능

### Established Patterns
- 모듈 구조: `src/` 디렉토리에 소스, `tests/` 디렉토리에 테스트
- pandas DataFrame 기반 데이터 처리
- 한국어 에러 메시지 (ValueError: "필수 컬럼이 누락되었습니다")

### Integration Points
- `process_sales_data(file_path)` 호출: 임시 파일 경로를 전달하면 결과 반환
- `summary_dict`: `{"total_rows": int, "skipped_rows": int, "result_rows": int}` — 요약 정보 표시에 직접 사용
- `result_df.to_html()` 또는 Jinja2 템플릿에서 DataFrame 렌더링

</code_context>

<specifics>
## Specific Ideas

- 결과 컬럼 순서: 마켓명, 판매자 고유코드, 상품명, 주문수량 합계, 최근 주문일 (Phase 1 D-03에서 확정)
- 고유코드 수(K개)는 summary에 없으므로 `len(result_df)`로 계산 필요
- 드래그 시 페이지 전체가 드롭 타겟이므로 dragover/drop 이벤트를 document 레벨에서 처리

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-web-interface*
*Context gathered: 2026-04-10*
