# Project Research Summary

**Project:** Sales Data Excel Analysis Web App (판매정보 엑셀 분석 웹앱)
**Domain:** Data processing web tool (single-purpose, personal use)
**Researched:** 2026-04-10
**Confidence:** HIGH

## Executive Summary

This project is a straightforward single-purpose web tool: upload an Excel file of sales data (~600 rows), deduplicate by seller code, sum order quantities per code, and display results in a table. Experts build this type of tool with the simplest possible stack -- Flask for HTTP handling, pandas for data processing, server-rendered HTML for display. There is no need for a frontend framework, database, API layer, or async processing. The entire architecture fits in two Python files and one HTML template.

The recommended approach is a flat Flask application with in-memory processing. The uploaded Excel file is read directly from the request stream into a pandas DataFrame (never saved to disk), processed with groupby/sum operations, and rendered as an HTML table via Jinja2. This is a solved pattern with extensive documentation. The main technical risk is not complexity but silent data corruption -- Korean column name mismatches from whitespace, numeric columns loaded as strings causing concatenated sums instead of arithmetic sums, and NaN keys being silently dropped from groupby results. All of these produce output that looks correct but is wrong.

Key risks are mitigated through defensive data loading: strip column whitespace on read, explicitly cast numeric types with `pd.to_numeric(errors='coerce')`, use `groupby(dropna=False)`, and validate expected columns exist before processing. The `defusedxml` package should be installed from day one to prevent XML-based attacks via crafted xlsx files. These are all low-cost preventions that must be built into Phase 1, not added later.

## Key Findings

### Recommended Stack

The stack is deliberately minimal. Flask 3.1.x handles routing and file uploads. pandas 2.2.x (not 3.0.x -- breaking changes with Copy-on-Write and PyArrow string dtype add risk for zero benefit) handles Excel reading and data aggregation. openpyxl 3.1.x is the Excel engine used by pandas under the hood. Jinja2 (bundled with Flask) renders HTML. No JavaScript framework, no database, no build tools.

**Core technologies:**
- **Python 3.12:** Latest stable with broadest library compatibility (3.13 available but less tested)
- **Flask 3.1.x:** HTTP/routing -- right tool for simple server-rendered apps; FastAPI would add unnecessary async/Pydantic complexity
- **pandas 2.2.x:** Data processing -- read_excel, drop_duplicates, groupby/sum in 3-4 lines; v2.2 over v3.0 to avoid migration friction
- **openpyxl 3.1.x:** Excel engine -- required by pandas for .xlsx; no direct API usage needed
- **defusedxml:** Security -- protects against XML bomb attacks in crafted xlsx files; zero-config, just install

### Expected Features

**Must have (table stakes):**
- Excel file upload with drag-and-drop -- the only input mechanism
- File validation (extension, required columns, clear Korean error messages)
- Deduplication by seller code -- core business logic
- Quantity summation per code -- core business logic
- Results table with product name alongside code -- code alone is meaningless
- Processing summary (row counts before/after) -- user sanity check
- Loading indicator and error state display

**Should have (differentiators for usability):**
- Excel download of results -- most practical enhancement; lets user reuse data elsewhere
- Client-side table sorting (click column headers)
- Summary row with totals

**Defer (v2+):**
- Market-based subtotals -- nice but not core workflow
- Raw data preview before processing -- unnecessary if data format is consistent
- Table search/filter -- under 150 result rows, scrolling is sufficient

### Architecture Approach

The architecture is a single-page server-rendered app with no client-side state management. One URL (`/`) handles both GET (show upload form) and POST (process file, show results). The processor module is a pure function: file-like object in, DataFrame out, zero knowledge of Flask. This separation is the one architectural discipline worth enforcing -- it keeps the data logic testable independently.

**Major components:**
1. **Upload Form (HTML)** -- file selection via drag-and-drop or file picker, POST to server
2. **Flask Route Handler (app.py)** -- receives upload, validates file, calls processor, renders template
3. **Data Processor (processor.py)** -- reads Excel, normalizes columns, deduplicates, aggregates, returns DataFrame
4. **Results Template (index.html)** -- conditionally displays upload form or results table with Jinja2

**Build order follows data flow:** processor.py first (testable without Flask), app.py second (wires upload to processor), template third (needs to know data shape), CSS last.

### Critical Pitfalls

1. **Korean column name fragility** -- Whitespace and invisible Unicode characters in Excel headers cause KeyError or silent mismatches. Fix: `df.columns = df.columns.str.strip()` immediately after loading, plus column existence validation.

2. **Numeric data loaded as strings** -- Mixed types in quantity column cause pandas to infer string type; `sum()` then concatenates ("1"+"2"="12") instead of adding. Fix: `pd.to_numeric(df['column'], errors='coerce')` with NaN count reporting.

3. **NaN keys silently dropped from groupby** -- Empty seller codes are excluded from results without warning. Fix: `groupby(dropna=False)` or `fillna()` before grouping, plus row count verification.

4. **XML attack vulnerability** -- Crafted xlsx can exploit openpyxl's XML parser for memory/CPU exhaustion. Fix: install `defusedxml` (openpyxl uses it automatically) and set `MAX_CONTENT_LENGTH`.

5. **Wrong header row** -- Korean business software often exports 1-3 metadata rows above the actual header. Fix: validate expected columns exist after loading; provide clear error if not found.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Core Processing Pipeline

**Rationale:** The data processing logic is the entire value of this tool. Architecture research confirms processor.py should be built and verified first, before any web layer. All critical pitfalls (column normalization, type casting, NaN handling) must be addressed here -- they cannot be bolted on later without risking silent data corruption.

**Delivers:** Working data processor that reads xlsx, validates columns, normalizes data types, deduplicates by seller code, sums quantities, and returns a clean DataFrame. Testable as a standalone module.

**Addresses features:** Deduplication, quantity summation, product name retention, processing summary counts.

**Avoids pitfalls:** Korean column name fragility, numeric-as-string concatenation, NaN key dropping, wrong header row detection.

### Phase 2: Web Interface (Upload + Display)

**Rationale:** With the processor verified, the web layer is straightforward wiring. Flask route receives file, passes to processor, renders results. Architecture research confirms this is a single-page pattern -- one URL, conditional rendering, no navigation.

**Delivers:** Working web app with file upload (drag-and-drop), validation with Korean error messages, results table display, loading indicator. The tool is usable end-to-end.

**Addresses features:** File upload with drag-and-drop, file validation, error display, results table, loading indicator.

**Avoids pitfalls:** File not saved to disk (in-memory processing), MAX_CONTENT_LENGTH set, defusedxml installed, Korean error messages instead of 500 errors.

### Phase 3: Usability Enhancements

**Rationale:** Once the core tool works, add features that make it genuinely useful for daily work. Excel download is the highest-value addition -- without it, the user can only look at the table. Sorting and summary row are low-effort, high-impact.

**Delivers:** Excel download of processed results, client-side table sorting, summary totals row.

**Addresses features:** Result download, column sorting, summary row.

### Phase Ordering Rationale

- **Processor before web layer** because the processor is the product's actual value and is testable in isolation. Building web UI first risks building around untested data logic.
- **All critical pitfalls addressed in Phase 1** because they cause silent data corruption -- the worst class of bug for a data analysis tool. Adding defenses later means all data processed before the fix is suspect.
- **Enhancements last** because they add polish to a working tool. None are required for the tool to fulfill its core purpose.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** May need research if the actual Excel file format has unexpected structure (metadata rows, merged cells, multiple header rows). Recommend testing with real sample files early.

Phases with standard patterns (skip research-phase):
- **Phase 2:** Flask file upload + Jinja2 table rendering is extremely well-documented. No research needed.
- **Phase 3:** pandas to_excel + Flask send_file for download, and client-side JS table sorting are standard patterns with abundant examples.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Standard Python web stack, all libraries verified on PyPI with current versions |
| Features | HIGH | Clear scope from project definition; feature set is small and well-defined |
| Architecture | HIGH | Solved pattern (Flask + pandas file processing); multiple tutorial sources confirm approach |
| Pitfalls | HIGH | All pitfalls are well-documented in pandas/openpyxl/Flask official docs and community posts |

**Overall confidence:** HIGH

### Gaps to Address

- **Actual Excel file structure:** Research assumes standard headers in row 1. Real files from the user's specific sales platform may have metadata rows, merged cells, or non-standard column names. Validate with a real sample file during Phase 1 implementation.
- **Exact column names:** The specific Korean column names need confirmation against the actual export format. Build the column mapping as a configuration rather than deep-buried hardcoded strings.

## Sources

### Primary (HIGH confidence)
- Flask 3.1.x PyPI and official documentation -- routing, file uploads, configuration
- pandas 2.2.x documentation -- read_excel, groupby, aggregation, type handling
- openpyxl documentation -- xlsx engine, defusedxml security note

### Secondary (MEDIUM confidence)
- GeeksforGeeks, LinkedIn articles -- Flask + Excel upload implementation patterns
- Uploadcare, Eleken -- file upload UX best practices
- Statology -- pandas vs openpyxl usage patterns

### Tertiary (LOW confidence)
- Performance benchmarks (calamine vs openpyxl) -- not directly relevant at 600 rows but useful if scale grows

---
*Research completed: 2026-04-10*
*Ready for roadmap: yes*
