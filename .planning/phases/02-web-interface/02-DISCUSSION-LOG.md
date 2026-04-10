# Phase 2: Web Interface - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-10
**Phase:** 02-web-interface
**Areas discussed:** 페이지 레이아웃, 드래그 앤 드롭 UX, 테이블 스타일

---

## 페이지 레이아웃

### 업로드/결과 배치

| Option | Description | Selected |
|--------|-------------|----------|
| 교체형 (추천) | 처음에 업로드 영역만 표시, 업로드 후 결과 테이블로 교체. '새 파일' 버튼으로 재업로드 | ✓ |
| 상하 고정형 | 업로드 영역이 항상 상단에 있고, 결과가 아래에 표시 | |
| Claude가 결정 | 업무용 도구에 적합한 레이아웃을 Claude가 판단 | |

**User's choice:** 교체형
**Notes:** 없음

### 디자인 톤

| Option | Description | Selected |
|--------|-------------|----------|
| 깨끗한 미니멀 (추천) | 흰 배경, 깔끔한 여백, 최소한 색상 | |
| 색상 포인트 있는 디자인 | 헤더나 버튼에 브랜드 색상 적용 | ✓ |
| Claude가 결정 | 업무용 도구에 적합한 스타일을 Claude가 판단 | |

**User's choice:** 색상 포인트 있는 디자인
**Notes:** 없음

---

## 드래그 앤 드롭 UX

### 드롭 영역 구성

| Option | Description | Selected |
|--------|-------------|----------|
| 넓은 드롭존 (추천) | 페이지 중앙에 넓은 점선 영역. 안내 텍스트 + 파일 선택 버튼 | |
| 콤팩트 업로드 버튼 | 작은 버튼 + 안내 텍스트. 드래그는 페이지 전체에서 받음 | ✓ |
| Claude가 결정 | 업무용 도구에 적합한 방식을 Claude가 판단 | |

**User's choice:** 콤팩트 업로드 버튼
**Notes:** 없음

### 처리 중 피드백

| Option | Description | Selected |
|--------|-------------|----------|
| 버튼 로딩 (추천) | 파일 선택 후 버튼이 '처리 중...' 상태로 변경 | ✓ |
| 전체 화면 로딩 | 페이지 전체에 스피너/프로그레스 바 표시 | |
| Claude가 결정 | 데이터 규모에 맞는 적절한 방식 선택 | |

**User's choice:** 버튼 로딩
**Notes:** 600건 수준이라 거의 즉시 완료될 것

---

## 테이블 스타일

### 줄무늬

| Option | Description | Selected |
|--------|-------------|----------|
| 줄무늬 적용 (추천) | 짝수/홀수 행 배경색 교대 | ✓ |
| 테두리만 | 깨끗한 구분선만 사용 | |
| Claude가 결정 | 데이터 밀도에 맞는 스타일 선택 | |

**User's choice:** 줄무늬 적용
**Notes:** 없음

### 요약 정보 위치

| Option | Description | Selected |
|--------|-------------|----------|
| 테이블 위 (추천) | 결과 테이블 바로 위에 요약 정보 표시 | ✓ |
| 테이블 아래 | 테이블 하단에 요약 표시 | |
| Claude가 결정 | 적절한 위치를 Claude가 판단 | |

**User's choice:** 테이블 위
**Notes:** 없음

### 숫자 포맷

| Option | Description | Selected |
|--------|-------------|----------|
| 콤마 구분 (추천) | 1,234 처럼 천 단위 콤마 구분 | ✓ |
| 그냥 숫자 | 1234 그대로 표시 | |
| Claude가 결정 | 데이터 규모에 맞게 판단 | |

**User's choice:** 콤마 구분
**Notes:** 없음

### 날짜 포맷

| Option | Description | Selected |
|--------|-------------|----------|
| YYYY-MM-DD (추천) | 2026-04-10 형식 | ✓ |
| YYYY년 MM월 DD일 | 한국어 날짜 표기 | |
| MM/DD | 간결하지만 연도 없음 | |

**User's choice:** YYYY-MM-DD
**Notes:** 없음

---

## Claude's Discretion

- 에러 메시지 표시 위치 및 스타일 (사용자가 논의 대상에서 제외)
- 구체적인 색상 팔레트 선택
- CSS 프레임워크 사용 여부
- Flask 앱 구조

## Deferred Ideas

None
