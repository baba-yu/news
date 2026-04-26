# Direction



Make a report include the following sections. Then, save it as `{current_dir}/future-prediction/future-prediction-yyyymmdd.md`. After creating the report, please validate it once to ensure there are no false or unsupported statements. DO NOT make a section to make sure the internal paths to .md.



IMORTANT: Only the URLs cited in report/news-yyyymmdd.md within the scope being summarized may be used for investigation. No additional research is required.



## Checking Predictions Against Reality



Read the **Future** sections of the `{current_dir}/report/*` from up to one week prior (excluding today), and tell me whether today’s report contains items related to those contents.

Use the following format:



* Table

   * Prediction (summary) | Prediction date | Related item(s) included in today’s report (YYYYMMDD) | Relevance (5-point scale) | Reference link(s)

* Summary of Findings



### Dormant pool re-check (in addition to the last-week scan)

The last-week scan only reaches predictions ≤ 7 days old. Older predictions may be dormant and live in the persistent dormant snapshot at `memory/dormant/dormant-*.md`. They must still be evaluated when today's news touches them — that is the "longshot revival" mechanism. The persistent snapshot is what makes daily evaluation cheap: instead of re-scanning all of project history, we read just one snapshot file plus today's news.

1. **Locate the latest dormant snapshot**: read the most recent `memory/dormant/dormant-*.md` (lexicographically last filename).

2. **Due-date inclusion**: for each row in the snapshot, if `Next ping ≤ today's date`, the prediction is **due**. Add a row to today's validation table for it regardless of news content. Honest relevance score (often 1 if no signal, that is the point of the periodic re-check).

3. **2-layer longshot detection** — separate from due-date inclusion. Both layers run; union the results.

   **Layer 1 — keyword scan (mechanical)**:
   - Tokenize today's `report/news-YYYYMMDD.md` body.
   - For each row in the snapshot, check whether **any term in the row's `Signals` column** appears as a substring or whole token in today's news.
   - On hit, record the matching signal as evidence.

   **Layer 2 — semantic scan (recall safety net)**:
   - Take today's `## Headlines` (5 bullets) plus all `### subheadings` from today's news (≤ 50 lines total).
   - Take all `Prediction (short)` lines from the snapshot (one line each).
   - In a single pass, identify dormant IDs whose short text plausibly relates to any of those headings/headlines.
   - On hit, record the related heading as evidence.

   **Union & dedupe by ID.** Each hit becomes a row in today's validation table:
   - Relevance score 1-5, evaluated honestly against the actual matching news content. Do not boost just because it was a longshot.
   - Reference link(s) drawn from the news section that triggered the match.
   - Mark the row's "Related item" cell with the source of revival (signal token or related heading) so the audit trail is explicit.

4. **No mutation of the dormant snapshot.** Daily flow only writes the validation table. The next Sunday's memory rolling job reads the past 7 days of validation files and removes any revived ID from the dormant pool automatically.



## Relation to My Own Predictions



In addition, I have the following two predictions. If anything close to my predictions is included, please let me know. The write-up can be in free form.



* Malicious local LLMs will begin to function like malware.

   * It is difficult to fully anticipate AI behavior itself. Local LLMs can exhibit internally driven multifunctional behaviors and may trigger breaches or data leakage. The conclusion will be that fundamental safeguards must be based on a zero-trust model, with properly designed multilayer authentication for data access, and this principle will be applied to AI as well. In practice, this means intentionally designing system paths in which AI alone cannot access data. Solutions that emphasize zero-trust-based access control for AI are likely to remain stable in both the short and long term.

   * Behavior specification for AI systems, including agents, will gain traction as a form of harness engineering. From a defense-in-depth perspective, it is effective, but it does not overturn the assumption that malicious activity can still bypass it. Solutions that claim to monitor and manage behavior will likely attract attention in only the short term. 



* A division of roles will emerge: AI used for advanced intellectual tasks will rely on cloud APIs, while routine daily operations will be handled by local LLMs. This shift will be unavoidable, driven by rising cloud usage costs.

   * Due to soaring electricity costs driven by energy issues and competition for increasingly scarce computational resources, the prices of all SaaS products that support AI functions will rise sharply. This will likely first appear in the form of changes to service delivery models and pricing structures.



* The use of reinforcement learning, or similar LLM-based approaches, to improve forecasting performance for real-world phenomena—like this scheduled task—will become widespread.
