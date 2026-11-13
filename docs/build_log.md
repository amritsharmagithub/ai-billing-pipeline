# Build Log

This log records what I did in each session: the commands I ran, the output I got, and short notes. I wrote it as I went, not from memory at the end.

---

## Session 1 — Friday, November 13, 2026

**Phase:** 1 — Setup
**Goal for today:** Create the project folder, set up a Python 3.13 virtual environment, install dbt-duckdb, and set up the docs folders.
**Learning source:** MotherDuck, "DuckDB & dbt End-to-End Data Engineering Project" by Mehdi Ouazza, Part 1 (https://motherduck.com/videos/90/duckdb-python-end-to-end-data-engineering-project-13)

### Step 1: Create the project folder

**What I did:** Created the project folder in my home directory and moved into it.

```bash
$ mkdir ~/ai-billing-pipeline && cd ~/ai-billing-pipeline && pwd
/Users/amritsharma/ai-billing-pipeline
```

**Notes:**
- `mkdir` creates the folder, `cd` moves into it, and `pwd` prints the current folder to confirm it worked.
- `&&` runs the next command only if the one before it succeeded.
- Result: worked on the first try.

### Step 2: Create a Python 3.13 virtual environment

**What I did:** Created a virtual environment called `.venv` inside the project folder.

```bash
$ python3.13 -m venv .venv && ls -a
.	..	.venv
```

**Notes:**
- A virtual environment is a private copy of Python for one project. Packages installed in it stay separate from the rest of my Mac and from my other projects.
- I used `python3.13` on purpose. My Mac's system Python is 3.9, which is too old for current dbt versions.
- The dot in `.venv` makes the folder hidden, which is a common convention. `ls -a` shows hidden items, so I could confirm it was created.
- Result: worked on the first try.

### Step 3: Activate the virtual environment

**What I did:** Activated the environment and checked which Python the terminal was using.

```bash
$ source .venv/bin/activate && which python && python --version
/Users/amritsharma/ai-billing-pipeline/.venv/bin/python
Python 3.13.17
(.venv) $
```

**Notes:**
- Creating a virtual environment does not turn it on. `source .venv/bin/activate` makes this terminal use the project's Python.
- `(.venv)` at the start of the prompt shows the environment is active.
- `which python` pointed inside my project folder, which confirmed I was using the project's Python and not the system one.
- Habit to remember: every new Terminal window needs `cd ~/ai-billing-pipeline` and `source .venv/bin/activate` before I work on the project.
- Result: worked on the first try.

### Step 4: Upgrade pip and install dbt-duckdb (first attempt failed)

**What I did:** Upgraded pip, then tried to install dbt-duckdb.

```bash
(.venv) $ pip install --upgrade pip && pip install dbt-duckdb
...
Successfully installed pip-26.3
Collecting dbt-duckdb
  Downloading dbt_duckdb-1.11.1-py3-none-any.whl.metadata (48 kB)
...
Collecting dbt-core-experimental-parser<3,>=2.0.11 (from dbt-core>=1.8.0->dbt-duckdb)
  Downloading dbt_core_experimental_parser-2.0.11.tar.gz (4.7 kB)
  ...
  Preparing metadata (pyproject.toml) ... error
  ...
  RuntimeError: failed to download https://github.com/dbt-labs/dbt/releases/download/v2.0.11/dbt_core_experimental_parser-2.0.11-py3-none-macosx_10_12_x86_64.whl: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1032)>
...
error: metadata-generation-failed
× Encountered error while generating package metadata.
╰─> dbt-core-experimental-parser
```

**Notes:**
- The pip upgrade worked (26.2.2 → 26.3).
- The dbt-duckdb install failed. One of dbt-core's dependencies, `dbt-core-experimental-parser`, tries to download an extra file from GitHub while it installs, and that download failed with `CERTIFICATE_VERIFY_FAILED`.
- Status: investigating. See the mistakes log for the root cause and fix.

![SSL certificate error during dbt-duckdb install](screenshots/phase1_01_ssl_certificate_error.png)

### Step 5: Confirm the cause before fixing it

**What I did:** Checked whether my Python 3.13 came from the python.org installer. That installer does not set up trusted certificates automatically. It leaves a one-time script to do it.

```bash
(.venv) $ ls "/Applications/Python 3.13/"
IDLE.app			Install Certificates.command	Python Documentation.html	ReadMe.rtf
Icon?				License.rtf			Python Launcher.app		Update Shell Profile.command
```

**Notes:**
- The folder exists and contains `Install Certificates.command`. That confirms Python 3.13 was installed from python.org, and the certificate setup script was never run.
- I confirmed the cause before changing anything, the same way I would trace a break in reconciliation before adjusting it.
- I chose not to use the common shortcut of turning off certificate checks (for example, `--trusted-host`), because that removes a security check instead of fixing the cause.

### Step 6: Run the one-time certificate setup

**What I did:** Ran the certificate setup script that the python.org installer provides.

```bash
(.venv) $ "/Applications/Python 3.13/Install Certificates.command"
 -- pip install --upgrade certifi
Collecting certifi
  Using cached certifi-2026.10.23-py3-none-any.whl.metadata (2.5 kB)
Using cached certifi-2026.10.23-py3-none-any.whl (135 kB)
Installing collected packages: certifi
Successfully installed certifi-2026.10.23
 -- removing any existing file or link
 -- creating symlink to certifi certificate bundle
 -- setting permissions
 -- update complete
```

**Notes:**
- The script installed `certifi`, a list of trusted certificate authorities maintained from Mozilla's list, and pointed Python 3.13's SSL settings at it.
- This fixes the main Python 3.13 on my Mac. My `.venv` is built on it, so the project gets the fix too.
- This is a one-time setup per Python version. Any future project on Python 3.13 will not hit this error.

![Confirming the python.org install and running Install Certificates](screenshots/phase1_02_install_certificates_fix.png)

### Step 7: Retry the dbt-duckdb install (worked)

**What I did:** Ran the same install again after the certificate fix.

```bash
(.venv) $ pip install dbt-duckdb
...
Successfully installed Babel-2.18.0 MarkupSafe-3.0.4 agate-1.9.1 ... dbt-adapters-1.24.5 dbt-common-1.39.0 dbt-core-1.12.7 dbt-core-experimental-parser-2.0.11 dbt-duckdb-1.11.1 ... duckdb-2.0.0 ... zipp-4.1.2
```

**Notes:**
- No errors this time. `dbt-core-experimental-parser-2.0.11`, the package that failed before, installed successfully. That confirms the certificate fix solved the problem.
- Main versions installed:
  - `dbt-core` 1.12.7: the dbt tool itself
  - `dbt-duckdb` 1.11.1: the adapter that connects dbt to DuckDB
  - `duckdb` 2.0.0: the database
- About 60 packages were installed in total. Most are supporting libraries that dbt needs.
- Time from first error to working install: about 13 minutes.

### Step 8: Confirm dbt works

**What I did:** Checked the dbt version and which database adapters dbt can see.

```bash
(.venv) $ dbt --version
Core:
  - installed: 1.12.7
  - latest:    1.12.7 - Up to date!

Plugins:
  - duckdb: 1.11.1 - Up to date!

14:20:10  dbt v2 is available, and is the default for new installations. This is dbt Core v1.
          New project - install v2: https://docs.getdbt.com/docs/local/install-dbt?utm_source=dbt-cli
          Existing v1 project - upgrade guide: https://docs.getdbt.com/docs/dbt-versions/dbt-upgrade/upgrading-to-v2?utm_source=dbt-cli
```

**Notes:**
- dbt Core 1.12.7 is installed, and the DuckDB adapter (1.11.1) shows under Plugins. Setup works.
- dbt also printed a notice that **dbt v2** is now the default for new installations. I stopped to look into this before going further, because it affects which version the whole project is built on. See the decisions log.

![dbt --version output with the v2 notice](screenshots/phase1_03_dbt_version.png)

**Decision:** Build on dbt v1 now and upgrade to v2 in Phase 8. See Decision 1 in the [decisions log](decisions_log.md).

### Step 9: Create the docs folders

**What I did:** Created a `docs` folder for the project logs, with a `screenshots` folder inside it.

```bash
(.venv) $ mkdir -p docs/screenshots && ls docs
screenshots
```

**Notes:**
- `-p` creates both folders in one command and does not fail if they already exist.
- I set up the docs folders during setup, so the logs grow with the project instead of being written at the end.

### Step 10: Save exact package versions

**What I did:** Saved every installed package and its exact version to `requirements.txt`, then checked the three main ones.

```bash
(.venv) $ pip freeze > requirements.txt && grep -E "^(dbt-core|dbt-duckdb|duckdb)==" requirements.txt
dbt-core==1.12.7
dbt-duckdb==1.11.1
duckdb==2.0.0
```

**Notes:**
- `pip freeze` lists installed packages with exact versions, and `>` saves the list to a file.
- Anyone who clones the repo can run `pip install -r requirements.txt` to get the same versions I used.
- This also records my "before" versions for the dbt v2 upgrade planned for Phase 8.

### Step 11: Create a .gitignore file

**What I did:** Created a `.gitignore` file listing the files Git should never upload to GitHub.

```bash
(.venv) $ printf ".venv/\n__pycache__/\n*.duckdb\n*.duckdb.wal\ntarget/\nlogs/\ndbt_packages/\n.env\n.DS_Store\n" > .gitignore && cat .gitignore
.venv/
__pycache__/
*.duckdb
*.duckdb.wal
target/
logs/
dbt_packages/
.env
.DS_Store
```

**Notes:**
- `.venv/`: my virtual environment. Others rebuild it from `requirements.txt`.
- `__pycache__/`, `target/`, `logs/`, `dbt_packages/`: files created automatically by Python and dbt.
- `*.duckdb`, `*.duckdb.wal`: the database file. The code rebuilds it, so the code is what gets saved.
- `.env`: added before any secrets exist, as a safety net so keys or tokens can never be committed by accident.
- `.DS_Store`: hidden macOS files that are not part of the project.

### Step 12: Start tracking the project with Git

**What I did:** Turned the folder into a Git repository and checked what Git can see.

```bash
(.venv) $ git init -b main && git status
Initialized empty Git repository in /Users/amritsharma/ai-billing-pipeline/.git/
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.gitignore
	requirements.txt

nothing added to commit but untracked files present (use "git add" to track)
```

**Notes:**
- `-b main` names the main branch `main`, which matches GitHub's default.
- `.venv/` does not appear in the untracked list, which confirms `.gitignore` is working.
- `docs/` does not appear yet because Git ignores empty folders.
- I set up Git at the start of the project, so the commit history shows the project growing phase by phase.

### Step 13: Add the docs to the project

**What I did:** Unpacked the docs I had been keeping during the session (logs, credits, screenshots) into the project folder.

```bash
(.venv) $ unzip -o ~/Downloads/phase1_docs.zip -d ~/ai-billing-pipeline && git status
Archive:  /Users/amritsharma/Downloads/phase1_docs.zip
  inflating: /Users/amritsharma/ai-billing-pipeline/CREDITS.md
  inflating: /Users/amritsharma/ai-billing-pipeline/docs/build_log.md
  ...
  inflating: /Users/amritsharma/ai-billing-pipeline/docs/screenshots/phase1_03_dbt_version.png
On branch main

No commits yet

Untracked files:
	.gitignore
	CREDITS.md
	docs/
	requirements.txt
```

**Notes:**
- The first try failed with `cannot find or open` because I had not downloaded the zip yet. After downloading it, the command worked.
- `-o` overwrites older copies without asking, so I can reuse the same command at the end of each session.

### Step 14: Stage files and review before committing

**What I did:** Staged all files and checked the list before saving anything.

```bash
(.venv) $ git add . && git status
Changes to be committed:
	new file:   .gitignore
	new file:   CREDITS.md
	new file:   docs/build_log.md
	new file:   docs/decisions_log.md
	new file:   docs/lessons_learned.md
	new file:   docs/mistakes_log.md
	new file:   docs/project_brief.md
	new file:   docs/screenshots/phase1_01_ssl_certificate_error.png
	new file:   docs/screenshots/phase1_02_install_certificates_fix.png
	new file:   docs/screenshots/phase1_03_dbt_version.png
	new file:   requirements.txt
```

**Notes:**
- 11 files staged, with nothing from `.venv/` and no secrets.
- I review the staged list before every commit. It's the last chance to catch something that should not go to GitHub, like checking a batch before releasing a settlement file.

### Step 15: First commit (with a warning)

**What I did:** Made the first commit and checked the history.

```bash
(.venv) $ git commit -m "Phase 1: project setup, Python 3.13 venv, dbt-duckdb, and docs" && git log --oneline
[main (root-commit) 4890308] Phase 1: project setup, Python 3.13 venv, dbt-duckdb, and docs
 Committer: Amrit Sharma <amritsharma@Amrits-MacBook-Pro.local>
Your name and email address were configured automatically based
on your username and hostname. Please check that they are accurate.
...
 11 files changed, 511 insertions(+)
...
4890308 (HEAD -> main) Phase 1: project setup, Python 3.13 venv, dbt-duckdb, and docs
```

**Notes:**
- The commit worked, but Git had never been told my name and email on this Mac, so it guessed `amritsharma@Amrits-MacBook-Pro.local`.
- GitHub links commits to a profile by email. With this address, my commits would not link to my profile or count on my contribution graph.
- I caught it before pushing. See Issue 2 in the [mistakes log](mistakes_log.md).

### Step 16: Set my Git name and email

**What I did:** Set my name and GitHub's private noreply email for all Git projects on this Mac.

```bash
(.venv) $ git config --global user.name "Amrit Sharma" && git config --global user.email "<my GitHub noreply email>" && git config --global --list | grep user
user.name=Amrit Sharma
user.email=<my GitHub noreply email>
```

**Notes:**
- `--global` applies these settings to every Git project on my Mac, so this is a one-time setup.
- I used GitHub's noreply address (from github.com/settings/emails) instead of my personal email. Commit emails are public, and the noreply address still links commits to my profile.

### Step 17: Fix the author on the first commit

**What I did:** Replaced the first commit with a copy that has my correct name and email.

```bash
(.venv) $ git commit --amend --reset-author --no-edit && git log --format="%h %an <%ae> %s"
[main 01603ef] Phase 1: project setup, Python 3.13 venv, dbt-duckdb, and docs
 11 files changed, 511 insertions(+)
 ...
01603ef Amrit Sharma <my GitHub noreply email> Phase 1: project setup, Python 3.13 venv, dbt-duckdb, and docs
```

**Notes:**
- The commit ID changed from `4890308` to `01603ef`. Changing a commit creates a new commit.
- `--no-edit` kept the same commit message.
- Amending was safe only because I had not pushed yet. Changing commits that are already on GitHub rewrites shared history, so I avoid that.

### Step 18: Create the empty repo on GitHub

**What I did:** Created a public repo named `ai-billing-pipeline` on github.com/new.

**Notes:**
- Description: "Billing and revenue data pipeline for a fictional AI API company. Python, DuckDB, dbt, Airflow. Documented as a learning project."
- I left "Add a README", ".gitignore", and "license" unchecked. My project already had files locally, and if GitHub had created its own, the two histories would not match and my first push would be rejected.

### Step 19: Connect the local project to GitHub

**What I did:** Saved the GitHub repo address as `origin`.

```bash
(.venv) $ git remote add origin https://github.com/amritsharmagithub/ai-billing-pipeline.git && git remote -v
origin	https://github.com/amritsharmagithub/ai-billing-pipeline.git (fetch)
origin	https://github.com/amritsharmagithub/ai-billing-pipeline.git (push)
```

**Notes:**
- `origin` is the standard name for the main online copy of a project.
- The saved address has no token in it. The token is only used at push time and is never stored in the project settings.

### Step 20: First push to GitHub (worked, but exposed my token)

**What I did:** Entered my token with `read -s TOKEN` and pushed.

```bash
(.venv) $ git push -u https://amritsharmagithub:${TOKEN}@github.com/amritsharmagithub/ai-billing-pipeline.git main
Enumerating objects: 15, done.
...
To https://github.com/amritsharmagithub/ai-billing-pipeline.git
 * [new branch]      main -> main
branch 'main' set up to track 'https://amritsharmagithub:[TOKEN REMOVED]@github.com/amritsharmagithub/ai-billing-pipeline.git/main'.
```

**Notes:**
- The push worked. All 11 files are on GitHub.
- The `-u` flag made Git save the full push URL, **including my token**, into `.git/config` on my Mac, and it printed the token in the terminal. I had pasted that output into my chat with Claude, so the token was exposed there too.
- I have removed the token from this log. See Issue 3 in the [mistakes log](mistakes_log.md).

### Step 21: Remove the token from the project settings

**What I did:** Replaced the saved URL with `origin`, fetched GitHub's copy of `main`, and checked that no token was left.

```bash
(.venv) $ git config branch.main.remote origin && git fetch origin && grep -c "ghp_" .git/config
0
```

**Notes:**
- `0` means no token is left in `.git/config`.
- I also cleared the terminal (Cmd + K) so the token could not end up in a screenshot.
- I revoked the exposed token at github.com/settings/tokens. That is the step that made it safe.

### Step 22: Check the repo on GitHub

**What I did:** Opened the repo in my browser to confirm the push.

![The repo on GitHub after the first push](screenshots/phase1_04_github_first_push.png)

**Notes:**
- All four top-level items are there: `docs`, `.gitignore`, `CREDITS.md`, and `requirements.txt`.
- The commit `01603ef` shows my username and profile picture, which confirms the Git identity fix from Issue 2 worked.

### Step 23: Replace the old docs zip

**What I did:** Deleted the old zip from Downloads before downloading the updated one.

```bash
(.venv) $ rm ~/Downloads/phase1_docs.zip && ls ~/Downloads | grep -i phase1
```

**Notes:**
- No output means the old file was gone. If it had stayed, the browser would have saved the new file as `phase1_docs (1).zip`, and my unzip command would have used the old one.

### Step 24: Unpack the updated docs

**What I did:** Unpacked the updated docs over the old ones and checked what changed.

```bash
(.venv) $ unzip -o ~/Downloads/phase1_docs.zip -d ~/ai-billing-pipeline && git status
...
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
	modified:   docs/build_log.md
	modified:   docs/lessons_learned.md
	modified:   docs/mistakes_log.md

Untracked files:
	docs/screenshots/phase1_04_github_first_push.png
```

**Notes:**
- Git only listed the files that actually changed. The unchanged files were overwritten with identical copies, so Git ignored them.
- `Your branch is up to date with 'origin/main'` shows the cleanup in Step 21 worked: my branch now tracks `origin`, which has no token in it.

### Step 25: Commit the updated docs

**What I did:** Staged, reviewed, and committed the updated docs.

```bash
(.venv) $ git add . && git status --short && git commit -m "Phase 1: log Git identity fix, token incident, and first push"
M  docs/build_log.md
M  docs/lessons_learned.md
M  docs/mistakes_log.md
A  docs/screenshots/phase1_04_github_first_push.png
[main 5ffd724] Phase 1: log Git identity fix, token incident, and first push
 4 files changed, 274 insertions(+)
 create mode 100644 docs/screenshots/phase1_04_github_first_push.png
```

**Notes:**
- `M` means modified and `A` means added. 4 files, as expected.
- No identity warning this time, which confirms the Git name and email settings from Step 16 are working.

### Step 26: Push with a new token, the safe way

**What I did:** Created a new token (classic, `repo` scope only, 30-day expiration), pushed **without `-u`**, then cleared the token and checked that nothing was saved.

```bash
(.venv) $ read -s TOKEN
(.venv) $ git push https://amritsharmagithub:${TOKEN}@github.com/amritsharmagithub/ai-billing-pipeline.git main
...
To https://github.com/amritsharmagithub/ai-billing-pipeline.git
   01603ef..5ffd724  main -> main
(.venv) $ unset TOKEN && echo "TOKEN is now: [${TOKEN}]" && grep -c "ghp_" .git/config
TOKEN is now: []
0
```

**Notes:**
- No `-u`, so Git did not save the URL, and the token did not appear in the output.
- `TOKEN is now: []` proves the token was cleared from the terminal session.
- `0` proves no token was written to `.git/config`.
- This is now my standard push routine (see `project_brief.md`).

### Step 27: Sync my local view of GitHub

```bash
(.venv) $ git fetch origin && git status -sb
From https://github.com/amritsharmagithub/ai-billing-pipeline
   01603ef..5ffd724  main       -> origin/main
## main...origin/main
```

**Notes:**
- Pushing to the full URL does not update my Mac's record of what GitHub has. `git fetch origin` refreshes it without needing a token, because the repo is public.
- `## main...origin/main` with nothing after it means my Mac and GitHub match.

### Session 1 summary

**Done:**
- Project folder, Python 3.13 virtual environment, dbt-core 1.12.7 + dbt-duckdb 1.11.1 + DuckDB 2.0.0
- `requirements.txt`, `.gitignore`, Git repo, docs folder, and two commits pushed to GitHub

**Issues hit and fixed (see the [mistakes log](mistakes_log.md)):**
1. SSL certificate error during install: ran the python.org certificate script
2. First commit made without my Git name and email: set them and amended the commit before pushing
3. GitHub token exposed by `-u` on the first push: revoked it, cleaned `.git/config`, and set a safe push routine

**Decision made (see the [decisions log](decisions_log.md)):** build on dbt v1 now and upgrade to dbt v2 in Phase 8.

**What I'd tell myself at the start:** setup is where small environment problems show up. Reading each output line, especially warnings on commands that "worked," caught two of the three issues before they caused harm.

**Next:** watch Part 1 of the MotherDuck series and take notes in `video_notes.md`, then start Phase 2 (generating billing data in Python).

---

## Session 2 — Friday, November 13, 2026 (later the same morning)

**Goal for this session:** Save the end-of-Phase-1 docs to GitHub, watch Part 1 of the MotherDuck series, and start Phase 2.

### Step 1: Check the docs zip before unpacking

**What I did:** My browser saved the new download as `phase1_docs (1).zip`. I deleted the older copy, then checked the size of the one I kept.

```bash
(.venv) $ ls -l ~/Downloads/"phase1_docs (1).zip"
-rw-r--r--@ 1 amritsharma  staff  609645 Nov 13 09:56 /Users/amritsharma/Downloads/phase1_docs (1).zip
```

**Notes:**
- The size I was told to expect (725,087 bytes) was the total size of the files *inside* the zip, not the zip itself. Zip files are compressed, so they are smaller.
- Comparing against the actual file that was sent (609,645 bytes) confirmed it was the right one. Lesson: check against the real source, not a number someone tells me.
- File names with spaces or brackets need quotes in Terminal: `~/Downloads/"phase1_docs (1).zip"`.

### Step 2: Unpack the updated docs

```bash
(.venv) $ unzip -o ~/Downloads/"phase1_docs (1).zip" -d ~/ai-billing-pipeline && git status --short
...
 M docs/build_log.md
 M docs/mistakes_log.md
 M docs/project_brief.md
?? docs/video_notes.md
```

**Notes:**
- ` M` means modified, and `??` means a new file Git has not seen before.
- 3 docs updated, plus the new `video_notes.md`.

### Step 3: Commit the end-of-Phase-1 docs

```bash
(.venv) $ git add . && git status --short && git commit -m "Phase 1: add session summary, video notes, and safe push routine"
M  docs/build_log.md
M  docs/mistakes_log.md
M  docs/project_brief.md
A  docs/video_notes.md
[main 7c16e3f] Phase 1: add session summary, video notes, and safe push routine
 4 files changed, 181 insertions(+)
 create mode 100644 docs/video_notes.md
```

### Step 4: Push with the safe routine

```bash
(.venv) $ read -s TOKEN
(.venv) $ git push https://amritsharmagithub:${TOKEN}@github.com/amritsharmagithub/ai-billing-pipeline.git main
(.venv) $ unset TOKEN && echo "TOKEN is now: [${TOKEN}]" && grep -c "ghp_" .git/config
TOKEN is now: []
0
(.venv) $ git fetch origin && git status -sb
From https://github.com/amritsharmagithub/ai-billing-pipeline
   5ffd724..7c16e3f  main       -> origin/main
## main...origin/main
```

**Notes:**
- `5ffd724..7c16e3f` in the fetch output confirms GitHub received the new commit.
- Token cleared, nothing saved in `.git/config`, and my Mac matches GitHub.
- **Phase 1 is complete.**

### Step 5: Watch Part 1 of the MotherDuck series
Watched the full video and wrote short notes on the key takeaways and what I'll do differently for billing. See [video notes](video_notes.md).

### Step 6: Re-scope the project
Stepped back to check the plan against my target roles (analytics, finance, billing, possibly data science). Dropped Airflow, made the dbt v2 upgrade optional, and switched to lighter logging for routine steps. See Decision 2 in the [decisions log](decisions_log.md).

### Step 7: Design the data and the planted errors
Designed 6 tables and 7 planted errors, each tied to my settlement work at Fiserv. See Decision 3 in the [decisions log](decisions_log.md).

---

## Phase 2: Generate billing data

### Step 8: Create the generator folder
```bash
(.venv) $ mkdir -p generator && touch generator/__init__.py generator/config.py generator/main.py && ls generator
__init__.py	config.py	main.py
```
- `config.py` holds settings (prices, period, seed), `main.py` holds the main flow, and `__init__.py` makes the folder a Python package. This follows the "main file reads like a list of steps" approach from the MotherDuck video.

### Step 9: Set up VS Code
- Installed VS Code (desktop) and the Microsoft Python extension (which includes Pylance and the Python Debugger). Skipped signing in, and left GitHub Copilot off so the code I write is my own.
- Opened the project folder. VS Code's Source Control panel showed my 3 commits and the 3 new generator files.
- I commit in Terminal, not with VS Code's Commit button, so every commit goes through my review routine.
- **Open issue:** the Python extension stayed on "Python extension loading..." for over 15 minutes, even after `Developer: Reload Window`. It doesn't block the work (I write code in VS Code and run it in Terminal), so I moved on and will come back to it.

### Step 10: Write the settings in `config.py`
- Added the random seed (42), number of customers (50), billing period (January 1 to June 30, 2026), and three plans (Starter, Pro, Enterprise), each with a monthly fee, included tokens, and an overage price.
- All money is stored in **whole cents**, because decimals like 0.1 can't be stored exactly by computers and cause rounding breaks.
- Running `config.py` by itself prints nothing, which is expected: it only stores settings. I checked that the settings load correctly:

```bash
(.venv) $ python -c "from generator.config import PLANS, BILLING_START, BILLING_END; print(PLANS['Pro']); print(BILLING_START, 'to', BILLING_END)"
{'monthly_fee_cents': 50000, 'included_tokens': 50000000, 'overage_cents_per_million': 150}
2026-01-01 to 2026-06-30
```
- Worked example: a Pro customer using 60 million tokens pays the $500 fee + 10 million extra tokens × $1.50 per million = **$515.00** (51,500 cents).

### Step 11: Build the customers table
- Added `generator/generate.py` with `generate_customers()`: 50 customers, each with an ID (`C001`–`C050`), a made-up company name, a country (US most common), and a signup date in 2025.
- Added `generator/main.py`, the main flow: set the seed, build the tables, print a quick check.
- Ran it with `python -m generator.main`. The `-m` runs it as part of the `generator` package, so imports between my files work.

```bash
(.venv) $ python -m generator.main
Customers: 50 rows
{'customer_id': 'C001', 'company_name': 'North Labs', 'country': 'GB', 'signup_date': datetime.date(2025, 8, 28)}
{'customer_id': 'C002', 'company_name': 'Swift Health', 'country': 'US', 'signup_date': datetime.date(2025, 1, 19)}
{'customer_id': 'C003', 'company_name': 'Nova Analytics', 'country': 'IN', 'signup_date': datetime.date(2025, 12, 15)}
```
- Company names can repeat by chance. That's realistic, and it's why every customer has a unique ID. In billing, records are matched on IDs, never names.
- Ran it a second time and got exactly the same rows, which proves the seed works. Anyone who clones the repo gets the same data, so my test and reconciliation results can be checked by someone else.

### Step 12: Build the subscriptions table
- Added `generate_subscriptions()`: one plan per customer, picked with weights (60% Starter, 30% Pro, 10% Enterprise). About 1 in 5 start on Feb 1 or Mar 1, and about 1 in 10 cancel at the end of March, April, or May.
- Prices are copied onto each subscription ("price snapshot"), and subscriptions start and end on whole months to avoid proration. See Decision 4.
- My first run showed the old output, because I had pasted an older version of the code. See Issue 4 in the [mistakes log](mistakes_log.md).

```bash
(.venv) $ python -m generator.main
Customers: 50 rows
Subscriptions: 50 rows
Plans: Counter({'Pro': 23, 'Starter': 23, 'Enterprise': 4})
Cancelled: 6
First subscription: {'subscription_id': 'S001', 'customer_id': 'C001', 'plan': 'Pro', 'monthly_fee_cents': 50000, 'included_tokens': 50000000, 'overage_cents_per_million': 150, 'start_date': datetime.date(2026, 1, 1), 'end_date': None}
```
- The plan mix (23 / 23 / 4) is not exactly 60 / 30 / 10. With only 50 customers, random picks can land well away from the target. That's normal for small samples, and it's still a realistic mix.

### Step 13: Build the usage_events table
- Added `generate_usage_events()`: one row per subscription per active day, with the model used and the tokens used. Each customer uses 50%–150% of their included tokens per month, so about half will have overage. Daily usage varies by up to 30%.
- The usage data is kept clean on purpose. The "unbilled usage" error is planted later, in the invoices.
- The first run failed with `ImportError: cannot import name 'generate_usage_events'`, because only `main.py` had been updated. The `wc -l` check before running showed `generate.py` was still the old length, which pointed straight at the cause. After saving the new `generate.py`, it worked:

```bash
(.venv) $ wc -l generator/generate.py generator/main.py && python -m generator.main
     124 generator/generate.py
      33 generator/main.py
...
Usage events: 8325 rows
Total tokens used: 27,998,804,417
First usage event: {'usage_id': 'U00001', 'customer_id': 'C001', 'subscription_id': 'S001', 'usage_date': datetime.date(2026, 1, 1), 'model': 'lumen-small', 'tokens_used': 998789}
```
- Lesson: read the **last line** of an error first. Here it named the exact missing function.

### Step 14: Save the tables to CSV and DuckDB
- Added `generator/db.py`. It writes each table to `data/raw/<table>.csv` (like exports from Lumen AI's systems), then loads each CSV into `data/lumen_billing.duckdb` as a table in the `raw` schema.
- Each run uses `CREATE OR REPLACE TABLE`, so rerunning never creates duplicate rows (the idempotent-writes idea from the MotherDuck video).
- Python's `None` becomes an empty CSV cell, which DuckDB reads as `NULL`.

```bash
(.venv) $ python -m generator.main
...
Wrote 3 CSV files to data/raw/
Loading into data/lumen_billing.duckdb:
  raw.customers: 50 rows
  raw.subscriptions: 50 rows
  raw.usage_events: 8325 rows
```
- Row counts in DuckDB match the counts in Python, so nothing was lost or duplicated during the load.

![Generator output and DuckDB load](screenshots/phase2_02_data_loaded.png)

### Step 15: Add a helper for running SQL
- Added `run_sql.py` in the project folder. It runs a `.sql` file against the DuckDB database and prints the result as a table: `python run_sql.py queries/<file>.sql`.
- It opens the database **read-only**, so a query can never change the data, like read-only access to a production ledger.
- I keep every query in a `queries/` folder, so my data exploration is saved and visible in the repo.

### Step 16: First SQL query, plan mix
- Wrote `queries/01_plan_mix.sql`: customers and monthly subscription fees per plan.
- The first run failed with `FileNotFoundError`, because VS Code had created the file in the project folder instead of inside `queries/`. I found it with `find . -name "01_plan_mix*" -not -path "./.venv/*"` and moved it with `mv`.

```bash
(.venv) $ python run_sql.py queries/01_plan_mix.sql
┌────────────┬───────────┬──────────────────┐
│    plan    │ customers │ monthly_fees_usd │
├────────────┼───────────┼──────────────────┤
│ Enterprise │         4 │          20000.0 │
│ Pro        │        23 │          11500.0 │
│ Starter    │        23 │           1150.0 │
└────────────┴───────────┴──────────────────┘
```

![First SQL query: plan mix](screenshots/phase2_03_first_query.png)

**What the result shows:**
- The 4 Enterprise customers (8% of customers) bring in about **61%** of monthly subscription fees ($20,000 of $32,650). That's **revenue concentration**: losing one Enterprise customer would cost more than all 23 Starter customers combined. Finance teams watch this closely.
- The dollar column came out as `double` (a decimal number type that can have tiny rounding errors). That's fine for a quick look, but in the dbt models I'll use an exact `DECIMAL` type for money.

### Step 17: Build the invoices table (clean version)
- Added `generate_invoices()`: one invoice per subscription per active month. It sums each month's usage, works out overage (never below 0), prices it, and adds the subscription fee. Invoices are dated the 1st of the next month and due 30 days later (Net 30).
- Overage is rounded to the nearest cent, with half a cent rounding up, using whole-number math only. See Decision 5.
- `main.py` now checks the overage math with an `assert` before building any invoices: the Pro example (10 million extra tokens at 150 cents per million) must equal 1,500 cents, or the script stops.
- These are the **correct** invoices. Errors will be planted in a separate step, so I always know exactly which errors were added.
- The `wc -l` check caught that `main.py` hadn't been updated on the first try (still the old length), so I replaced it before trusting the output.

```bash
(.venv) $ python -m generator.main
...
Invoices: 276 rows
Invoices with overage: 127
Total billed: $183,711.96
...
  raw.invoices: 276 rows
```
- 127 of 276 invoices (46%) have overage, close to the "about half" the usage design aimed for.

### Step 18: Control check on the clean invoices
- Wrote `queries/02_invoice_checks.sql`, a reconciliation that compares each invoice to its source data:
  1. **Usage check:** invoice `usage_tokens` vs. the sum of `usage_events` for that subscription and month
  2. **Math check:** `total_cents` vs. `subscription_fee_cents + overage_cents`
  3. **Missing check:** months with usage but **no invoice at all**. Checks 1 and 2 start from invoices, so they can't find a missing invoice. This check starts from usage, so it's two-sided matching, like reconciling both the client side and the bank side.
- The file first ended up in `queries/queries/` (see Issue 5). After moving it:

```bash
(.venv) $ python run_sql.py queries/02_invoice_checks.sql
┌──────────────────┬──────────────┬─────────────┬────────────────────────┐
│ invoices_checked │ usage_breaks │ math_breaks │ months_with_no_invoice │
├──────────────────┼──────────────┼─────────────┼────────────────────────┤
│              276 │            0 │           0 │                      0 │
└──────────────────┴──────────────┴─────────────┴────────────────────────┘
```
![Control check on clean invoices: 0 breaks](screenshots/phase2_04_invoice_checks_clean.png)

- **0 breaks on clean data.** After planting errors, I'll run this exact query again, and it should find them. Same check, before and after.

### Step 19: Keep generated data off GitHub
```bash
(.venv) $ echo "data/" >> .gitignore && tail -3 .gitignore && git status --short
.env
.DS_Store
data/
 M .gitignore
?? generator/
?? queries/
?? run_sql.py
```
- Added `data/` to `.gitignore`. The CSVs and DuckDB file are rebuilt in seconds by the generator and come out identical every time (fixed seed), so the code is the real record.
- `>>` adds a line to the end of a file. A single `>` would have replaced the whole file.

### Step 20: Commit and push Phase 2 progress
- Checked the docs zip size against the size sent (927,394 bytes), unpacked it, reviewed the staged list (19 files, nothing from `data/`, `.venv/`, or `__pycache__/`), and committed `38c14eb`.
- Pushed with the safe routine: `7c16e3f..38c14eb  main -> main`, `TOKEN is now: []`, `0` tokens in `.git/config`, and `## main...origin/main`.

### Step 21: Build the payments table (clean version)
- Added `REPORT_DATE = date(2026, 7, 31)` to `config.py`: the month-end close date. Only payments received on or before it are included.
- Added `generate_payments()`: most invoices are paid in full 5–40 days after the invoice date (due in 30, so some are late). About 1 in 20 are never paid; these feed the aging report.

```bash
(.venv) $ python -m generator.main
...
Total billed: $183,711.96
Payments: 259 rows (as of 2026-07-31)
Total collected: $174,173.57
Unpaid invoices: 17 ($9,538.39)
...
  raw.payments: 259 rows
```

**Checked by hand (accounts receivable):**
- $183,711.96 billed − $174,173.57 collected = **$9,538.39** unpaid ✓
- 259 paid invoices + 17 unpaid = **276** invoices ✓

### Step 22: Plant the errors, with an answer key
- Added `generator/errors.py` (created with `touch`, per Issue 5). It plants 20 errors in the clean invoices and payments and writes an **answer key**, `raw.planted_errors`, listing each one. Each invoice and its payments get at most one error, so every break has exactly one cause.
- Before handing me the code, Claude rebuilt my generator on its side and tested it. That caught a bug in its first draft (invoices don't store the overage price, so it has to be looked up from the subscription) and math errors that were too small to matter ($0.53). Both were fixed before I ran anything. See Decision 3 (update).

```bash
(.venv) $ wc -l generator/errors.py generator/main.py && python -m generator.main && python run_sql.py queries/02_invoice_checks.sql
     162 generator/errors.py
      71 generator/main.py
...
Invoices: 274 rows
Payments: 264 rows (as of 2026-07-31)
Total billed: $183,019.01
Total collected: $175,105.81

Planted errors: 20
  cutoff_error: 3
  duplicate_payment: 3
  invoice_math_error: 3
  short_payment_unexplained: 2
  short_payment_wire_fee: 2
  unapplied_cash: 3
  unbilled_usage_missing_invoice: 2
  unbilled_usage_understated: 2
...
  raw.planted_errors: 20 rows
┌──────────────────┬──────────────┬─────────────┬────────────────────────┐
│ invoices_checked │ usage_breaks │ math_breaks │ months_with_no_invoice │
├──────────────────┼──────────────┼─────────────┼────────────────────────┤
│              274 │            2 │           3 │                      2 │
└──────────────────┴──────────────┴─────────────┴────────────────────────┘
```

![Errors planted, and the control check finding the invoice errors](screenshots/phase2_05_errors_planted.png)

**Before and after:** the same control check showed **0 / 0 / 0** on the clean data (Step 18) and now shows **2 / 3 / 2**, exactly the planted invoice errors (2 understated usage, 3 math errors, 2 missing invoices). The payment errors need new checks, which come in Phases 4 and 5.

### Phase 2 summary
- **Built:** a reproducible generator for 6 tables (customers, subscriptions, usage events, invoices, payments, and the planted-errors answer key), loaded into DuckDB.
- **Checked:** row counts after loading, accounts receivable by hand (billed − collected = unpaid), and a two-sided invoice control check, before and after planting errors.
- **Issues:** 4 and 5 (old code run by mistake, files in the wrong folder), both fixed by changing my process.
- **Decisions:** 3, 4, and 5 (data design, price snapshots and whole months, rounding rule).
- **Next:** Phase 3, dbt models, following Part 2 of the MotherDuck series.
