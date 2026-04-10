<!-- GSD:project-start source:PROJECT.md -->
## Project

**판매정보 분석기**

판매정보 엑셀 파일(.xlsx)을 업로드하면 판매자 고유코드 기준으로 중복을 제거하고, 코드별 판매수량 합계를 테이블로 보여주는 파이썬 웹 애플리케이션. 개인 업무용 도구.

**Core Value:** 엑셀 파일 업로드 한 번으로 판매자 고유코드별 판매수량을 즉시 확인할 수 있어야 한다.

### Constraints

- **Tech stack**: Python — 사용자 요청
- **File format**: .xlsx만 지원
- **Deployment**: 로컬 실행 (개발 서버)
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Technologies
| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12 | Runtime | Latest stable with full ecosystem support. 3.13 is available but 3.12 has broader library compatibility. Pandas 3.x requires >=3.11, so 3.12 is the sweet spot. |
| Flask | 3.1.x | Web framework | This is a simple server-rendered web app with file upload and HTML table output -- Flask's sweet spot. No API, no async needs, no WebSocket. Flask gets this running in under 50 lines of route code. FastAPI would add unnecessary complexity (Pydantic models, async patterns) for zero benefit here. |
| pandas | 2.2.x | Data processing | Handles Excel reading, deduplication (`drop_duplicates`), and aggregation (`groupby().sum()`) in 3-4 lines. Using 2.2.x instead of 3.0.x because 3.0 introduced breaking changes (Copy-on-Write default, new string dtype backed by PyArrow) that add complexity without benefit for a 600-row personal tool. 2.2.x is stable, well-documented, and has no Python version friction. |
| openpyxl | 3.1.x | Excel engine | Required by pandas as the default engine for `read_excel()` with .xlsx files. No separate API usage needed -- pandas wraps it automatically. |
| Jinja2 | 3.1.x | HTML templating | Bundled with Flask. Renders the results table server-side. No frontend framework needed for a single-page table display. |
### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Werkzeug | 3.1.x | HTTP/file upload handling | Bundled with Flask. Provides `FileStorage` for secure file upload handling. No separate install needed. |
| python-calamine | 0.3.x | Fast Excel reading (optional) | Only if performance becomes an issue. The calamine engine is 5-28x faster than openpyxl for large files. For 600 rows, openpyxl is fine. Can be added later with `engine="calamine"` in `read_excel()`. |
### Development Tools
| Tool | Purpose | Notes |
|------|---------|-------|
| pip + venv | Package management | Standard Python tooling. `python -m venv venv` to create, `pip install -r requirements.txt` to install. No need for Poetry/PDM for a project this simple. |
| Flask dev server | Local development | `flask run --debug` enables auto-reload and debugger. Sufficient for personal local use -- no production WSGI server needed. |
## Installation
# Create virtual environment
# Core dependencies
# Freeze
## Alternatives Considered
| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Flask | FastAPI | When building an API-first service with many concurrent requests, automatic OpenAPI docs, or async I/O. Not this project -- we serve HTML, not JSON. |
| Flask | Streamlit | When building a quick data dashboard with charts. Streamlit abstracts away HTML/CSS entirely, but gives less control over layout and is overkill for a simple table. Also harder to customize the upload flow. |
| pandas 2.2.x | pandas 3.0.x | When starting a new large-scale data project and wanting the latest features (PyArrow-backed strings, CoW). For this small tool, 2.2.x avoids migration friction. |
| pandas 2.2.x | polars | When processing millions of rows and needing maximum performance. For 600 rows, pandas is simpler, more documented, and has native Excel support. |
| openpyxl | python-calamine | When reading very large Excel files (100K+ rows). Calamine is 5-28x faster but is read-only. For 600 rows, the default openpyxl engine is sufficient. |
| Server-side HTML | React/Vue SPA | When building a complex interactive UI with state management. A single table with file upload needs zero JavaScript framework. |
## What NOT to Use
| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Django | Massive overkill for a single-page tool. ORM, admin, auth, migrations -- none needed here. Adds 20+ files of boilerplate. | Flask |
| Streamlit | Tempting for data apps, but locks you into its component model. Can't easily customize file upload UX or table rendering. Runs its own server model. | Flask + Jinja2 |
| xlrd | Only reads old .xls format (not .xlsx since v2.0). The project explicitly uses .xlsx files. | openpyxl (via pandas) |
| xlwings | Requires Excel to be installed. Heavy dependency for simple read operations. Designed for Excel automation, not web apps. | openpyxl (via pandas) |
| pandas 3.0.x | Breaking changes (CoW default, PyArrow string dtype) add debugging risk for zero benefit on a 600-row personal tool. Wait for ecosystem to stabilize. | pandas 2.2.x |
| JavaScript frontend framework | No interactive state to manage. Server-rendered HTML table is simpler, faster to build, and has zero build tooling. | Jinja2 templates |
| SQLAlchemy / any ORM | Project explicitly excludes database storage. Data is processed per-upload, not persisted. | In-memory pandas DataFrame |
## Stack Patterns by Variant
- Add `python-calamine` for faster Excel reading
- Use `engine="calamine"` in `pd.read_excel()`
- Consider chunked processing with pandas
- pandas `read_excel()` with calamine engine also supports .xls, .xlsm, .xlsb
- For CSV: `pd.read_csv()` -- no additional dependency
- Add `gunicorn` as WSGI server
- Add basic rate limiting on uploads
- Set `MAX_CONTENT_LENGTH` in Flask config to limit file size
## Version Compatibility
| Package | Compatible With | Notes |
|---------|-----------------|-------|
| Flask 3.1.x | Python >=3.9 | No issues with 3.12 |
| pandas 2.2.x | Python >=3.9 | Broad compatibility, well-tested |
| pandas 3.0.x | Python >=3.11 | Would force Python 3.11+ minimum |
| openpyxl 3.1.x | Python >=3.8 | Required as pandas Excel engine for .xlsx |
## Sources
- [Flask PyPI](https://pypi.org/project/Flask/) -- version 3.1.3 confirmed (Feb 2026)
- [pandas release notes](https://pandas.pydata.org/docs/whatsnew/index.html) -- pandas 3.0.2 latest, 2.2.3 stable
- [pandas 3.0 breaking changes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html) -- CoW default, string dtype changes
- [openpyxl PyPI](https://pypi.org/project/openpyxl/) -- version 3.1.5 confirmed
- [Flask vs FastAPI comparison (Strapi)](https://strapi.io/blog/fastapi-vs-flask-python-framework-comparison) -- Flask better for simple server-rendered apps
- [calamine performance benchmarks](https://hakibenita.com/fast-excel-python) -- 5-28x faster than openpyxl for large files
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

테스트
