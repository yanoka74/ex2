# Feature Landscape

**Domain:** 판매정보 엑셀 분석 웹앱 (Sales Data Excel Analysis Web App)
**Researched:** 2026-04-10
**Scope:** Personal-use tool, ~600 rows, local deployment

## Table Stakes

Features users expect. Missing = tool feels broken or unusable.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| 엑셀 파일(.xlsx) 업로드 | 도구의 유일한 입력 방식. 없으면 아무것도 안 됨 | Low | HTML file input + openpyxl/pandas read_excel |
| 드래그 앤 드롭 업로드 | 파일 선택 대화상자만 있으면 2010년대 느낌. 드래그 앤 드롭은 현대 웹앱의 기본 | Low | JS 이벤트 핸들링, 클릭 업로드도 병행 제공 |
| 업로드 파일 유효성 검사 | .xlsx가 아닌 파일, 빈 파일, 필수 컬럼 누락 시 명확한 에러 메시지 필요 | Low | 확장자 체크 + 컬럼 존재 여부 확인 |
| 판매자 고유코드 기준 중복 제거 | 핵심 비즈니스 로직. 이게 없으면 도구 존재 이유 없음 | Low | pandas drop_duplicates 또는 groupby |
| 고유코드별 판매수량 합계 | 핵심 비즈니스 로직. 사용자가 원하는 최종 결과값 | Low | pandas groupby + sum |
| 결과 테이블 웹 표시 | 결과를 볼 수 없으면 의미 없음 | Low | HTML table 렌더링 |
| 상품명 등 참고 정보 표시 | 고유코드만으로는 어떤 상품인지 모름. 상품명이 같이 보여야 유용 | Low | groupby 시 first() 또는 리스트로 상품명 병합 |
| 처리 중 로딩 인디케이터 | 업로드 후 화면이 멈추면 사용자가 오류로 판단. 600건이라 빠르겠지만 피드백은 필수 | Low | 간단한 spinner 또는 progress bar |
| 에러 상태 표시 | 파일 형식 오류, 컬럼 누락 등 문제 시 무엇이 잘못됐는지 알려줘야 함 | Low | Flash message 또는 alert UI |

## Differentiators

개인 도구이므로 "경쟁 우위"보다는 "업무 효율을 크게 높이는 추가 기능"으로 해석.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| 결과 엑셀 다운로드 | 분석 결과를 다시 엑셀로 받아 다른 용도로 활용 가능. 웹 테이블만 보는 것보다 훨씬 실용적 | Low | pandas to_excel + Flask send_file |
| 테이블 정렬 (컬럼 클릭) | 판매수량 높은 순, 상품명 가나다순 등으로 빠르게 재정렬. 데이터 파악 속도 향상 | Low | JS 클라이언트 사이드 정렬 또는 DataTables 라이브러리 |
| 테이블 검색/필터 | 특정 상품 코드나 상품명을 빠르게 찾기. 결과 행이 많을 때 유용 | Low | 클라이언트 사이드 text filter |
| 업로드 전 파일 미리보기 | 업로드 전 파일명, 크기, 시트 정보 확인. 잘못된 파일 업로드 방지 | Low | JS FileReader API로 기본 정보 표시 |
| 원본 데이터 미리보기 | 처리 전 원본 데이터 상위 N행을 보여줌. 컬럼 매핑이 맞는지 확인 가능 | Medium | 별도 엔드포인트 또는 2단계 프로세스 필요 |
| 합계 행 (총 판매수량) | 테이블 하단에 전체 합계 표시. 전체 규모 파악에 유용 | Low | 단순 sum 계산 + 테이블 footer |
| 마켓별 소계 | 마켓명 기준 그룹핑하여 마켓별 판매 현황 파악 | Medium | 추가 groupby 로직 + UI 탭 또는 섹션 |
| 처리 건수 요약 | "총 600건 중 중복 제거 후 150건, 45개 고유코드" 같은 요약 정보 | Low | 간단한 count 계산 |

## Anti-Features

의도적으로 만들지 않을 기능. PROJECT.md의 Out of Scope와 일치 + 추가 판단.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| 차트/그래프 시각화 | v1 범위 밖. 사용자가 명시적으로 테이블만 원함. 차트 추가 시 복잡도 급증 (Chart.js 등 추가 의존성) | 테이블로 충분. 필요 시 다운로드한 엑셀에서 차트 생성 |
| 사용자 인증/로그인 | 개인 도구. 인증 시스템은 불필요한 복잡도 | 로컬 실행으로 충분한 보안 확보 |
| 데이터베이스 저장 | 매번 업로드하여 확인하는 용도. DB 추가 시 마이그레이션, 백업 등 운영 부담 발생 | 메모리에서 처리 후 결과만 표시/다운로드 |
| 다중 파일 형식 지원 (CSV, ODS 등) | xlsx만 사용하는 워크플로우. 다른 형식 지원은 파싱 로직 분기 + 테스트 부담 | .xlsx 전용으로 단순하게 유지 |
| 실시간 협업/공유 | 개인 도구에 불필요. WebSocket 등 인프라 복잡도 폭증 | 결과 엑셀 다운로드로 공유 대체 |
| AI 기반 인사이트 | 트렌디하지만 이 도구의 목적은 단순 집계. LLM API 비용 + 복잡도 대비 가치 없음 | 사용자가 테이블 보고 직접 판단 |
| 다중 시트 지원 | 단일 시트에 데이터가 있는 표준 워크플로우. 시트 선택 UI 추가 시 복잡도 증가 | 첫 번째 시트(또는 활성 시트) 자동 사용. 에러 시 안내 메시지 |
| 반응형 모바일 UI | 로컬 개발 서버에서 데스크톱으로 사용. 모바일 대응은 불필요한 CSS 작업 | 데스크톱 화면 기준 레이아웃 |

## Feature Dependencies

```
파일 업로드 → 유효성 검사 → 중복 제거 → 판매수량 합계 → 테이블 표시
                                                          ↓
                                                     결과 엑셀 다운로드

파일 업로드 → 업로드 전 파일 미리보기 (독립)
테이블 표시 → 테이블 정렬 (테이블 렌더링 후 가능)
테이블 표시 → 테이블 검색/필터 (테이블 렌더링 후 가능)
판매수량 합계 → 합계 행 (합계 계산 로직 확장)
판매수량 합계 → 마켓별 소계 (groupby 키 변경)
중복 제거 → 처리 건수 요약 (전후 count 비교)
```

## MVP Recommendation

프로젝트 특성(개인 도구, 600건, 로컬 실행)을 고려한 우선순위.

**Phase 1 - 핵심 기능 (Must Ship):**
1. 엑셀 파일 업로드 (드래그 앤 드롭 포함)
2. 파일 유효성 검사 + 에러 표시
3. 판매자 고유코드 기준 중복 제거
4. 고유코드별 판매수량 합계
5. 상품명 포함 결과 테이블 표시
6. 처리 건수 요약 (간단한 추가)

**Phase 2 - 실용성 강화 (Nice to Have):**
7. 결과 엑셀 다운로드 -- 가장 실용적인 차별화 기능
8. 테이블 정렬 (컬럼 클릭)
9. 합계 행

**Defer:**
- 마켓별 소계: 핵심 사용 사례와 거리 있음. 필요성 확인 후 추가
- 원본 데이터 미리보기: 데이터가 정형화되어 있으면 불필요
- 테이블 검색/필터: 150건 이하 결과에서는 스크롤로 충분

## Sources

- [Uploadcare - File Uploader UX Best Practices](https://uploadcare.com/blog/file-uploader-ux-best-practices/)
- [Eleken - File Upload UI Tips](https://www.eleken.co/blog-posts/file-upload-ui)
- [Filestack - Building Modern Drag-and-Drop Upload UI](https://blog.filestack.com/building-modern-drag-and-drop-upload-ui/)
- [Microsoft Support - Analyze Data in Excel](https://support.microsoft.com/en-us/office/analyze-data-in-excel-3223aab8-f543-4fda-85ed-76bb0295ffc4)
- [Cigro - 쇼핑몰 채널별 매출/비용 관리 엑셀 자동화](https://www.cigro.io/post/%EC%87%BC%ED%95%91%EB%AA%B0-%EC%B1%84%EB%84%90%EB%B3%84-%EB%A7%A4%EC%B6%9C-%EB%B9%84%EC%9A%A9-%EA%B4%80%EB%A6%AC-%EA%B3%B5%ED%97%8C%EC%9D%B4%EC%9D%B5-%EC%97%91%EC%85%80-%EC%9E%90%EB%8F%99%ED%99%94-%EC%8B%9C%ED%8A%B8-%EA%B3%B5%EC%9C%A0-%EB%AC%B4%EB%A3%8C-%EC%97%91%EC%85%80-%ED%85%9C%ED%94%8C%EB%A6%BF)
