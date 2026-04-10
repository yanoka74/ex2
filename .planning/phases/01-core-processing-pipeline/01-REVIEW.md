---
phase: 01-core-processing-pipeline
reviewed: 2026-04-10T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - src/processor.py
  - tests/test_processor.py
  - tests/conftest.py
  - requirements.txt
findings:
  critical: 1
  warning: 2
  info: 0
  total: 3
status: issues_found
---

# Phase 1: Code Review Report

**Reviewed:** 2026-04-10
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Reviewed the core processing pipeline: `src/processor.py` (data processing logic), test suite, conftest fixtures, and requirements. The processing logic is well-structured with clear separation of validation, filtering, and aggregation steps. Tests cover the main scenarios thoroughly.

One critical bug was found in the NaN/None filtering logic that causes rows with missing key fields to pass through as the literal strings "nan" or "None" instead of being excluded. Two warnings relate to a crash risk when all dates in a group are unparseable, and a missing test for empty-input behavior.

## Critical Issues

### CR-01: NaN/None values survive key-field filtering due to incorrect operation order

**File:** `src/processor.py:36-43`
**Issue:** `astype(str)` is applied before the `notna()` check. When pandas reads an empty Excel cell, the value is `NaN` (float) or `None`. Calling `.astype(str)` converts these to the literal strings `"nan"` and `"None"`, which then pass both `.str.strip().ne("")` and `.notna()` checks. Rows with missing "판매자 고유코드" or "마켓명" will appear in results with key values of `"nan"` or `"None"`.

Confirmed by test: `pd.Series([None, np.nan]).astype(str).str.strip().ne("")` returns `[True, True]`.

**Fix:** Check `notna()` before converting to string, and also filter out the literal string "nan":
```python
# 판매자 고유코드가 빈 행 제외
valid_df = valid_df[
    valid_df["판매자 고유코드"].notna()
    & valid_df["판매자 고유코드"].astype(str).str.strip().ne("")
]
# 마켓명이 빈 행 제외
valid_df = valid_df[
    valid_df["마켓명"].notna()
    & valid_df["마켓명"].astype(str).str.strip().ne("")
]
```

Since pandas uses short-circuit-like semantics with `&`, `notna()` first eliminates NaN/None rows, and then `astype(str)` only processes actual values.

Note: pandas `&` does not truly short-circuit (both sides are evaluated), but `notna()` being first in the boolean mask means the combined result is correct -- NaN rows will be False from the left operand regardless of the right operand's value.

## Warnings

### WR-01: `idxmax()` crashes when all dates in a group are unparseable (NaT)

**File:** `src/processor.py:60`
**Issue:** After line 55 converts "주문일" with `errors="coerce"`, some or all dates in a group could be `NaT`. If every "주문일" value in a group is `NaT`, `group["주문일"].idxmax()` raises `ValueError: attempt to get argmax of an empty sequence` (current behavior) or will raise `ValueError` in a future pandas version. This can happen when the Excel file has valid key fields and quantities, but malformed date strings.

**Fix:** Handle the all-NaT case in `aggregate_group`:
```python
def aggregate_group(group):
    valid_dates = group["주문일"].dropna()
    if valid_dates.empty:
        latest_idx = group.index[0]  # fallback to first row
    else:
        latest_idx = valid_dates.idxmax()
    return pd.Series({
        "마켓명": group.name[1],
        "판매자 고유코드": group.name[0],
        "상품명": group.loc[latest_idx, "상품명"],
        "주문수량 합계": group["주문수량"].sum(),
        "최근 주문일": group["주문일"].max(),
    })
```

### WR-02: No test covers all-rows-filtered (empty result) scenario

**File:** `tests/test_processor.py`
**Issue:** There is no test for the case where all rows are invalid (all filtered out), resulting in an empty DataFrame. If every row has invalid quantities or missing keys, `groupby().apply()` on an empty DataFrame may produce unexpected column ordering or an empty DataFrame without the expected columns, causing the `result[RESULT_COLUMNS]` selection on line 77 to raise a `KeyError`.

**Fix:** Add a test case:
```python
class TestEmptyResult:
    """All rows are invalid -- result should be an empty DataFrame with correct columns."""

    def test_all_rows_invalid(self, xlsx_factory):
        rows = [
            {"판매자 고유코드": "", "마켓명": "", "상품명": "제품A",
             "주문수량": "abc", "주문일": "2026-01-01"},
        ]
        path = xlsx_factory(rows)
        result_df, summary = process_sales_data(path)

        assert len(result_df) == 0
        assert list(result_df.columns) == ["마켓명", "판매자 고유코드", "상품명", "주문수량 합계", "최근 주문일"]
```

---

_Reviewed: 2026-04-10_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
