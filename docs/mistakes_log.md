# Mistakes and Lessons

The mistakes that taught me something while building this project: what happened, why, how I fixed it, and what I do now.

---

## Mistake 1: I planned too much at the start
**Date:** November 13, 2026 · **Phase:** Before Phase 2

**What happened:** My first plan had 8 phases, including Airflow for scheduling. After setup, I checked the plan against the jobs I'm targeting (analytics, finance, and billing roles) and saw it didn't fit well.

**Why:** I planned around tools instead of starting from the goal. Airflow is mostly a data engineering skill, and it would have taken time away from what matters most for my target roles: SQL, data quality, and reconciliation.

**How I fixed it:** I wrote the project goal in one sentence, removed Airflow, and made the dbt v2 upgrade optional. The reconciliation report became the centerpiece. (See Decision 2.)

**What I do now:** Before starting a project, I write the goal in one sentence and check each planned step against it.

---

## Mistake 2: I trusted the output without checking what was actually saved
**Date:** November 13, 2026 · **Phase:** 2 (Generate billing data)

**What happened:** A few times while building the data generator, a run showed old results, or said a file didn't exist. What I saw in my editor was not what was saved on disk. Once I had pasted an older version of the code, and twice a new file was saved in the wrong folder.

**Why:** I assumed the file matched what I expected and ran it without checking.

**How I fixed it:** I checked the actual files instead of running them again: `wc -l` to compare line counts, and `find` to locate the misplaced files. Then I replaced or moved them.

**What I do now:** I check a file before running it (line count, or a line I expect to see), and I create new files from Terminal with `touch` so they land in the right folder. When a mistake happens twice, I change the process, not just the file. It's the same habit as reconciliation: check the actual record, not what I think it says.

![Finding a misplaced file, moving it, and re-running the check](screenshots/phase2_04_invoice_checks_clean.png)
