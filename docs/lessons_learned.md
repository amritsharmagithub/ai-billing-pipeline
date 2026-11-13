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
