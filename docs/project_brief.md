# Project Brief

I keep this file so I (or anyone helping me) can pick up the project with the same goals and rules. When I start a new chat with Claude or Claude Code, I paste this in first.

## Project
**AI Billing & Revenue Pipeline.** A data pipeline for a fictional AI API company, "Lumen AI": subscriptions with included credits, usage overage, invoices, payments, credits, and refunds, with deliberate data errors to find and reconcile.

**Goal in one sentence:** Show that I can take messy billing data and turn it into revenue numbers people can trust: model it, test it, reconcile it, and explain the breaks.

**Target roles:** analytics, finance, and billing roles (possibly data science). Not data engineering.

**Stack:** Python 3.13, DuckDB, dbt (dbt-duckdb, v1), GitHub, dashboard tool to be decided in Phase 6.

**Phases** (see Decision 2):
1. Setup (done)
2. Generate billing data (Python)
3. dbt models
4. dbt tests
5. Reconciliation report (the centerpiece)
6. Dashboard
7. Publish (README and docs)

**Optional, after the core is finished:** a short analysis notebook (data science angle), dbt v2 upgrade. Airflow is dropped.

## About me
- About 4 years as a Senior Settlement Analyst at Fiserv/First Data (Mastercard reconciliation).
- B.S. in Computer Science. Career break from 2022 to now.
- Target roles: analytics, finance, and billing roles at AI companies (possibly data science).
- Previous projects: `sre-incident-agent`, `model-selection-eval`.

## Main goal of this project
Document the learning process for a hiring manager: what I built, how I built it, the mistakes I made, how I prevent them now, and what I learned, including from the videos.

## Rules
1. **Document as I go, at the right level.** Full detail for mistakes, decisions, and lessons. Short entries for routine steps. Screenshots for results only. Never written from memory at the end.
2. **Log every real mistake** in this format: what happened, why, how I fixed it, how I prevent it now. Never invent mistakes.
3. **Write down lessons** after each step and video section, including what I did differently from the video for billing data.
4. **Always give credit:** in `CREDITS.md`, in the README, and in code comments when an idea came from somewhere else.
5. **Show the learning on GitHub:** the README opens with what I learned and links to all the logs.
6. **Checkpoint after every step:** screenshot (if needed) and output saved, before moving to the next step.
7. **AI-assisted code, my understanding.** Claude may write or suggest code. I review it, run it, and make sure I can explain every line, because interviewers will ask. I credit AI help honestly.
8. **One step at a time**, explained in simple, plain English. For code: Claude first asks me to type it. If I reply "list below", Claude writes the full code for me to copy.
9. **Writing style:** simple, plain, professional English that shows I'm learning. Not flashy.
10. **Security:** never put tokens or keys in chat or in files. Push to GitHub with `read -s TOKEN`, then `unset TOKEN`.

## Daily start
```bash
cd ~/ai-billing-pipeline
source .venv/bin/activate
```

## Safe push routine
Run one line at a time. Never add `-u` to a push that has a token in the URL (see Issue 3 in the mistakes log).

```bash
read -s TOKEN
git push https://amritsharmagithub:${TOKEN}@github.com/amritsharmagithub/ai-billing-pipeline.git main
unset TOKEN && echo "TOKEN is now: [${TOKEN}]" && grep -c "ghp_" .git/config
git fetch origin && git status -sb
```
- Expected after line 3: `TOKEN is now: []` and `0`.
- Line 4 syncs my local view of GitHub. Expected: `## main...origin/main` with nothing after it.
- Before pasting any output anywhere, check it for anything starting with `ghp_`.

## Docs
- `docs/build_log.md`: what I did each session
- `docs/mistakes_log.md`: real mistakes and how I prevent them
- `docs/lessons_learned.md`: what I learned, by topic
- `docs/decisions_log.md`: choices and why I made them
- `docs/video_notes.md`: notes from the MotherDuck videos
- `docs/screenshots/`: named like `phase1_01_description.png`
- `CREDITS.md`: every source used
