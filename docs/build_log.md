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
