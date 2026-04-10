# Requirements: 판매정보 분석기

**Defined:** 2026-04-10
**Core Value:** 엑셀 파일 업로드 한 번으로 판매자 고유코드별 판매수량을 즉시 확인할 수 있어야 한다.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### 파일 업로드

- [ ] **UPLD-01**: 사용자가 .xlsx 파일을 선택하여 업로드할 수 있다
- [ ] **UPLD-02**: 사용자가 드래그 앤 드롭으로 파일을 업로드할 수 있다
- [ ] **UPLD-03**: 잘못된 파일 업로드 시 명확한 에러 메시지를 볼 수 있다 (확장자, 빈 파일, 필수 컬럼 누락)

### 데이터 처리

- [ ] **DATA-01**: 판매자 고유코드 기준으로 중복 행이 제거된다
- [ ] **DATA-02**: 판매자 고유코드별 판매수량(고객 주문 수량)이 합산된다
- [ ] **DATA-03**: 각 고유코드에 해당하는 상품명이 함께 표시된다
- [ ] **DATA-04**: 중복 상품의 경우 마지막 판매일(고객 주문일 최신값)이 표시된다

### 결과 표시

- [ ] **DISP-01**: 결과가 HTML 테이블로 웹 페이지에 표시된다
- [ ] **DISP-02**: 컬럼 클릭으로 테이블을 정렬할 수 있다
- [ ] **DISP-03**: 처리 건수 요약이 표시된다 (전체 N건 → 중복 제거 후 M건, K개 고유코드)
- [ ] **DISP-04**: 테이블 하단에 전체 판매수량 합계 행이 표시된다
- [ ] **DISP-05**: 결과를 .xlsx 파일로 다운로드할 수 있다

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### 필터/검색

- **FILT-01**: 테이블 내 텍스트 검색 필터
- **FILT-02**: 마켓별 소계 표시

### 미리보기

- **PREV-01**: 업로드 전 파일 정보 미리보기 (파일명, 크기)
- **PREV-02**: 처리 전 원본 데이터 상위 N행 미리보기

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| 차트/그래프 시각화 | 사용자가 테이블만 원함. 필요 시 다운로드한 엑셀에서 생성 |
| 사용자 인증/로그인 | 개인 도구이므로 불필요 |
| 데이터베이스 저장 | 매번 업로드해서 확인하는 용도 |
| 다중 파일 형식 (CSV, ODS) | .xlsx만 사용하는 워크플로우 |
| 모바일 반응형 UI | 데스크톱 로컬 사용 |
| AI 기반 인사이트 | 단순 집계 도구에 과도한 복잡도 |
| 다중 시트 지원 | 첫 번째 시트 자동 사용 |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| UPLD-01 | - | Pending |
| UPLD-02 | - | Pending |
| UPLD-03 | - | Pending |
| DATA-01 | - | Pending |
| DATA-02 | - | Pending |
| DATA-03 | - | Pending |
| DATA-04 | - | Pending |
| DISP-01 | - | Pending |
| DISP-02 | - | Pending |
| DISP-03 | - | Pending |
| DISP-04 | - | Pending |
| DISP-05 | - | Pending |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 0
- Unmapped: 12 ⚠️

---
*Requirements defined: 2026-04-10*
*Last updated: 2026-04-10 after initial definition*
