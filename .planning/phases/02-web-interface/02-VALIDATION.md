---
phase: 2
slug: web-interface
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-10
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | None — pytest auto-discovers from project root |
| **Quick run command** | `python -m pytest tests/test_app.py -x -q` |
| **Full suite command** | `python -m pytest tests/ -x -q` |
| **Estimated runtime** | ~3 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_app.py -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -x -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | UPLD-01 | T-02-01 | File extension check | integration | `python -m pytest tests/test_app.py::test_upload_valid_xlsx -x` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | UPLD-02 | — | N/A (JS behavior) | manual-only | Manual browser test | N/A | ⬜ pending |
| 02-01-03 | 01 | 1 | UPLD-03 | T-02-01 | Korean error messages | integration | `python -m pytest tests/test_app.py::TestErrorHandling -x` | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 1 | DISP-01 | — | N/A | integration | `python -m pytest tests/test_app.py::test_results_table -x` | ❌ W0 | ⬜ pending |
| 02-01-05 | 01 | 1 | DISP-03 | — | N/A | integration | `python -m pytest tests/test_app.py::test_summary_display -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_app.py` — Flask test client setup + stubs for UPLD-01, UPLD-03, DISP-01, DISP-03
- [ ] Flask test client fixture (in test_app.py or conftest.py)

*Existing infrastructure (conftest.py, test_processor.py) covers Phase 1. Phase 2 needs test_app.py.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Drag-and-drop file upload | UPLD-02 | JavaScript DOM event handling, not testable via Flask test client | 1. Open browser to localhost:5000 2. Drag .xlsx file onto page 3. Verify file uploads and results display |
| Zebra striping on table rows | D-05 | Visual CSS rendering | 1. Upload valid file 2. Verify alternating row colors in browser |
| Loading button feedback | D-04 | JavaScript UI state change | 1. Select file 2. Verify button text changes to "처리 중..." |

*All other phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
