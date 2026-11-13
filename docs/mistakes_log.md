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

---

## Issue 2: First commit was made without my Git name and email

**Date:** November 13, 2026
**Phase:** 1 — Setup
**Time to resolve:** about 4 minutes

### What happened
My first commit worked, but Git printed a warning:

```
Committer: Amrit Sharma <amritsharma@Amrits-MacBook-Pro.local>
Your name and email address were configured automatically based
on your username and hostname. Please check that they are accurate.
```

### Why it happened (root cause)
Git had never been given my name and email on this Mac, so it guessed them from my computer's username and hostname. GitHub links commits to a profile by email. With `amritsharma@Amrits-MacBook-Pro.local`, my commits would not have linked to my GitHub profile or counted on my contribution graph, which matters because the goal of this project is to show my work on GitHub.

### How I fixed it
1. Set my name and email once for all projects on this Mac:
   `git config --global user.name "Amrit Sharma"` and `git config --global user.email "<my GitHub noreply email>"`.
2. Fixed the first commit with `git commit --amend --reset-author --no-edit`.
3. Checked the result with `git log --format="%h %an <%ae> %s"`. The commit now shows my name and noreply email.
4. After pushing, confirmed on GitHub that the commit shows my username and profile picture.

![Commit linked to my GitHub profile](screenshots/phase1_04_github_first_push.png)

### Choices I made
- I used GitHub's private noreply email instead of my personal email. Commit emails are public in a public repo, and the noreply address still links commits to my profile.
- Amending was only safe because I had not pushed yet. If the commit had already been on GitHub, changing it would have rewritten shared history.

### How I prevent it now
- On any new computer, I set `user.name` and `user.email` before the first commit.
- Before pushing, I check the author on my commits with `git log --format="%h %an <%ae> %s"`.
- I read Git's warnings even when the command "worked." This one was easy to miss because the commit itself succeeded.

---

## Issue 3: My GitHub token was exposed during the first push

**Date:** November 13, 2026
**Phase:** 1 — Setup
**Severity:** High (a credential with write access to all my repos was exposed)

### What happened
I pushed with this command, which Claude gave me:

```bash
git push -u https://amritsharmagithub:${TOKEN}@github.com/amritsharmagithub/ai-billing-pipeline.git main
```

The push worked, but the last line of the output printed my full token:

```
branch 'main' set up to track 'https://amritsharmagithub:[TOKEN REMOVED]@github.com/amritsharmagithub/ai-billing-pipeline.git/main'.
```

I pasted that output into my chat with Claude before noticing it.

### Why it happened (root cause)
- `-u` tells Git to remember where this branch pushes to. Because the push address was a full URL with the token inside it, Git saved that URL, token included, in `.git/config`, and printed it.
- My earlier projects pushed without `-u`, so this had never happened before.
- I ran the command without questioning it because it came from my AI assistant. The assistant made the mistake, but it was still my credential, and I ran the command.

### What was and was not exposed
- **Exposed:** my terminal screen, `.git/config` on my Mac, and my chat with Claude.
- **Not exposed:** the GitHub repo. `.git/config` is never uploaded, and the token was not in any committed file.

### How I fixed it
1. **Revoked the token** at github.com/settings/tokens, so the leaked value no longer works anywhere.
2. Ran `unset TOKEN` to clear it from the terminal session.
3. Replaced the saved URL with the safe remote name: `git config branch.main.remote origin`, then `git fetch origin`.
4. Checked that no token was left: `grep -c "ghp_" .git/config` returned `0`.
5. Cleared the terminal with Cmd + K, and removed the token from this log.

### How I prevent it now
- **Never combine `-u` with a URL that contains a token.** I set the upstream with `origin` instead, which has no token in it.
- **Check output for secrets before pasting it anywhere**, including into an AI chat. Look for anything starting with `ghp_`.
- **Read every command before running it, and ask what each flag does, even when the command comes from an AI assistant.**
- **Revoke first, then clean up.** If a credential is exposed, revoking it comes before anything else, because cleanup alone does not make a leaked token safe.
- Use short expiration dates on tokens, so a leak has a time limit.
