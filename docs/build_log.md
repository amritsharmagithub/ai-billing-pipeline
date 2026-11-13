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
