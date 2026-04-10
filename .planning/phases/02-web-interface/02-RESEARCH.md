# Phase 2: Web Interface - Research

**Researched:** 2026-04-10
**Domain:** Flask web application with file upload and HTML table rendering
**Confidence:** HIGH

## Summary

Phase 2 builds a Flask web application that accepts .xlsx file uploads (button + drag-and-drop), processes them through the existing `process_sales_data()` function from Phase 1, and displays results as an HTML table with summary statistics. The scope is a single-page server-rendered app with minimal JavaScript (only for drag-and-drop and loading feedback).

The core pattern is straightforward: Flask route receives file via `request.files`, saves to a temp file, calls `process_sales_data(temp_path)`, renders results with Jinja2. The drag-and-drop UX requires vanilla JavaScript (~30 lines) to handle `dragover`/`drop` events on the document and submit via `fetch()` or form submission. Error handling maps Python exceptions to Korean user-facing messages.

**Primary recommendation:** Single-file Flask app (`src/app.py`) with one template (`templates/index.html`) and inline CSS. Use `tempfile.NamedTemporaryFile` for uploaded files, clean up after processing. No CSS framework needed for this scope.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** 교체형 레이아웃 -- 초기 화면에 업로드 영역만 표시, 업로드 후 결과 테이블로 화면 교체. 다시 업로드하려면 '새 파일 업로드' 버튼 클릭.
- **D-02:** 색상 포인트 있는 디자인 -- 헤더나 버튼에 브랜드 색상 적용.
- **D-03:** 콤팩트 업로드 버튼 -- 안내 텍스트 + 파일 선택 버튼 구성. 드래그는 페이지 전체에서 받음.
- **D-04:** 버튼 로딩 피드백 -- 파일 선택 후 버튼이 '처리 중...' 상태로 변경.
- **D-05:** 줄무늬 적용 -- 짝수/홀수 행 배경색 교대.
- **D-06:** 요약 정보는 테이블 위에 표시 -- "전체 N건 -> 중복 제거 후 M건, K개 고유코드" 형태.
- **D-07:** 숫자(주문수량 합계)는 천 단위 콤마 구분 (예: 1,234).
- **D-08:** 날짜(최근 주문일)는 YYYY-MM-DD 포맷.

### Claude's Discretion
- 에러 메시지 표시 위치 및 스타일
- 구체적인 색상 팔레트 선택
- CSS 프레임워크 사용 여부 (순수 CSS vs Bootstrap 등)
- Flask 앱 구조 (단일 파일 vs 모듈 분리)

### Deferred Ideas (OUT OF SCOPE)
None
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| UPLD-01 | 사용자가 .xlsx 파일을 선택하여 업로드할 수 있다 | Flask file upload pattern: `request.files`, `<input type="file">` with accept=".xlsx" |
| UPLD-02 | 사용자가 드래그 앤 드롭으로 파일을 업로드할 수 있다 | HTML5 Drag and Drop API on document level, JavaScript FormData + fetch/form submit |
| UPLD-03 | 잘못된 파일 업로드 시 명확한 에러 메시지를 볼 수 있다 | Extension check + ValueError from processor + empty file check, Korean messages |
| DISP-01 | 결과가 HTML 테이블로 웹 페이지에 표시된다 | Jinja2 template rendering with DataFrame iteration, zebra striping |
| DISP-03 | 처리 건수 요약이 표시된다 | summary_dict from process_sales_data() + len(result_df) for unique code count |
</phase_requirements>

## Standard Stack

### Core (already installed)
| Library | Version | Purpose | Verified |
|---------|---------|---------|----------|
| Flask | 3.1.3 | Web framework, routing, request handling | [VERIFIED: `python3 -c "import flask"` -- 3.1.3 installed] |
| pandas | 2.2.3 | Data processing (Phase 1 dependency) | [VERIFIED: `python3 -c "import pandas"` -- 2.2.3 installed] |
| openpyxl | 3.1.5 | Excel reading engine | [VERIFIED: `python3 -c "import openpyxl"` -- 3.1.5 installed] |
| Jinja2 | 3.1.6 | HTML templating (bundled with Flask) | [VERIFIED: `python3 -c "import jinja2"` -- 3.1.6 installed] |
| Werkzeug | bundled | File upload handling, secure_filename | [VERIFIED: bundled with Flask 3.1.3] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| tempfile | stdlib | Temporary file for uploaded xlsx | Always -- save upload to temp, process, delete |

### No Additional Dependencies Needed

All required packages are already in `requirements.txt`. No new packages to install for this phase.

## Architecture Patterns

### Recommended Project Structure
```
src/
  __init__.py          # existing
  processor.py         # existing (Phase 1)
  app.py               # NEW: Flask application
templates/
  index.html           # NEW: single Jinja2 template (upload + results)
tests/
  conftest.py          # existing
  test_processor.py    # existing
  test_app.py          # NEW: Flask app tests
```

**Rationale for single-file app:** This is a 2-route application (GET / and POST /upload). A single `app.py` with a single template is appropriate. No blueprint, no factory pattern needed. [ASSUMED -- Claude's discretion per CONTEXT.md]

### Pattern 1: Flask File Upload with Temp File
**What:** Receive upload, save to temp file, process, render, clean up
**When to use:** Always -- this is the core flow

```python
# Source: Flask official file upload pattern + project-specific integration
import os
import tempfile
from flask import Flask, request, render_template, flash
from werkzeug.utils import secure_filename
from src.processor import process_sales_data

app = Flask(__name__, template_folder="../templates")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB limit
app.secret_key = os.urandom(24)  # for flash messages

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        return render_template("index.html", error="파일을 선택해주세요.")

    if not file.filename.lower().endswith(".xlsx"):
        return render_template("index.html", error=".xlsx 파일만 업로드할 수 있습니다.")

    # Save to temp file, process, clean up
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    try:
        file.save(tmp.name)
        tmp.close()
        result_df, summary = process_sales_data(tmp.name)
        # ... render results
    except ValueError as e:
        return render_template("index.html", error=str(e))
    finally:
        os.unlink(tmp.name)
```
[VERIFIED: Flask file upload pattern from official docs -- flask.palletsprojects.com/en/stable/patterns/fileuploads/]

### Pattern 2: Drag-and-Drop with Full-Page Drop Target (D-03)
**What:** JavaScript handles dragover/drop on `document`, submits file via hidden form
**When to use:** Required by D-03 -- drag anywhere on page

```javascript
// Prevent default browser behavior (open file)
document.addEventListener("dragover", (e) => {
    e.preventDefault();
    document.body.classList.add("drag-over");
});

document.addEventListener("dragleave", (e) => {
    // Only if leaving the document
    if (e.relatedTarget === null) {
        document.body.classList.remove("drag-over");
    }
});

document.addEventListener("drop", (e) => {
    e.preventDefault();
    document.body.classList.remove("drag-over");
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        // Set file to hidden input and submit form
        const input = document.getElementById("file-input");
        input.files = files;
        document.getElementById("upload-form").submit();
    }
});
```
[CITED: HTML5 Drag and Drop API -- developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API]

### Pattern 3: Replacement Layout (D-01)
**What:** Single template with conditional rendering -- upload view vs. results view
**When to use:** Required by D-01

```html
{% if results %}
  <!-- Results view: summary + table + "새 파일 업로드" button -->
  <div class="summary">{{ summary_text }}</div>
  <table>...</table>
  <a href="/" class="btn">새 파일 업로드</a>
{% else %}
  <!-- Upload view: instruction text + file button -->
  <p>엑셀 파일(.xlsx)을 선택하거나 이 페이지에 드래그하세요</p>
  <form id="upload-form" action="/upload" method="post" enctype="multipart/form-data">
    <input type="file" id="file-input" name="file" accept=".xlsx">
    <button type="submit">업로드</button>
  </form>
{% endif %}

{% if error %}
  <div class="error">{{ error }}</div>
{% endif %}
```
[ASSUMED -- standard Jinja2 conditional pattern]

### Pattern 4: Number Formatting in Jinja2 (D-07, D-08)
**What:** Format numbers with comma separator and dates as YYYY-MM-DD
**When to use:** Required by D-07 and D-08

```python
# In app.py -- register Jinja2 filter
@app.template_filter("comma")
def comma_filter(value):
    """천 단위 콤마: 1234 -> 1,234"""
    return f"{int(value):,}"
```

```html
<!-- In template -->
<td>{{ row["주문수량 합계"] | comma }}</td>
<td>{{ row["최근 주문일"].strftime("%Y-%m-%d") if row["최근 주문일"] is not none else "" }}</td>
```
[VERIFIED: Jinja2 custom filter pattern -- Jinja2 docs]

### Anti-Patterns to Avoid
- **Storing uploads permanently:** Don't save files to disk. Use tempfile + cleanup. No UPLOAD_FOLDER needed.
- **Using DataFrame.to_html():** It generates uncontrolled HTML with no CSS hooks. Use Jinja2 `{% for %}` loop instead for full control over classes, formatting, striping.
- **JavaScript framework for drag-and-drop:** Dropzone.js or similar is overkill. 20-30 lines of vanilla JS handles full-page drop.
- **Separate API endpoint returning JSON:** The app is server-rendered. POST /upload returns HTML directly. No fetch() + JSON response needed.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| File extension validation | Complex MIME type checking | `.filename.endswith(".xlsx")` + accept attribute | Only .xlsx needed, MIME checking adds complexity for no gain in this use case |
| Temp file management | Manual file path generation | `tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)` + `os.unlink()` | Handles unique naming, proper temp directory |
| XSS protection in template | Manual HTML escaping | Jinja2 auto-escaping (enabled by default in Flask) | Flask enables autoescaping for .html templates |
| CSRF protection | Custom token system | Not needed -- personal local tool, no auth | Would add complexity for zero security benefit |

## Common Pitfalls

### Pitfall 1: Forgetting enctype="multipart/form-data"
**What goes wrong:** Form submits but `request.files` is empty
**Why it happens:** Default form encoding doesn't support file uploads
**How to avoid:** Always set `enctype="multipart/form-data"` on file upload forms
**Warning signs:** `request.files.get("file")` returns None even when file was selected

### Pitfall 2: Not Cleaning Up Temp Files on Error
**What goes wrong:** Temp files accumulate on disk after exceptions
**Why it happens:** Error in `process_sales_data()` skips cleanup
**How to avoid:** Use `try/finally` block with `os.unlink()` in finally
**Warning signs:** Growing temp directory

### Pitfall 3: MAX_CONTENT_LENGTH Error Handling
**What goes wrong:** Flask returns 413 error with no user-friendly message
**Why it happens:** Werkzeug raises `RequestEntityTooLarge` before route handler runs
**How to avoid:** Register `@app.errorhandler(413)` to return Korean error message
**Warning signs:** Raw HTML error page instead of styled error

### Pitfall 4: Drag-and-Drop Browser Default Behavior
**What goes wrong:** Browser opens the dropped file instead of uploading
**Why it happens:** Default `dragover` and `drop` behavior is to open/navigate to file
**How to avoid:** `e.preventDefault()` on BOTH `dragover` AND `drop` events
**Warning signs:** Dropping file navigates away from the page

### Pitfall 5: Empty File Upload
**What goes wrong:** User submits form without selecting a file, or drops a non-file item
**Why it happens:** No client-side validation, empty filename check missing
**How to avoid:** Check `file.filename == ""` and `file.content_length == 0` server-side
**Warning signs:** Cryptic pandas error instead of user-friendly message

### Pitfall 6: DataTransfer.files Assignment
**What goes wrong:** Cannot set `input.files = e.dataTransfer.files` in older browsers
**Why it happens:** FileList assignment was not always supported
**How to avoid:** Use FormData + form submit approach. Alternatively, submit the form programmatically after setting files. Modern browsers (all current) support this.
**Warning signs:** Only applies if targeting very old browsers -- not a concern for this local tool

## Code Examples

### Complete Flask App Structure
```python
# src/app.py
# Source: Flask official patterns + project integration
import os
import tempfile
from flask import Flask, request, render_template

from src.processor import process_sales_data

app = Flask(__name__, template_folder="../templates")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB


@app.template_filter("comma")
def comma_filter(value):
    return f"{int(value):,}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    # Validation
    if not file or file.filename == "":
        return render_template("index.html", error="파일을 선택해주세요.")
    if not file.filename.lower().endswith(".xlsx"):
        return render_template("index.html", error=".xlsx 파일만 업로드할 수 있습니다.")

    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    try:
        file.save(tmp.name)
        tmp.close()
        result_df, summary = process_sales_data(tmp.name)

        # K개 고유코드 = result rows (each row is a unique code+market combo)
        unique_codes = len(result_df)

        # Convert DataFrame to list of dicts for template
        rows = result_df.to_dict("records")

        return render_template(
            "index.html",
            results=rows,
            summary=summary,
            unique_codes=unique_codes,
        )
    except ValueError as e:
        return render_template("index.html", error=str(e))
    except Exception:
        return render_template("index.html", error="파일 처리 중 오류가 발생했습니다.")
    finally:
        os.unlink(tmp.name)


@app.errorhandler(413)
def too_large(e):
    return render_template("index.html", error="파일 크기가 너무 큽니다. (최대 16MB)"), 413
```
[VERIFIED: Flask patterns from official docs, integrated with project's process_sales_data API]

### Flask Test Client Pattern
```python
# tests/test_app.py
import io
import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "업로드" in response.data.decode("utf-8")


def test_upload_no_file(client):
    response = client.post("/upload", content_type="multipart/form-data")
    assert "파일을 선택해주세요" in response.data.decode("utf-8")


def test_upload_wrong_extension(client):
    data = {"file": (io.BytesIO(b"test"), "test.csv")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert ".xlsx 파일만" in response.data.decode("utf-8")


def test_upload_valid_xlsx(client, xlsx_factory):
    path = xlsx_factory([{
        "마켓명": "A마켓", "판매자 고유코드": "CODE1",
        "상품명": "상품A", "주문수량": 10, "주문일": "2024-01-01"
    }])
    with open(path, "rb") as f:
        data = {"file": (f, "test.xlsx")}
        response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert "CODE1" in response.data.decode("utf-8")
```
[ASSUMED -- standard Flask test_client pattern, adapted with existing conftest fixtures]

### Summary Display Pattern (D-06)
```html
<!-- 요약: "전체 N건 -> 중복 제거 후 M건, K개 고유코드" -->
<div class="summary">
    전체 {{ summary.total_rows }}건
    {% if summary.skipped_rows > 0 %}
        ({{ summary.skipped_rows }}건 제외)
    {% endif %}
    &rarr; 중복 제거 후 {{ summary.result_rows }}건, {{ unique_codes }}개 고유코드
</div>
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Flask-Uploads extension | Built-in Werkzeug FileStorage | Flask-Uploads deprecated ~2020 | Use native Flask file handling, no extension needed |
| jQuery AJAX file upload | Vanilla JS Fetch + FormData | ~2020 | No jQuery dependency needed |
| Separate CSS file for small apps | Inline `<style>` in template | Always valid for single-page | One less file to manage |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Single-file app structure (app.py) is sufficient | Architecture Patterns | LOW -- easily refactored if needed |
| A2 | No CSS framework needed (pure CSS sufficient) | Architecture Patterns | LOW -- can add later without breaking changes |
| A3 | Form submission (not fetch+JSON) is best for replacement layout | Architecture Patterns | LOW -- page reload is desired behavior for layout replacement |
| A4 | Flask test_client with existing conftest fixtures will work | Code Examples | LOW -- may need minor fixture adaptation |

## Open Questions

1. **Template directory location**
   - What we know: Flask default is `templates/` relative to app module. With app in `src/`, need explicit `template_folder="../templates"` or put templates inside `src/templates/`.
   - What's unclear: Project convention for template location not established.
   - Recommendation: Use `templates/` at project root with `template_folder="../templates"` in Flask init. Keeps templates separate from Python code.

2. **Flask app entry point**
   - What we know: Need a way to run `flask run` from project root.
   - What's unclear: Whether to use `FLASK_APP` env var or a run script.
   - Recommendation: Add `FLASK_APP=src.app:app` to a `.flaskenv` file, or document `flask --app src.app run --debug`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runtime | Yes | 3.14.3 | -- |
| Flask | Web framework | Yes | 3.1.3 | -- |
| pandas | Data processing | Yes | 2.2.3 | -- |
| openpyxl | Excel engine | Yes | 3.1.5 | -- |
| Jinja2 | Templating | Yes | 3.1.6 | -- |
| pytest | Testing | Yes | 8.x | -- |

**Missing dependencies with no fallback:** None
**Missing dependencies with fallback:** None

All required packages already installed. No new dependencies needed.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x |
| Config file | None -- pytest auto-discovers from project root |
| Quick run command | `python -m pytest tests/test_app.py -x -q` |
| Full suite command | `python -m pytest tests/ -x -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| UPLD-01 | .xlsx file upload via button | integration | `python -m pytest tests/test_app.py::test_upload_valid_xlsx -x` | No -- Wave 0 |
| UPLD-02 | Drag-and-drop upload | manual-only | Manual browser test (JS behavior) | N/A |
| UPLD-03 | Error messages for invalid files | integration | `python -m pytest tests/test_app.py::TestErrorHandling -x` | No -- Wave 0 |
| DISP-01 | Results in HTML table | integration | `python -m pytest tests/test_app.py::test_results_table -x` | No -- Wave 0 |
| DISP-03 | Summary statistics display | integration | `python -m pytest tests/test_app.py::test_summary_display -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_app.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_app.py` -- covers UPLD-01, UPLD-03, DISP-01, DISP-03
- [ ] Flask test client fixture in test_app.py or conftest.py

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Personal local tool, no auth |
| V3 Session Management | No | No sessions needed |
| V4 Access Control | No | No access control needed |
| V5 Input Validation | Yes | File extension check + pandas ValueError for column validation |
| V6 Cryptography | No | No crypto operations |

### Known Threat Patterns for Flask File Upload

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via filename | Tampering | `secure_filename()` from werkzeug (not strictly needed since we use tempfile, but good practice) |
| Large file DoS | Denial of Service | `MAX_CONTENT_LENGTH = 16MB` in Flask config |
| Malicious file content | Tampering | File is only read by openpyxl/pandas -- limited attack surface. No file execution. |

**Note:** This is a personal local tool with no authentication, no public access, and no persistent storage. Security posture is minimal by design.

## Sources

### Primary (HIGH confidence)
- Flask 3.1.3 installed locally -- version and API verified via import [VERIFIED]
- Flask official file upload docs -- flask.palletsprojects.com/en/stable/patterns/fileuploads/ [CITED]
- Existing project code: `src/processor.py` API (return type, error handling) [VERIFIED: codebase grep]
- Existing test infrastructure: `tests/conftest.py` fixtures [VERIFIED: codebase grep]

### Secondary (MEDIUM confidence)
- Miguel Grinberg Flask file upload tutorial -- blog.miguelgrinberg.com/post/handling-file-uploads-with-flask [CITED]
- HTML5 Drag and Drop API -- MDN Web Docs [CITED]

### Tertiary (LOW confidence)
- None -- all patterns are well-established Flask fundamentals

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all packages verified installed, versions confirmed
- Architecture: HIGH -- straightforward Flask patterns, well-documented
- Pitfalls: HIGH -- common Flask file upload issues, well-known

**Research date:** 2026-04-10
**Valid until:** 2026-05-10 (stable stack, no fast-moving dependencies)
