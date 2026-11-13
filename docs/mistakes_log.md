# Mistakes and Issues Log

This file records real problems I ran into while building this project. I write each one like a short incident report: what happened, why it happened, how I fixed it, and what I do now so it does not happen again.

---

## Issue 1: dbt-duckdb install failed with an SSL certificate error

**Date:** November 13, 2026
**Phase:** 1 — Setup
**Time to resolve:** about 13 minutes

### What happened
Running `pip install dbt-duckdb` failed. One of dbt-core's dependencies, `dbt-core-experimental-parser`, tries to download an extra file from GitHub while it installs. That download failed:

```
RuntimeError: failed to download https://github.com/dbt-labs/dbt/releases/download/v2.0.11/dbt_core_experimental_parser-2.0.11-py3-none-macosx_10_12_x86_64.whl: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1032)>
error: metadata-generation-failed
```

![SSL certificate error](screenshots/phase1_01_ssl_certificate_error.png)

### Why it happened (root cause)
- My Python 3.13 was installed with the python.org installer for macOS. That installer does not set up trusted certificate authorities automatically. It leaves a one-time script, `Install Certificates.command`, that the user has to run. I had never run it.
- pip itself worked because pip carries its own certificate list. But this package used Python's built-in downloader (`urllib`), which had no certificate list. So Python could not confirm that GitHub was trustworthy, and it refused the download.

### How I confirmed the cause
Before changing anything, I checked how Python was installed:

```bash
ls "/Applications/Python 3.13/"
```

The folder existed and contained `Install Certificates.command`. That confirmed a python.org install where the certificate setup had never been run.

### How I fixed it
1. Ran the one-time setup script: `"/Applications/Python 3.13/Install Certificates.command"`. It installed `certifi` (a list of trusted certificate authorities based on Mozilla's) and pointed Python's SSL settings at it.
2. Ran `pip install dbt-duckdb` again. It installed without errors.

![Install Certificates fix](screenshots/phase1_02_install_certificates_fix.png)

### What I did not do, and why
A common suggestion online is to turn off certificate checking (for example, `pip install --trusted-host ...` or disabling SSL verification in code). That makes the error go away by removing a security check. I fixed the missing certificates instead. In billing and payments work, quietly turning off a safety check to make an error disappear is exactly the habit to avoid.

### How I prevent it now
- After installing any new Python version from python.org on a Mac, I run `Install Certificates.command` right away, before creating any virtual environments.
- I will add this step to the "Setup" section of this project's README, so anyone cloning the repo on a Mac knows to do it.
- When I see `CERTIFICATE_VERIFY_FAILED`, I check how Python was installed first, instead of searching for a way to skip the check.
