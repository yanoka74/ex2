"""판매 데이터 처리 모듈 단위 테스트.

테스트 대상: src.processor.process_sales_data
요구사항: DATA-01~DATA-04, 결정사항: D-01~D-07
"""
import pytest
import pandas as pd

from src.processor import process_sales_data


class TestDeduplication:
    """DATA-01, D-01: 판매자 고유코드 + 마켓명 기준 중복 제거."""

    def test_same_code_same_market_merged(self, xlsx_factory):
        """동일 고유코드+마켓명 행이 하나로 합쳐진다."""
        rows = [
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "제품A",
             "주문수량": 1, "주문일": "2026-01-01"},
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "제품A",
             "주문수량": 2, "주문일": "2026-01-02"},
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "제품A",
             "주문수량": 3, "주문일": "2026-01-03"},
        ]
        path = xlsx_factory(rows)
        result_df, summary = process_sales_data(path)

        assert len(result_df) == 1

    def test_same_code_different_market_separate(self, xlsx_factory):
        """같은 고유코드라도 마켓이 다르면 별도 행이다."""
        rows = [
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "제품A",
             "주문수량": 1, "주문일": "2026-01-01"},
            {"판매자 고유코드": "ABC001", "마켓명": "쿠팡", "상품명": "제품A",
             "주문수량": 1, "주문일": "2026-01-01"},
        ]
        path = xlsx_factory(rows)
        result_df, summary = process_sales_data(path)

        assert len(result_df) == 2


class TestQuantitySum:
    """DATA-02: 주문수량이 숫자로 합산된다."""

    def test_quantity_summed(self, xlsx_factory):
        """동일 집계 키의 주문수량이 합산된다."""
        rows = [
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "제품A",
             "주문수량": 3, "주문일": "2026-01-01"},
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "제품A",
             "주문수량": 5, "주문일": "2026-01-02"},
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "제품A",
             "주문수량": 2, "주문일": "2026-01-03"},
        ]
        path = xlsx_factory(rows)
        result_df, summary = process_sales_data(path)

        assert result_df.iloc[0]["주문수량 합계"] == 10


class TestLatestProductName:
    """DATA-03, D-02: 최근 주문일 기준 상품명이 선택된다."""

    def test_latest_order_date_product_name(self, xlsx_factory):
        """최근 주문일 기준 상품명이 결과에 표시된다."""
        rows = [
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "A제품",
             "주문수량": 1, "주문일": "2026-01-01"},
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "B제품",
             "주문수량": 1, "주문일": "2026-03-15"},
        ]
        path = xlsx_factory(rows)
        result_df, summary = process_sales_data(path)

        assert result_df.iloc[0]["상품명"] == "B제품"


class TestLatestOrderDate:
    """DATA-04: 최근 주문일이 결과에 포함된다."""

    def test_latest_order_date_included(self, xlsx_factory):
        """최근 주문일이 결과에 포함된다."""
        rows = [
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "A제품",
             "주문수량": 1, "주문일": "2026-01-01"},
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "B제품",
             "주문수량": 1, "주문일": "2026-03-15"},
        ]
        path = xlsx_factory(rows)
        result_df, summary = process_sales_data(path)

        assert pd.Timestamp("2026-03-15") == result_df.iloc[0]["최근 주문일"]


class TestResultColumns:
    """D-03: 결과 컬럼이 정확히 지정된 순서로 존재한다."""

    def test_result_columns_exact(self, xlsx_factory):
        """결과 DataFrame의 컬럼이 정확히 [마켓명, 판매자 고유코드, 상품명, 주문수량 합계, 최근 주문일]이다."""
        rows = [
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "제품A",
             "주문수량": 1, "주문일": "2026-01-01"},
        ]
        path = xlsx_factory(rows)
        result_df, summary = process_sales_data(path)

        expected_columns = ["마켓명", "판매자 고유코드", "상품명", "주문수량 합계", "최근 주문일"]
        assert list(result_df.columns) == expected_columns


class TestSkipInvalidQuantity:
    """D-04: 주문수량이 빈 값이거나 숫자 변환 불가인 행은 제외된다."""

    def test_empty_quantity_skipped(self, xlsx_factory):
        """주문수량이 빈 값인 행은 제외되고 skipped_rows에 카운트된다."""
        rows = [
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "제품A",
             "주문수량": 5, "주문일": "2026-01-01"},
            {"판매자 고유코드": "ABC002", "마켓명": "쿠팡", "상품명": "제품B",
             "주문수량": "", "주문일": "2026-01-02"},
            {"판매자 고유코드": "ABC003", "마켓명": "11번가", "상품명": "제품C",
             "주문수량": "abc", "주문일": "2026-01-03"},
        ]
        path = xlsx_factory(rows)
        result_df, summary = process_sales_data(path)

        assert len(result_df) == 1
        assert summary["skipped_rows"] == 2


class TestSkipMissingKeys:
    """D-05: 판매자 고유코드 또는 마켓명이 빈 행은 제외된다."""

    def test_missing_keys_skipped(self, xlsx_factory):
        """판매자 고유코드 또는 마켓명이 빈 행은 제외되고 skipped_rows에 카운트된다."""
        rows = [
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "제품A",
             "주문수량": 5, "주문일": "2026-01-01"},
            {"판매자 고유코드": "", "마켓명": "쿠팡", "상품명": "제품B",
             "주문수량": 3, "주문일": "2026-01-02"},
            {"판매자 고유코드": "ABC003", "마켓명": "", "상품명": "제품C",
             "주문수량": 2, "주문일": "2026-01-03"},
        ]
        path = xlsx_factory(rows)
        result_df, summary = process_sales_data(path)

        assert len(result_df) == 1
        assert summary["skipped_rows"] == 2


class TestReturnType:
    """반환값이 (DataFrame, summary_dict) 튜플이다."""

    def test_return_tuple(self, xlsx_factory):
        """반환값이 (DataFrame, dict) 튜플이며 summary_dict 키가 올바르다."""
        rows = [
            {"판매자 고유코드": "ABC001", "마켓명": "스마트스토어", "상품명": "제품A",
             "주문수량": 1, "주문일": "2026-01-01"},
        ]
        path = xlsx_factory(rows)
        result = process_sales_data(path)

        assert isinstance(result, tuple)
        assert len(result) == 2

        result_df, summary = result
        assert isinstance(result_df, pd.DataFrame)
        assert isinstance(summary, dict)
        assert "total_rows" in summary
        assert "skipped_rows" in summary
        assert "result_rows" in summary


class TestMissingColumns:
    """D-06, D-07: 필수 컬럼이 누락되면 ValueError를 발생시킨다."""

    def test_missing_required_column_raises_error(self, xlsx_custom_columns_factory):
        """필수 컬럼이 누락되면 ValueError가 발생한다."""
        # "주문수량" 컬럼 누락
        columns = ["마켓명", "판매자 고유코드", "상품명", "주문일"]
        rows_data = [["스마트스토어", "ABC001", "제품A", "2026-01-01"]]
        path = xlsx_custom_columns_factory(columns, rows_data)

        with pytest.raises(ValueError, match="필수 컬럼이 누락되었습니다"):
            process_sales_data(path)
