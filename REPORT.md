# Beyond Plausible Answers: Independently Checking LLM Graph Coloring

**Retrospective research case study · 15 October 2026**

## Question and finding

Can a model satisfy a strict response format while giving a mathematically wrong answer to a small, exactly verifiable constraint problem?

Yes, in the recovered records: on Tests 10 and 11, answers attributed to ChatGPT declare UNSAT for graphs with independently verified 3-colorings. Answers attributed to Claude provide valid colorings for both. Both Test 11 pasted responses satisfy the JSON format requirement. This supports a separation between format compliance and mathematical correctness in these cases; it does not establish a general ranking of the models.

## Evidence and provenance

The sources are research excerpts from a prior project conversation and a user-supplied reconstruction of Tests 1–10. The conversation reader exposed only five recent turns, with no continuation cursor. Relevant research excerpts are retained in the dataset directory; unrelated conversation content, private identifiers and session metadata were removed for publication. Source labels preserve links between the dataset and excerpts.

All 11 exact edge lists **as supplied** are retained. Tests 1–10 come from the reconstruction, which explicitly standardizes some original instructions. Test 11's graph comes directly from the retained prompt announcement. Only Claude Test 10 and both Test 11 responses are available as raw pasted text. Earlier responses are reconstructed JSON payloads; original prose and complete prompts are unavailable. “ChatGPT” and “Claude” are historical labels supplied by the user and adjacent assistant messages, not authenticated model identities.

The audit validates the supplied graphs and payloads. It cannot prove that reconstructed records exactly match original sessions.

## Methodology

The task is to determine whether each undirected graph admits a proper coloring with colors `{0,1,2}`. A SAT answer must assign every vertex exactly one permitted integer color and satisfy every edge. An UNSAT answer must have an empty assignment.

The verifier validates graph endpoints, counts listed and unique undirected edges, and independently solves each graph using complete deterministic Python backtracking. DSATUR chooses an uncolored vertex with the greatest number of distinct neighbor colors, then degree and vertex ID break ties. Each permitted color is explored; a failed branch restores its assignment. There is no timeout or search cutoff. An UNSAT result follows exhaustion of the search tree, not a model assertion. Search-node counts are implementation diagnostics, not counts of all possible assignments or evidence of model difficulty.

Every returned SAT witness and model SAT assignment is checked directly against every edge. An independent `itertools.product` enumeration cross-checks Tests 1–9, fixing vertex 0 to color 0 by color-permutation symmetry. Tests 10–11 have directly checked SAT certificates, which suffice to establish satisfiability without exhausting all assignments. The historical Test 10 witness also passes the independent edge check.

The parser distinguishes JSON-only syntax, the required response schema, correct classification, and full mathematical correctness. It rejects duplicate keys, nonstandard constants and Boolean colors. A narrow recovery rule allows a single fenced JSON block to be scored mathematically while failing JSON-only compliance; arbitrary explanatory text is not automatically stripped. Reconstructed payloads can be scored mathematically, but cannot establish raw format compliance.

Test 1 is excluded from all primary aggregate metrics: the reconstruction says its prompt disclosed the exact answer, which both models reproduced. It remains in the dataset for transparency. Tests 2–11 each receive equal weight. No graph is removed based on the audit outcome.

## Recomputed results

| Test | Vertices | Edges | Verified truth | ChatGPT mathematical result | Claude mathematical result |
|---|---:|---:|---|---|---|
| 1 (excluded pilot) | 5 | 6 | SAT | Pass | Pass |
| 2 | 6 | 9 | SAT | Pass | Pass |
| 3 | 7 | 12 | UNSAT | Pass | Pass |
| 4 | 8 | 14 | SAT | Pass | Pass |
| 5 | 9 | 18 | SAT | Pass | Pass |
| 6 | 10 | 24 | UNSAT | Pass | Pass |
| 7 | 11 | 25 | UNSAT | Pass | Pass |
| 8 | 12 | 30 | SAT | Pass | Pass |
| 9 | 11 | 29 | UNSAT | Pass | Pass |
| 10 | 15 | 54 | SAT | Fail: false UNSAT | Pass |
| 11 | 16 | 58 | SAT | Fail: false UNSAT | Pass |

All listed pairs are distinct when treated as undirected edges. All supplied SAT model assignments are complete, use permitted colors and have zero edge violations. Both models classify all four UNSAT benchmark graphs correctly. Among the six SAT benchmark graphs, ChatGPT is correct on 4/6 and Claude on 6/6.

| Metric, excluding Test 1 | ChatGPT | Claude | Evidence qualification |
|---|---:|---:|---|
| Correct SAT/UNSAT classification | 8/10 (80%) | 10/10 (100%) | Recomputed from supplied inputs |
| Full mathematical correctness | 8/10 (80%) | 10/10 (100%) | Recomputed; UNSAT via complete search |
| Format compliance including reported history | 10/10 (100%) | 8/10 (80%) | Partly reported, not fully independently observed |
| Format compliance directly inspectable | 1/1 | 2/2 | Only raw pasted responses; selective subset |

Reported Claude format failures are Tests 2 and 3, where explanatory prose reportedly preceded JSON. The actual prose is missing. Therefore 8/10 is a reconstruction-supported historical figure, not a fully rerun raw-text formatting measurement. The observed 1/1 and 2/2 figures describe coverage, not estimates of model-wide compliance.

## Corrections and claim reconciliation

The audit confirms, rather than assumes, the historical 8/10 versus 10/10 mathematical totals and both false UNSAT cases. Test 5 has 18 edges; the previously mentioned 19-edge count is incorrect. Test 10 contains 54 listed and unique undirected edges, so the earlier 54-edge claim is supported. Test 11 contains 58. Tests 6, 7 and 9 are independently re-established as UNSAT; earlier assistant claims of having run Python were not accepted as execution evidence.

The project title is changed from “SAT-Based Verification” to “Independently Checking”: the executed pipeline uses backtracking and direct constraint checks. Describing it as a PySAT experiment would be inaccurate. “Advanced” difficulty and a general tendency to fail on dense graphs are not established by these records.

## Backtracking versus PySAT

No PySAT library was installed or executed. A future independent SAT-solver implementation could introduce variables `x(v,c)`, add one clause requiring at least one color per vertex, three pairwise clauses enforcing at most one, and three clauses per edge forbidding equal endpoint colors. For these loop-free graphs, this gives `3n` variables and `4n + 3m` clauses before simplification. A PySAT wrapper could submit this CNF to a specified solver backend, decode SAT models and compare answers. That would be SAT-solver verification, distinct from this project's Python search. Stronger independent assurance of UNSAT could additionally use proof-producing solvers and checked proof logs; those are future work, not completed deliverables.

## Limitations and next experiment

This is a small, adaptive convenience sample with one recorded response per model per graph. Test 11 was selected after the Test 10 failure. Several graphs share substantial structure, so results are not independent draws. Prompts reportedly used fresh conversations, but actual session isolation, tools, model versions, sampling parameters, retries and hidden selection decisions are unverified. Reconstruction may introduce transcription error; raw provider logs would improve confidence. A correct UNSAT declaration alone does not reveal a model's reasoning, and format success says nothing about reasoning fidelity.

There is no basis for causal claims about graph density, broad model superiority or current model capabilities. A stronger follow-up would preregister graph generation and metrics, save seeds and full prompts, balance SAT/UNSAT instances, randomize vertex labels and response order, log exact model identifiers/settings and tools, run repeated trials, and use independent backtracking and SAT implementations. Keep mathematical validity, classification, formatting, latency and resource use separate. Do not infer safety or alignment performance from this narrow task alone.

## Reproduction and portfolio framing

Run `python3 verify.py` and `python3 -m unittest -v` from the project directory with Python 3.10+. No network or external packages are needed. Inspect `results/audit.json` for witnesses, violations, search counts, per-metric denominators and the dataset SHA-256; compare the per-test CSV with this table.

The defensible portfolio contribution is an auditable evaluation pipeline, careful evidence provenance, contamination handling and explicit reconciliation of historical claims. It demonstrates verification practice on a bounded case study, rather than claiming a new general benchmark result or an established failure mechanism.
