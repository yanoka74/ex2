# Roadmap: 판매정보 분석기

## Overview

Excel 판매 데이터를 업로드하면 판매자 고유코드별 판매수량을 집계하여 테이블로 보여주는 개인용 웹 도구. 데이터 처리 엔진을 먼저 구축하고(Phase 1), 웹 인터페이스를 씌운 뒤(Phase 2), 정렬/다운로드 등 사용성 기능을 추가한다(Phase 3).

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Core Processing Pipeline** - pandas 기반 데이터 처리 엔진 (중복 제거, 수량 합산, 컬럼 정규화)
- [ ] **Phase 2: Web Interface** - Flask 웹 앱으로 파일 업로드와 결과 테이블 표시
- [ ] **Phase 3: Usability Enhancements** - 테이블 정렬, 합계 행, 결과 다운로드

## Phase Details

### Phase 1: Core Processing Pipeline
**Goal**: 판매자 고유코드 기준으로 중복을 제거하고 판매수량을 정확히 합산하는 데이터 처리 모듈이 동작한다
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04
**Success Criteria** (what must be TRUE):
  1. .xlsx 파일을 읽어 판매자 고유코드 기준으로 중복 행이 제거된 결과를 반환한다
  2. 동일 고유코드의 주문수량이 산술적으로 합산된다 (문자열 연결이 아닌 숫자 덧셈)
  3. 각 고유코드에 해당하는 상품명이 결과에 포함된다
  4. 중복 상품의 경우 가장 최근 주문일이 결과에 포함된다
**Plans:** 1 plans

Plans:
- [x] 01-01-PLAN.md — TDD로 pandas 데이터 처리 모듈 구현 (process_sales_data 함수)

### Phase 2: Web Interface
**Goal**: 사용자가 웹 브라우저에서 엑셀 파일을 업로드하고 처리 결과를 테이블로 확인할 수 있다
**Depends on**: Phase 1
**Requirements**: UPLD-01, UPLD-02, UPLD-03, DISP-01, DISP-03
**Success Criteria** (what must be TRUE):
  1. 사용자가 파일 선택 버튼으로 .xlsx 파일을 업로드할 수 있다
  2. 사용자가 드래그 앤 드롭으로 파일을 업로드할 수 있다
  3. 잘못된 파일(확장자 오류, 빈 파일, 필수 컬럼 누락) 업로드 시 한국어 에러 메시지가 표시된다
  4. 처리 결과가 HTML 테이블로 웹 페이지에 표시된다
  5. 처리 건수 요약(전체 N건, 중복 제거 후 M건, K개 고유코드)이 표시된다
**Plans:** 2 plans
**UI hint**: yes

Plans:
- [ ] 02-01-PLAN.md — Flask 앱 백엔드 + Jinja2 템플릿 + 통합 테스트
- [ ] 02-02-PLAN.md — 브라우저에서 전체 UI/UX 수동 검증 (checkpoint)

### Phase 3: Usability Enhancements
**Goal**: 결과 테이블의 정렬, 합계 확인, 엑셀 다운로드로 일상 업무에서 편리하게 활용할 수 있다
**Depends on**: Phase 2
**Requirements**: DISP-02, DISP-04, DISP-05
**Success Criteria** (what must be TRUE):
  1. 컬럼 헤더를 클릭하면 해당 컬럼 기준으로 테이블이 정렬된다
  2. 테이블 하단에 전체 판매수량 합계 행이 표시된다
  3. 처리 결과를 .xlsx 파일로 다운로드할 수 있다
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 03-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Processing Pipeline | 0/1 | Not started | - |
| 2. Web Interface | 0/2 | Not started | - |
| 3. Usability Enhancements | 0/0 | Not started | - |
