"""Flask 웹 앱 통합 테스트.

테스트 대상: src.app (Flask routes)
요구사항: UPLD-01~03, DISP-01, DISP-03
"""
import io
import re

import pytest

from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_index_page(client):
    """GET / returns 200 with upload UI."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "업로드" in html or "파일 선택" in html
    assert "판매정보 분석기" in html


def test_upload_no_file(client):
    """POST /upload with no file returns error message."""
    response = client.post("/upload", content_type="multipart/form-data")
    html = response.data.decode("utf-8")
    assert "파일을 선택해주세요" in html


def test_upload_empty_filename(client):
    """POST /upload with empty filename returns error message."""
    data = {"file": (io.BytesIO(b""), "")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    html = response.data.decode("utf-8")
    assert "파일을 선택해주세요" in html


def test_upload_wrong_extension(client):
    """POST /upload with .csv file returns extension error."""
    data = {"file": (io.BytesIO(b"test data"), "test.csv")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    html = response.data.decode("utf-8")
    assert ".xlsx 파일만 업로드할 수 있습니다" in html


def test_upload_valid_xlsx(client, xlsx_factory):
    """POST /upload with valid xlsx returns 200 with result data."""
    path = xlsx_factory([
        {"마켓명": "A마켓", "판매자 고유코드": "CODE1",
         "상품명": "상품A", "주문수량": 10, "주문일": "2024-01-01"},
    ])
    with open(path, "rb") as f:
        data = {"file": (f, "test.xlsx")}
        response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "CODE1" in html


def test_upload_missing_columns(client, xlsx_custom_columns_factory):
    """POST /upload with xlsx missing required columns returns error."""
    path = xlsx_custom_columns_factory(
        columns=["Wrong1", "Wrong2"],
        rows=[["val1", "val2"]],
    )
    with open(path, "rb") as f:
        data = {"file": (f, "test.xlsx")}
        response = client.post("/upload", data=data, content_type="multipart/form-data")
    html = response.data.decode("utf-8")
    assert "필수 컬럼이 누락되었습니다" in html


def test_results_table(client, xlsx_factory):
    """Valid upload response contains HTML table with correct column headers."""
    path = xlsx_factory([
        {"마켓명": "A마켓", "판매자 고유코드": "CODE1",
         "상품명": "상품A", "주문수량": 5, "주문일": "2024-01-15"},
    ])
    with open(path, "rb") as f:
        data = {"file": (f, "test.xlsx")}
        response = client.post("/upload", data=data, content_type="multipart/form-data")
    html = response.data.decode("utf-8")
    assert "<table" in html
    assert "마켓명" in html
    assert "판매자 고유코드" in html
    assert "상품명" in html
    assert "주문건수" in html
    assert "주문수량 합계" in html
    assert "최근 주문일" in html


def test_summary_display(client, xlsx_factory):
    """Valid upload response contains summary text."""
    path = xlsx_factory([
        {"마켓명": "A마켓", "판매자 고유코드": "CODE1",
         "상품명": "상품A", "주문수량": 5, "주문일": "2024-01-15"},
        {"마켓명": "A마켓", "판매자 고유코드": "CODE1",
         "상품명": "상품A", "주문수량": 3, "주문일": "2024-01-16"},
        {"마켓명": "B마켓", "판매자 고유코드": "CODE2",
         "상품명": "상품B", "주문수량": 2, "주문일": "2024-02-01"},
    ])
    with open(path, "rb") as f:
        data = {"file": (f, "test.xlsx")}
        response = client.post("/upload", data=data, content_type="multipart/form-data")
    html = response.data.decode("utf-8")
    # Should match pattern: 전체 N건 ... 중복 제거 후 M건 ... K개 고유코드
    assert re.search(r"전체\s+\d+건", html)
    assert re.search(r"중복 제거 후\s+\d+건", html)
    assert re.search(r"\d+개 고유코드", html)


def test_comma_filter(client, xlsx_factory):
    """Numbers are formatted with comma separators."""
    path = xlsx_factory([
        {"마켓명": "A마켓", "판매자 고유코드": "CODE1",
         "상품명": "상품A", "주문수량": 1234, "주문일": "2024-01-01"},
    ])
    with open(path, "rb") as f:
        data = {"file": (f, "test.xlsx")}
        response = client.post("/upload", data=data, content_type="multipart/form-data")
    html = response.data.decode("utf-8")
    assert "1,234" in html


def test_413_error(client):
    """Request exceeding MAX_CONTENT_LENGTH returns file size error."""
    app.config["MAX_CONTENT_LENGTH"] = 100  # Set very small limit for test
    try:
        data = {"file": (io.BytesIO(b"x" * 200), "large.xlsx")}
        response = client.post("/upload", data=data, content_type="multipart/form-data")
        html = response.data.decode("utf-8")
        assert response.status_code == 413
        assert "파일 크기가 너무 큽니다" in html
    finally:
        app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Restore
