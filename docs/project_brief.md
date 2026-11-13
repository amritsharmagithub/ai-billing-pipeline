# Project Brief

I keep this file so I (or anyone helping me) can pick up the project with the same goals and rules. When I start a new chat with Claude or Claude Code, I paste this in first.

## Project
**AI Billing & Revenue Pipeline.** A data pipeline for a fictional AI API company, "Lumen AI": subscriptions with included credits, usage overage, invoices, payments, credits, and refunds, with deliberate data errors to find and reconcile.

**Stack:** Python 3.13, DuckDB, dbt (dbt-duckdb, v1 for now), Airflow, GitHub, Hex dashboard.

**Phases:**
1. Setup
2. Generate billing data (Python)
3. dbt models
4. dbt tests
5. Reconciliation report
6. Airflow
7. Dashboard
8. Publish (README, logs, dbt v2 upgrade)

## About me
- About 4 years as a Senior Settlement Analyst at Fiserv/First Data (Mastercard reconciliation).
- B.S. in Computer Science. Career break from 2022 to now.
- Target roles: billing, payments, and revenue data at AI companies.
- Previous projects: `sre-incident-agent`, `model-selection-eval`.

## Main goal of this project
Document the learning process for a hiring manager: what I built, how I built it, the mistakes I made, how I prevent them now, and what I learned, including from the videos.

## Rules
1. **Document as I go.** Commands, outputs, screenshots, and workflows, written down at each step, never from memory at the end.
2. **Log every real mistake** in this format: what happened, why, how I fixed it, how I prevent it now. Never invent mistakes.
3. **Write down lessons** after each step and video section, including what I did differently from the video for billing data.
4. **Always give credit:** in `CREDITS.md`, in the README, and in code comments when an idea came from somewhere else.
5. **Show the learning on GitHub:** the README opens with what I learned and links to all the logs.
6. **Checkpoint after every step:** screenshot (if needed) and output saved, before moving to the next step.
7. **I write the SQL and Python myself.** Claude explains, gives structure, and reviews. Claude Code is for debugging help only.
8. **One command at a time**, explained in simple, plain English.
9. **Writing style:** simple, plain, professional English that shows I'm learning. Not flashy.
10. **Security:** never put tokens or keys in chat or in files. Push to GitHub with `read -s TOKEN`, then `unset TOKEN`.

## Daily start
```bash
cd ~/ai-billing-pipeline
source .venv/bin/activate
```

## Docs
- `docs/build_log.md`: what I did each session
- `docs/mistakes_log.md`: real mistakes and how I prevent them
- `docs/lessons_learned.md`: what I learned, by topic
- `docs/decisions_log.md`: choices and why I made them
- `docs/video_notes.md`: notes from the MotherDuck videos
- `docs/screenshots/`: named like `phase1_01_description.png`
- `CREDITS.md`: every source used
