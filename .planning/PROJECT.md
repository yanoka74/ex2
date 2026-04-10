# 판매정보 분석기

## What This Is

판매정보 엑셀 파일(.xlsx)을 업로드하면 판매자 고유코드 기준으로 중복을 제거하고, 코드별 판매수량 합계를 테이블로 보여주는 파이썬 웹 애플리케이션. 개인 업무용 도구.

## Core Value

엑셀 파일 업로드 한 번으로 판매자 고유코드별 판매수량을 즉시 확인할 수 있어야 한다.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] 엑셀 파일(.xlsx) 업로드 기능
- [ ] 판매자 고유코드 기준 중복 행 제거
- [ ] 판매자 고유코드별 판매수량(고객 주문 수량) 합계 계산
- [ ] 결과를 테이블 형태로 웹 페이지에 표시
- [ ] 상품명 등 참고 정보 함께 표시

### Out of Scope

- 차트/그래프 시각화 — v1은 테이블만
- 사용자 인증/로그인 — 개인 도구이므로 불필요
- 데이터베이스 저장 — 매번 업로드해서 확인하는 용도
- 엑셀 외 다른 파일 형식 지원 — xlsx만 지원

## Context

- 엑셀 파일 컬럼: 고객 주문 마켓별칭, 마켓명, 주문일, 주문번호, 판매자 고유코드, 상품코드, 상품명, 옵션명, 주문수량, 주문가격, 수령자, 전화번호, 주소
- 데이터 규모: 약 600건 수준
- 중복 기준: 판매자 고유코드 컬럼 값이 동일한 행
- 판매수량: 고객 주문 수량 컬럼 합산
- 파이썬으로 구현 (Flask 또는 FastAPI)

## Constraints

- **Tech stack**: Python — 사용자 요청
- **File format**: .xlsx만 지원
- **Deployment**: 로컬 실행 (개발 서버)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 판매자 고유코드로 중복 판별 | 사용자 확인 완료 | — Pending |
| 테이블만 표시 (차트 없음) | 사용자 선택 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-10 after initialization*
