---
phase: 02-web-interface
reviewed: 2026-04-10T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - src/app.py
  - templates/index.html
  - tests/test_app.py
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-04-10
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Reviewed the Flask web application (app.py), Jinja2 template (index.html), and integration tests (test_app.py) for the sales data analyzer. The code is well-structured and follows Flask conventions appropriately. Security basics are handled correctly: Jinja2 auto-escaping protects against XSS, file size limits are enforced, and file extension validation is present. Two warnings were found related to edge-case error handling that could cause unhandled exceptions under specific conditions.

## Warnings

### WR-01: NaT value not handled in template date formatting

**File:** `templates/index.html:180`
**Issue:** The template checks `if row["최근 주문일"] is not none` before calling `.strftime()`. However, when all order dates in a group are unparseable, `pandas.NaT` (Not a Time) is returned by the processor. `NaT` is not Python `None`, so the `is not none` check passes, and `.strftime()` is called on `NaT`. In pandas 2.2.x this returns the string `"NaT"` rather than crashing, but it displays an unintelligible value to the user.
**Fix:** Add an explicit check for NaT, or handle it in the processor before passing to the template:
```python
# Option A: Fix in processor (src/processor.py) before returning
# Replace NaT with None so Jinja2 check works
result["최근 주문일"] = result["최근 주문일"].where(result["최근 주문일"].notna(), None)
```
```html
<!-- Option B: Fix in template with additional check -->
<td>{{ row["최근 주문일"].strftime("%Y-%m-%d") if row["최근 주문일"] is not none and row["최근 주문일"] == row["최근 주문일"] else "" }}</td>
```

### WR-02: NameError if temporary file creation fails

**File:** `src/app.py:39-62`
**Issue:** If `tempfile.NamedTemporaryFile()` on line 39 raises an exception (e.g., disk full, permission error), the variable `tmp` is never assigned. The `finally` block on line 62 then calls `os.unlink(tmp.name)`, which raises `NameError` and masks the original error. While rare in practice, this violates robust error-handling patterns.
**Fix:** Initialize `tmp` before the try block or restructure to use a context manager:
```python
tmp_path = None
try:
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    tmp_path = tmp.name
    file.save(tmp_path)
    tmp.close()
    result_df, summary = process_sales_data(tmp_path)
    # ... render template ...
except ValueError as e:
    return render_template("index.html", error=str(e))
except Exception:
    return render_template("index.html",
        error="파일 처리 중 오류가 발생했습니다. 다른 파일로 다시 시도해주세요.")
finally:
    if tmp_path and os.path.exists(tmp_path):
        os.unlink(tmp_path)
```

## Info

### IN-01: comma_filter assumes integer-convertible input

**File:** `src/app.py:21`
**Issue:** The `comma_filter` template filter calls `int(value)` without guarding against non-numeric or NaN inputs. Currently the processor guarantees numeric output for the aggregated sum column, but if the data pipeline changes or a NaN slips through, this will raise an unhandled `ValueError` in the template rendering phase.
**Fix:** Add a defensive guard:
```python
@app.template_filter("comma")
def comma_filter(value):
    """천 단위 콤마 포맷: 1234 -> 1,234"""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)
```

---

_Reviewed: 2026-04-10_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
