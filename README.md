# Beyond Plausible Answers

A reproducible audit of 11 graph 3-coloring experiments comparing responses attributed to ChatGPT and Claude. Prepared as a research portfolio project, 15 October 2026.

**Status:** Mathematical results reproduced against supplied graph lists. Historical records are partly reconstructed; this is a retrospective case study, not a controlled model benchmark.

Excluding contaminated pilot Test 1, ChatGPT answers are mathematically correct on 8/10 graphs and Claude answers on 10/10. ChatGPT incorrectly returns UNSAT on Tests 10 and 11. Reported format compliance is 10/10 versus 8/10, but most full response texts are unavailable for independent formatting inspection.

## Why this matters

**An AI answer can follow every formatting instruction and still be mathematically wrong.** In Test 11, a pasted response attributed to ChatGPT follows the required JSON format but declares that no valid coloring exists. An independently checked coloring proves that conclusion incorrect. Test 10 provides a second false UNSAT case in the supplied records, although its ChatGPT response is reconstructed.

Graph coloring makes this distinction precisely testable: a proposed coloring can be checked against every edge, and complete search can determine whether a solution exists. The contribution is a reproducible evaluation process that separates formatting from correctness, excludes a contaminated pilot, and makes evidence limitations explicit. The 8/10 versus 10/10 comparison describes these records; it does not establish a general model ranking.

The connection to AI safety is **evaluation reliability**: independent checks can expose errors that format checks alone miss. This small case study demonstrates verification practice; it does not directly measure alignment or real-world safety performance.

## Reproduce

Requires Python 3.10 or later; no third-party packages, network, API keys or model calls.

```sh
python3 verify.py
python3 -m unittest -v
```

Run these commands from this project directory. The verifier writes `results/audit.json` and `results/audit.csv` deterministically, including a SHA-256 fingerprint of the input dataset. Custom paths are supported:

```sh
python3 verify.py --data data/experiments.json --output results/audit.json
```

The test suite independently enumerates assignments for Tests 1–9, checks SAT certificates for Tests 10–11, checks the historical Test 10 witness, and exercises format parsing, invalid assignments, known SAT/UNSAT graphs and pilot exclusion. It does not contact either model or reproduce their original sampling.

## Files

- `data/experiments.json`: all 11 graph edge lists, recorded payloads, available raw pasted responses, provenance, reported format outcomes and pilot exclusion.
- `data/source-reader-response.json`: curated conversation-reader research excerpts, including original Test 11 graph prompt, both pasted responses and Claude's pasted Test 10 response.
- `data/legacy-claims.json`: previous assistant claims, retained as claims rather than ground truth.
- `verify.py`: deterministic complete backtracking solver, independent constraint checks, response parser and metric calculations.
- `test_verify.py`: independent enumeration and regression checks.
- `results/audit.json`: per-response results, SAT witnesses, search counts and metrics with explicit denominators.
- `results/audit.csv`: readable per-test results from the audited run.
- `REPORT.md`: concise research report, evidence qualifications and follow-up design.

## Dataset conventions

Vertices are integers `0` through `n-1`; colors are integers 0, 1 and 2. Edges are undirected. Preserve listed edge orientation and order; the audit also counts distinct undirected pairs. `null` means unknown or not applicable, never failure or zero.

`raw` is text directly recovered from the conversation reader; even this is a user-pasted answer, not an authenticated model trace. `payload_json` is a JSON payload serialized from the user's reconstruction. It is not a verbatim full model response. `format_reported` records the reconstruction's format judgment; it is not inferred from the serialized payload. `prompt_raw` preserves the full available Test 11 prompt announcement; earlier full prompts remain unavailable.

Every reconstructed Test 1–10 graph and payload comes from the user's follow-up in this project chat dated 2026-10-15. Adjacent source labels supply model attribution. Tests 2–3 reportedly contained prose in Claude's answers; that prose is not preserved and is not fabricated. Model versions, settings and original timestamps are unknown.

## Solver identity

The default verifier is **exhaustive Python backtracking with DSATUR vertex ordering**, not PySAT. UNSAT means this terminating search exhausted all branches; SAT includes a directly checked witness. No external SAT solver ran, and no proof log was produced. See the report for a proposed CNF/PySAT cross-check, clearly separated from executed work.

## Updating records

Replace reconstructed fields only when better source evidence is available, preserve the previous provenance and document changes. Do not store a standardized JSON payload in `raw`. Re-run verification and tests after changes, and revise the report/summary if results change. The report is an interpretation of the fingerprinted audited dataset, not an automatic template.

This project does not establish general model superiority or safety performance.

## Publication notes

Private chat identifiers were replaced with consistent source labels. The evidence export contains relevant research excerpts only; original local files were preserved. Dataset results are regenerated from the publication copy, so its fingerprint differs from the original export.

This portfolio was prepared with AI assistance, including verification code and documentation. The executable checks and evidence qualifications are provided for independent review.

No license is granted in this initial publication; contact the repository owner about reuse.
