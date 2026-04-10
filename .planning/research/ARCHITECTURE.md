# Architecture Research

**Domain:** Excel data processing web app (sales data analyzer)
**Researched:** 2026-04-10
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Browser (Client)                       │
│  ┌───────────────┐  ┌────────────────────────────────┐  │
│  │ Upload Form   │  │ Results Table (HTML)            │  │
│  │ (.xlsx input) │  │ (rendered by Jinja2 template)   │  │
│  └───────┬───────┘  └────────────────▲───────────────┘  │
│          │ POST multipart/form-data  │ HTML response     │
├──────────┼───────────────────────────┼──────────────────┤
│          ▼                           │                   │
│  ┌───────────────────────────────────┴───────────────┐  │
│  │              Flask Route Handler                   │  │
│  │  - Receive file upload                            │  │
│  │  - Validate file type                             │  │
│  │  - Pass to processor                              │  │
│  │  - Render template with results                   │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │                                   │
│  ┌───────────────────▼───────────────────────────────┐  │
│  │           Data Processor (pandas)                  │  │
│  │  - Read xlsx into DataFrame                       │  │
│  │  - Deduplicate by 판매자 고유코드                    │  │
│  │  - Group by 판매자 고유코드, sum 주문수량              │  │
│  │  - Return processed DataFrame                     │  │
│  └───────────────────────────────────────────────────┘  │
│                      Flask App (Server)                  │
└─────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Upload Form | File selection, submit to server | HTML form with `enctype="multipart/form-data"` |
| Flask Route Handler | HTTP handling, file validation, orchestration | Flask route with `request.files`, file extension check |
| Data Processor | Excel parsing, dedup, aggregation | pandas `read_excel()`, `groupby()`, `agg()` |
| Results Template | Display processed data as table | Jinja2 template iterating over DataFrame rows |

## Recommended Project Structure

```
app/
├── app.py              # Flask application entry point, routes
├── processor.py        # Excel data processing logic (pandas)
├── templates/
│   ├── index.html      # Upload form + results table page
│   └── error.html      # Error display page
├── static/
│   └── style.css       # Minimal styling for table and form
└── requirements.txt    # Python dependencies
```

### Structure Rationale

- **Flat structure:** This is a single-purpose personal tool. One route handler, one processor module. No need for blueprints, packages, or MVC layering.
- **processor.py separated from app.py:** Keeps data logic testable independently from Flask. The processor takes a file object in, returns a DataFrame out -- no HTTP awareness.
- **Single template with conditional rendering:** Show the upload form always. Show the results table only when data has been processed. One page, no navigation needed.

## Architectural Patterns

### Pattern 1: In-Memory Processing (No File Storage)

**What:** Read the uploaded file directly from the request stream into pandas without saving to disk.
**When to use:** Small files (under a few MB), no need to retain the file after processing.
**Trade-offs:** Simpler (no temp file cleanup), but file cannot be re-processed without re-upload.

**Example:**
```python
from flask import Flask, request, render_template
import pandas as pd

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename.endswith(".xlsx"):
            results = process_excel(file)  # pass file stream directly
    return render_template("index.html", results=results)
```

### Pattern 2: Processor as Pure Function

**What:** The data processing module takes a file-like object, returns structured data (DataFrame or list of dicts). Zero knowledge of Flask, HTTP, or templates.
**When to use:** Always, even for small projects. Keeps logic testable.
**Trade-offs:** Tiny overhead of one extra module. Worth it for clarity.

**Example:**
```python
# processor.py
import pandas as pd

def process_sales_data(file) -> pd.DataFrame:
    df = pd.read_excel(file, engine="openpyxl")
    grouped = df.groupby("판매자 고유코드").agg(
        상품명=("상품명", "first"),
        판매수량=("주문수량", "sum")
    ).reset_index()
    return grouped.sort_values("판매수량", ascending=False)
```

### Pattern 3: Single-Page Upload + Results

**What:** One page handles both the upload form and the results display. No separate pages, no redirects.
**When to use:** Simple tools with one workflow.
**Trade-offs:** Simplest possible UX. No URL state management needed.

## Data Flow

### Request Flow

```
[User selects .xlsx file and clicks upload]
    │
    ▼
[Browser] ─── POST /  (multipart/form-data) ───▶ [Flask Route]
                                                       │
                                                       ▼
                                                  [Validate]
                                                  - file exists?
                                                  - .xlsx extension?
                                                       │
                                              ┌────────┴────────┐
                                              │ Invalid         │ Valid
                                              ▼                 ▼
                                         [Error msg]    [processor.process_sales_data(file)]
                                              │                 │
                                              │                 ▼
                                              │         [pandas reads xlsx]
                                              │         [groupby 판매자 고유코드]
                                              │         [sum 주문수량]
                                              │         [sort descending]
                                              │                 │
                                              ▼                 ▼
                                    [render index.html   [render index.html
                                     with error]          with results table]
                                              │                 │
                                              ▼                 ▼
                                         [Browser displays page]
```

### Key Data Flows

1. **Upload flow:** Browser sends xlsx binary via multipart POST. Flask receives it as a `FileStorage` object. Passed directly to pandas `read_excel()` (no disk write).
2. **Processing flow:** Raw DataFrame (all columns, ~600 rows) is grouped by `판매자 고유코드`. Aggregation produces summary DataFrame with code, product name (first occurrence), and total quantity. Sorted by quantity descending.
3. **Display flow:** Summary DataFrame is converted to list of dicts or passed directly to Jinja2 template. Template iterates rows and renders HTML table.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1 user, ~600 rows (current) | In-memory processing, development server, no optimizations needed |
| Multiple files, ~10K rows | Still fine with same architecture. pandas handles 10K rows trivially |
| 100K+ rows | Add progress indicator, consider chunked reading. Still single-server |

### Scaling Priorities

This is a personal tool. Scaling is not a concern. The entire dataset (~600 rows) processes in under 100ms on any modern machine. The architecture is deliberately simple because simplicity is the correct scaling strategy for personal tools.

## Anti-Patterns

### Anti-Pattern 1: Over-Engineering the Structure

**What people do:** Create a full MVC structure with blueprints, models, services, repositories, and dependency injection for a single-purpose tool.
**Why it's wrong:** Adds navigation complexity, more files to maintain, zero benefit for a tool with one route and one function.
**Do this instead:** Flat structure. Two Python files (app.py + processor.py), one template, done.

### Anti-Pattern 2: Saving Uploaded Files to Disk

**What people do:** Save the uploaded xlsx to a temp directory, then read it back with pandas, then forget to clean up.
**Why it's wrong:** Unnecessary I/O, temp file cleanup burden, potential disk space issues over time.
**Do this instead:** Pass the file stream directly to `pd.read_excel()`. It accepts file-like objects. No disk needed.

### Anti-Pattern 3: Using Database for Transient Data

**What people do:** Store uploaded data in SQLite/PostgreSQL "just in case" or "for history."
**Why it's wrong:** The project explicitly scopes out database storage. Each upload is a fresh analysis. Adding DB adds migration, connection management, and schema maintenance overhead.
**Do this instead:** Process in memory, render, forget. If the user wants to see data again, they re-upload.

### Anti-Pattern 4: Building a SPA Frontend

**What people do:** Use React/Vue for the frontend with a separate API backend.
**Why it's wrong:** Massively increases complexity (build tools, API serialization, CORS, two codebases) for a single upload-and-view workflow.
**Do this instead:** Server-rendered HTML with Jinja2 templates. One form, one table. Minimal CSS.

## Integration Points

### External Services

None. This is a self-contained local tool with no external dependencies beyond Python packages.

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| app.py <-> processor.py | Direct function call | processor receives file-like object, returns DataFrame |
| app.py <-> templates | Jinja2 rendering | Pass DataFrame (as records) and error messages to template context |
| Browser <-> Flask | HTTP POST (upload), HTTP GET (page load) | Single endpoint `/` handles both methods |

## Build Order (Dependency Graph)

Build order follows data flow direction:

1. **processor.py first** -- Core logic with no dependencies on Flask. Can be tested standalone with a sample xlsx file. This is the project's actual value.
2. **app.py second** -- Flask route that wires upload to processor. Depends on processor.py existing.
3. **templates/index.html third** -- Needs to know what data shape the route provides (column names, data format). Depends on app.py's render context being defined.
4. **static/style.css last** -- Pure presentation. No functional dependencies.

This ordering means the most critical and testable piece (data processing) is built and verified before any web layer exists.

## Sources

- [Upload and Read Excel File in Flask - GeeksforGeeks](https://www.geeksforgeeks.org/python/upload-and-read-excel-file-in-flask/)
- [Pandas vs Openpyxl Guide - Statology](https://www.statology.org/how-to-effectively-work-with-excel-files-in-python-pandas-vs-openpyxl-guide/)
- [Should I use openpyxl or pandas? - Python.org Discussion](https://discuss.python.org/t/should-i-be-using-openpyxl-or-pandas-to-read-write-spreadsheets/65012)
- [Building an Excel Data Processing Web App with Flask - LinkedIn](https://www.linkedin.com/pulse/building-excel-data-processing-web-application-flask-castellon)

---
*Architecture research for: 판매정보 엑셀 분석 웹앱*
*Researched: 2026-04-10*
