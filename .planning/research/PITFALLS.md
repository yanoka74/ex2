# Pitfalls Research

**Domain:** Python Excel processing web app (sales data analyzer)
**Researched:** 2026-04-10
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Korean Column Name Matching Fragility

**What goes wrong:**
Excel column headers contain Korean text (판매자 고유코드, 주문수량 etc.). Code that hardcodes exact column names breaks when the Excel file has leading/trailing whitespace, invisible Unicode characters (NBSP, zero-width spaces), or slightly different naming between exports. The app silently produces wrong results or crashes with a KeyError.

**Why it happens:**
Developers test with one sample file and hardcode `df['판매자 고유코드']`. Real-world Excel files from different export sources have inconsistent whitespace or encoding in headers.

**How to avoid:**
- Strip whitespace from all column names immediately after loading: `df.columns = df.columns.str.strip()`
- Validate that expected columns exist before processing; return a clear error message listing found vs. expected columns
- Use a column mapping/normalization step that can handle minor variations

**Warning signs:**
- KeyError on column access that "looks correct"
- Works with one file but fails with another from the same source
- Columns appear identical visually but `df.columns.tolist()` shows differences

**Phase to address:**
Phase 1 (Core Excel processing) -- column normalization must be built into the initial file reader, not bolted on later.

---

### Pitfall 2: Numeric Data Loaded as Strings

**What goes wrong:**
The 주문수량 (order quantity) column loads as string type instead of numeric, causing `groupby().sum()` to concatenate strings ("1" + "2" = "12") instead of adding numbers (1 + 2 = 3). The app shows wildly inflated or nonsensical totals with no error.

**Why it happens:**
Excel files may contain mixed types in a column (e.g., one cell has a number, another has text like "-" or a space). Pandas infers the column as object/string type. The `sum()` operation on strings concatenates silently -- no exception raised.

**How to avoid:**
- Explicitly convert quantity column: `pd.to_numeric(df['주문수량'], errors='coerce')` which turns non-numeric values to NaN
- After conversion, check for and report NaN count so the user knows how many rows had invalid quantities
- Add a basic sanity check: if any sum value exceeds a reasonable threshold, flag it

**Warning signs:**
- `df['주문수량'].dtype` is `object` instead of `int64` or `float64`
- Sum values are unreasonably large
- Result table shows quantities in the thousands when data has ~600 rows

**Phase to address:**
Phase 1 (Core Excel processing) -- type validation must happen during data loading, before any aggregation logic runs.

---

### Pitfall 3: openpyxl XML Attack Vulnerability (Billion Laughs / Quadratic Blowup)

**What goes wrong:**
A crafted .xlsx file (which is essentially a ZIP of XML files) can exploit XML parsing vulnerabilities. The "billion laughs" attack causes exponential memory consumption; quadratic blowup causes extreme CPU usage. Even for a personal tool, a corrupted or intentionally malicious file from an external source could crash the machine.

**Why it happens:**
openpyxl's documentation explicitly states it does NOT guard against these XML attacks by default. Developers assume .xlsx files are safe because they are "just spreadsheets."

**How to avoid:**
- Install `defusedxml` package: `pip install defusedxml`. openpyxl automatically uses it when available
- Set Flask's `MAX_CONTENT_LENGTH` to limit upload size (e.g., 16MB is more than enough for ~600 rows)

**Warning signs:**
- Processing hangs or memory spikes on a particular file
- `defusedxml` not in requirements.txt

**Phase to address:**
Phase 1 -- add `defusedxml` to dependencies from the start. It is a zero-config protection (just install it).

---

### Pitfall 4: Uploaded File Not Cleaned Up

**What goes wrong:**
Each file upload saves to disk (or stays in memory), but the temporary file is never deleted after processing. Over time (or with repeated testing), /tmp or the upload directory fills up. In development this seems harmless, but Flask's Werkzeug stores files under 500KB in memory; repeated uploads without cleanup cause gradual memory growth.

**Why it happens:**
Developers focus on the "happy path" of read-process-display and forget to clean up the uploaded file. Flask does not auto-delete uploaded files.

**How to avoid:**
- Process the file in-memory without saving to disk: read directly from `request.files['file'].stream` into pandas
- If saving to disk is needed, use a context manager or `try/finally` to ensure deletion
- For the in-memory approach: `df = pd.read_excel(file.stream, engine='openpyxl')`

**Warning signs:**
- Accumulating .xlsx files in upload directory
- Memory usage growing over time in dev server

**Phase to address:**
Phase 1 -- choose the in-memory processing approach from the start; never write uploaded files to disk for this use case.

---

### Pitfall 5: Groupby Silently Drops NaN Keys

**What goes wrong:**
Rows where 판매자 고유코드 is NaN/empty are silently excluded from `groupby()` results. The user sees a total that does not match the original data and has no idea rows were dropped.

**Why it happens:**
Pandas `groupby()` by default drops NaN group keys (changed in newer pandas versions but behavior varies). Empty cells in Excel load as NaN. Developers do not notice because the result "looks reasonable."

**How to avoid:**
- Use `groupby(dropna=False)` to include NaN groups, or
- Before groupby, fill empty codes with a placeholder: `df['판매자 고유코드'].fillna('(코드없음)')`
- Show a count of processed vs. original rows so the user can verify completeness

**Warning signs:**
- Sum of all group quantities does not match total rows in original file
- Some rows from the original file are "missing" in output

**Phase to address:**
Phase 1 -- handle NaN codes as part of the core aggregation logic.

---

### Pitfall 6: First-Row-Is-Not-Header Excel Files

**What goes wrong:**
The uploaded Excel file has metadata rows above the actual header (e.g., export date, report title). Pandas treats the first row as column headers, so all column names are wrong and every subsequent operation fails or produces garbage.

**Why it happens:**
Many Korean business software systems export Excel files with 1-3 metadata rows before the actual data header. Developers test with clean files and never encounter this.

**How to avoid:**
- Detect the header row dynamically: scan the first few rows for expected column names
- Provide a `header` parameter or auto-detect: look for a row containing known column names like '판매자 고유코드'
- At minimum, validate that the expected columns exist after loading and show a clear error if not

**Warning signs:**
- Column names look like data values rather than header labels
- `df.columns` contains dates or numeric values instead of field names

**Phase to address:**
Phase 1 -- header detection/validation should be part of file loading. Even a simple check ("do expected columns exist?") prevents silent failures.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcoded column names | Fast implementation | Breaks when Excel format changes | MVP only -- add column mapping config in v2 |
| No input validation on file | Less code | Crashes on unexpected files | Never -- always validate file type and structure |
| Processing in request thread | Simple architecture | Blocks server during processing | Acceptable for ~600 rows personal tool |
| No error message i18n | Faster dev | Mixed Korean/English errors | Acceptable for personal tool |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| pandas + openpyxl | Not specifying `engine='openpyxl'` explicitly | Always pass `engine='openpyxl'` to `pd.read_excel()` to avoid engine auto-detection issues |
| Flask file upload | Not setting `MAX_CONTENT_LENGTH` | Set `app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024` to reject oversized files before they consume memory |
| Flask + pandas | Saving file to disk then reading | Read directly from stream: `pd.read_excel(file.stream, engine='openpyxl')` |
| Werkzeug filename | Using user-provided filename directly | Always use `werkzeug.utils.secure_filename()` if saving to disk, or skip disk entirely |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading entire workbook with formatting | Slow load for large files | Use `read_only=True` in openpyxl or just use pandas (which handles this) | Files > 10K rows |
| Re-reading file multiple times | Slow response | Read once into DataFrame, process in memory | Even at 600 rows, noticeable if read 3+ times |
| Returning entire HTML table without pagination | Browser freezes | Not an issue at 600 rows; add pagination if data grows beyond 5K rows | 5K+ unique codes |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| No file extension validation | User uploads .py or .html file disguised as .xlsx | Check extension AND try to parse as xlsx; catch exceptions gracefully |
| Missing defusedxml | XML bomb in crafted .xlsx crashes server | `pip install defusedxml` -- openpyxl uses it automatically |
| Serving uploaded files back to user | Path traversal, XSS via filename | Never serve uploaded files; only serve processed results as HTML table |
| No upload size limit | DoS via huge file upload | Set `MAX_CONTENT_LENGTH` in Flask config |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Generic error on bad file ("500 Internal Server Error") | User has no idea what went wrong | Catch pandas/openpyxl exceptions and show specific Korean-language error: "엑셀 파일을 읽을 수 없습니다" with details |
| No loading indicator during upload | User clicks upload button multiple times | Show a spinner or "처리 중..." message; disable button after click |
| Results table has no sorting | Hard to find a specific seller code | Add client-side table sorting (e.g., DataTables.js or simple JS sort) |
| Column headers only in English | Confusing for Korean-speaking user | Use Korean column headers in the results table matching the source data |
| No way to download results | User has to manually copy data | Add "엑셀 다운로드" button to export the aggregated result |

## "Looks Done But Isn't" Checklist

- [ ] **File upload:** Handles non-.xlsx files gracefully with user-visible error (not a 500)
- [ ] **Column matching:** Strips whitespace from headers before matching
- [ ] **Numeric conversion:** Quantity column explicitly converted to numeric with error handling
- [ ] **Empty codes:** NaN/empty 판매자 고유코드 values are handled (not silently dropped)
- [ ] **Row count verification:** Output shows "N개 행 처리됨, M개 고유코드" so user can sanity-check
- [ ] **Error messages:** All error messages are in Korean, not English tracebacks
- [ ] **Header row:** Validates expected columns exist after loading; clear error if not
- [ ] **defusedxml:** Installed in requirements to protect against XML attacks

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Korean column name mismatch | LOW | Add `.str.strip()` and column validation; no architecture change needed |
| Numeric data as strings | LOW | Add `pd.to_numeric()` call; small code change |
| Missing defusedxml | LOW | `pip install defusedxml` and add to requirements.txt |
| File cleanup leak | LOW | Switch to stream-based reading; one-line change |
| Silent NaN dropping | LOW | Add `dropna=False` or `fillna()`; one-line change |
| Wrong header row | MEDIUM | Need to add header detection logic; may require testing with multiple file formats |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Korean column name fragility | Phase 1: Core processing | Test with file containing whitespace in headers |
| Numeric data as strings | Phase 1: Core processing | Assert `df['주문수량'].dtype` is numeric after loading |
| XML attack vulnerability | Phase 1: Setup/dependencies | Verify `defusedxml` in requirements.txt |
| File cleanup | Phase 1: Upload handling | Check no temp files remain after request completes |
| NaN group key dropping | Phase 1: Aggregation logic | Compare sum of group sizes with original row count |
| Wrong header row | Phase 1: File loading | Test with file that has metadata rows above header |
| Generic error messages | Phase 2: UX polish | Manual test: upload a .txt file, verify Korean error shown |
| No loading indicator | Phase 2: UX polish | Manual test: upload file, verify spinner appears |
| No result download | Phase 2: Feature enhancement | Manual test: verify download button produces valid .xlsx |

## Sources

- [openpyxl documentation -- security note on defusedxml](https://openpyxl.readthedocs.io/)
- [Flask file upload documentation](https://flask.palletsprojects.com/en/stable/patterns/fileuploads/)
- [Flask security considerations](https://flask.palletsprojects.com/en/stable/web-security/)
- [pandas read_excel documentation](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
- [pandas groupby documentation](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [Werkzeug large file upload memory issue](https://github.com/pallets/werkzeug/issues/2166)
- [HackerOne -- Secure File Uploads in Flask](https://www.hackerone.com/blog/secure-file-uploads-flask-filtering-and-validation-techniques)
- [pandas encoding issues with Excel](https://github.com/pandas-dev/pandas/issues/35753)

---
*Pitfalls research for: Python Excel sales data analysis web app*
*Researched: 2026-04-10*
