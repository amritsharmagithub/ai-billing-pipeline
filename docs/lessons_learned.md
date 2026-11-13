# Lessons Learned

What I learned while building this project, grouped by topic. Each lesson links back to where it came from.

---

## Setup and environment

### 1. Python from python.org on a Mac needs a one-time certificate setup
The python.org installer does not set up trusted certificates automatically. Without them, Python's built-in downloader cannot connect to HTTPS sites like GitHub. The fix is to run `Install Certificates.command` once after installing. pip can still work without it because pip carries its own certificate list, which is why the problem only showed up partway through an install.
*Source: Issue 1 in the [mistakes log](mistakes_log.md).*

### 2. Confirm the cause before applying a fix
When the install failed, I checked how Python was installed before running anything to fix it. It took one extra command, and it meant I knew the fix was right instead of guessing. This is the same habit I used in settlement reconciliation: trace the break to its source before adjusting anything.
*Source: Issue 1 in the [mistakes log](mistakes_log.md).*

### 3. Fix security errors, don't switch off the check
The quick fix for SSL errors that you often find online is to disable certificate verification. That hides the problem instead of solving it. The real fix was to give Python the certificates it was missing.
*Source: Issue 1 in the [mistakes log](mistakes_log.md).*

### 4. A virtual environment has to be activated every time
Creating `.venv` does not turn it on. Every new Terminal window needs `source .venv/bin/activate`, and `(.venv)` in the prompt shows it is active.
*Source: build log, Session 1, Step 3.*

## Git and GitHub

### 5. A command can succeed and still have a problem
My first commit worked, but Git warned that it had guessed my name and email. If I had ignored the warning, none of my commits would have counted on my GitHub profile. I now read warnings even when a command succeeds, the same way a reconciliation can "balance" while still hiding a problem.
*Source: Issue 2 in the [mistakes log](mistakes_log.md).*

### 6. Fix commits before pushing, not after
`git commit --amend` can fix the last commit, but only safely before it is pushed. After pushing, changing a commit rewrites history that others may already have. Checking commits before pushing makes fixes cheap.
*Source: Issue 2 in the [mistakes log](mistakes_log.md).*

### 7. Keep a private email out of public commits
Commit emails are public. GitHub's noreply address links commits to my profile without showing my personal email.
*Source: build log, Session 1, Step 16.*

## Security

### 8. Revoke first, clean up second
When my token was exposed, the first step was revoking it on GitHub. Removing it from my files and screen mattered too, but only revoking made the leaked value useless. In payments work, this is the same order as with a compromised card: block it first, then investigate.
*Source: Issue 3 in the [mistakes log](mistakes_log.md).*

### 9. Read every command before running it, even from an AI
The command that leaked my token came from my AI assistant. It looked like my usual push command with one extra flag (`-u`), and I didn't ask what that flag did. AI help is useful, but I'm still responsible for what runs on my machine.
*Source: Issue 3 in the [mistakes log](mistakes_log.md).*

## From the videos

### 10. Validate structure at the door, but let business errors through on purpose
The MotherDuck video stops the pipeline when source rows don't match the expected schema. For billing, I split this in two: structural problems (wrong types, missing columns) stop the pipeline, but business errors (duplicate payments, oversized refunds) are let through so the dbt tests and reconciliation can find and report them. Deciding *where* each check belongs is part of the design.
*Source: [video notes](video_notes.md), Part 1.*

### 11. Reruns must never double-count
The video makes writes idempotent by deleting a period's rows before inserting them again. In billing, this is essential: rerunning a billing period must never create duplicate charges or payments.
*Source: [video notes](video_notes.md), Part 1.*

### 12. Parameterize instead of hardcoding
Passing the period and other settings in as parameters means the same pipeline can be rerun for any period without editing code. For my generated data, a fixed random seed also makes every run reproducible.
*Source: [video notes](video_notes.md), Part 1.*

## Building the data (Phase 2)

### 13. Reconcile in both directions
My invoice check started from invoices, which can never find a month with **no invoice at all**. Adding a check that starts from usage made it two-sided, the same as matching both the client side and the bank side in settlement work. A one-sided check misses whole categories of breaks.
*Source: build log, Phase 2, Step 18.*

### 14. Sanity-check totals before trusting them
Before accepting $183,711.96 as total billed, I estimated it from the plan prices (about $196,000 if every customer were active all 6 months, less late starts and cancellations, plus overage). The real number fit the estimate. A quick rough check catches numbers that are way off.
*Source: build log, Phase 2, Step 17.*

### 15. When a mistake happens twice, change the process
Creating files in the wrong folder happened twice, so I stopped fixing files one at a time and changed how I create them (with `touch` in Terminal). The same goes for pasting code: checking `wc -l` before running caught two more mix-ups right away.
*Source: Issues 4 and 5 in the [mistakes log](mistakes_log.md).*

### 16. Look for the business story in the numbers
My first query showed that 4 Enterprise customers (8%) bring in about 61% of monthly fees. That's revenue concentration, which a finance team would want to know about. The SQL was simple; the useful part was what the result means.
*Source: build log, Phase 2, Step 16.*

### 17. Test a process against known answers
The planted-errors answer key works like a test file in settlement work: before trusting a reconciliation, run it on data where you already know every break, and check that it finds all of them. My invoice control check went from 0 / 0 / 0 on clean data to 2 / 3 / 2 after planting, matching the answer key exactly.
*Source: build log, Phase 2, Steps 18 and 22.*

### 18. Know what to do about each break, not just find it
A $25 wire fee and an unexplained short payment both show up as "short," but they're fixed differently: write off the fee to bank fee expense, or follow up with the customer. Planning for that difference is the judgment a finance team expects from an analyst.
*Source: Decision 3 (update) in the [decisions log](decisions_log.md).*
