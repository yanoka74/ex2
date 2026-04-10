# Phase 1: Core Processing Pipeline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-10
**Phase:** 01-core-processing-pipeline
**Areas discussed:** 상품명 처리 방식, 결과 테이블 컬럼, 비정상 데이터 처리, 컬럼명 매칭

---

## 상품명 처리 방식

| Option | Description | Selected |
|--------|-------------|----------|
| 콤마로 모두 표시 | 예: "사과, 배, 포도" — 어떤 상품이 묶였는지 한눈에 확인 | |
| 첫 번째 상품명만 | 대표 상품명 하나만 표시 — 간결하지만 정보 손실 | |
| 가장 많은 수량의 상품명 | 해당 고유코드에서 가장 많이 팔린 상품명을 대표로 표시 | |
| 가장 마지막에 팔린 상품명 | 주문일 기준 가장 최근 상품명 | ✓ |

**User's choice:** 가장 마지막에 팔린 상품에 상품명 (Other — 직접 입력)
**Notes:** 주문일 기준 가장 최근 상품명으로 확인됨

---

## 결과 테이블 컬럼

| Option | Description | Selected |
|--------|-------------|----------|
| 상품코드 | 상품코드 컬럼도 함께 표시 | |
| 마켓명 | 어느 마켓에서 팔렸는지 표시 | ✓ |
| 옵션명 | 상품 옵션 정보 표시 | |
| 추가 없음 | 고유코드 + 상품명 + 수량 + 최근주문일만으로 충분 | |

**User's choice:** 마켓명
**Notes:** 마켓별 별도 행으로 표시 → 집계 기준이 고유코드+마켓명 조합으로 변경됨

### 마켓 표시 방식 (추가 논의)

| Option | Description | Selected |
|--------|-------------|----------|
| 한 행, 마켓 목록 | 고유코드로 합산하고 마켓명은 콤마로 모아서 표시 | |
| 마켓별 별도 행 | 같은 고유코드라도 마켓이 다르면 별도 행으로 표시, 각 행 수량 합산 | ✓ |
| 마켓별 탭/필터 | 기본은 전체 합산이고, 마켓별로 필터링할 수 있는 기능 | |

**User's choice:** 마켓별 별도 행
**Notes:** 여러 차례 확인 후 최종 확정. 집계 키 = 판매자 고유코드 + 마켓명 조합.

---

## 비정상 데이터 처리

| Option | Description | Selected |
|--------|-------------|----------|
| 해당 행 건너뛰기 | 수량 변환 불가능한 행은 집계에서 제외하고, 건너뛴 건수를 요약에 표시 | ✓ |
| 0으로 처리 | 빈 값이나 변환 불가 수량을 0으로 간주하고 집계에 포함 | |
| 에러 표시 | 비정상 데이터 발견 시 에러 메시지로 알려주고 집계 중단 | |

**User's choice:** 해당 행 건너뛰기 (추천)
**Notes:** 고유코드나 마켓명이 빈 행도 동일하게 건너뛰기로 결정

---

## 컬럼명 매칭

| Option | Description | Selected |
|--------|-------------|----------|
| 항상 동일 | 컬럼명이 항상 고정되어 있으므로 정확한 이름으로 매칭하면 됨 | ✓ |
| 약간 다를 수 있음 | 공백이나 대소문자 차이가 있을 수 있어서 유연한 매칭 필요 | |
| 모르겠음 | 확인이 필요하니 유연하게 처리해 주세요 | |

**User's choice:** 항상 동일 (추천)
**Notes:** 실제 컬럼명 확인 완료: 고객 주문 마켓별칭, 마켓명, 주문일, 주문번호, 판매자 고유코드, 상품코드, 상품명, 옵션명, 주문수량, 주문가격, 수령자, 전화번호, 주소

## Claude's Discretion

- 모듈 구조 (함수 분리, 파일 구성)
- pandas groupby/agg 세부 구현 방식
- 에러 처리 세부 구현

## Deferred Ideas

None — discussion stayed within phase scope
