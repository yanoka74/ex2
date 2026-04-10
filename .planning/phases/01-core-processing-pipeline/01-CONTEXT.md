# Phase 1: Core Processing Pipeline - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

pandas 기반 데이터 처리 모듈: 엑셀(.xlsx) 파일을 읽어 판매자 고유코드 + 마켓명 조합으로 중복을 제거하고, 주문수량을 합산하여 결과를 반환한다.

</domain>

<decisions>
## Implementation Decisions

### 집계 기준
- **D-01:** 집계 키는 **판매자 고유코드 + 마켓명** 조합이다. 같은 고유코드라도 마켓이 다르면 별도 행으로 표시한다.
  - 원래 요구사항(고유코드 단독 기준)에서 사용자 요청으로 변경됨

### 상품명 처리
- **D-02:** 동일 집계 키(고유코드+마켓) 내 여러 상품명이 있을 때, **주문일 기준 가장 최근 상품명**을 표시한다.

### 결과 컬럼
- **D-03:** 최종 결과 테이블 컬럼: 마켓명, 판매자 고유코드, 상품명, 주문수량 합계, 최근 주문일

### 비정상 데이터 처리
- **D-04:** 주문수량이 빈 값이거나 숫자 변환 불가능한 행은 집계에서 제외하고 건너뛴 건수를 요약에 포함한다.
- **D-05:** 판매자 고유코드 또는 마켓명이 빈 행은 집계에서 제외하고 건너뛴 건수를 요약에 포함한다.

### 컬럼명 매칭
- **D-06:** 엑셀 컬럼명은 항상 동일하므로 정확한 이름으로 매칭한다. 유연한 매칭 불필요.
- **D-07:** 실제 컬럼명: 고객 주문 마켓별칭, 마켓명, 주문일, 주문번호, 판매자 고유코드, 상품코드, 상품명, 옵션명, 주문수량, 주문가격, 수령자, 전화번호, 주소

### Claude's Discretion
- 모듈 구조 (함수 분리, 파일 구성)
- pandas groupby/agg 세부 구현 방식
- 에러 처리 세부 구현 (건너뛴 행 추적 방식)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

No external specs — requirements fully captured in decisions above and project files:
- `.planning/REQUIREMENTS.md` — DATA-01~04 요구사항 정의
- `.planning/PROJECT.md` — 엑셀 컬럼 목록, 데이터 규모(600건), 제약조건
- `CLAUDE.md` — 기술 스택 (Flask, pandas 2.2.x, openpyxl)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- 기존 코드 없음 (첫 번째 페이즈)

### Established Patterns
- 패턴 없음 — 이 페이즈에서 기반 패턴 수립

### Integration Points
- Phase 2 (Web Interface)에서 이 모듈의 처리 함수를 호출할 예정
- 입력: 파일 경로 또는 파일 객체, 출력: DataFrame + 요약 정보 (전체 건수, 건너뛴 건수, 결과 건수)

</code_context>

<specifics>
## Specific Ideas

- 마켓명은 "마켓명" 컬럼 사용 ("고객 주문 마켓별칭" 아님)
- 주문일 기준 최신 판단 시 "주문일" 컬럼 사용
- 주문수량은 "주문수량" 컬럼 (PROJECT.md에서는 "고객 주문 수량"으로 언급되었으나 실제 컬럼명은 "주문수량")

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-core-processing-pipeline*
*Context gathered: 2026-04-10*
