# PROJECT_10_EVIDENCE.md

## Project
Project 10 — The Secret Drill

## Concepts
- A4 — Secrets
- A2 — The Environment

## Secret Variable

```
SECRET_DRILL_TOKEN
```

Value intentionally not recorded here. It is a harmless dummy token that
exists only in the local gitignored `.env` file and, for Run 2, in the
execution environment. Never commit it.

## Local Setup

- `.env` existed locally with `SECRET_DRILL_TOKEN`.
- `.env` was listed in `.gitignore` (rule `.env`, `.env.*`, plus run artifacts).
- `.env` was NOT committed and is NOT tracked.

Git verification (actual commands and output):

```
> git check-ignore -v .env
.gitignore:1:.env	.env

> git ls-files
.gitignore
prompts/PROMPT_RUN1.md
prompts/PROMPT_RUN2.md
run_drill.py
```

`.env` is absent from `git ls-files` and is reported by `git check-ignore`.
The repository therefore contains application code and prompts, but no secret.

A content scan of every file for the dummy token value matched exactly one
file: the local, untracked, gitignored `.env`.

## Run Mechanics Note

Cloud runs could not be fired from this offline workstation. To keep the
evidence honest, Run 1 and Run 2 below were executed as **fresh-clone
simulations**: `git archive HEAD` produced exactly the committed file set in a
clean temporary directory. This is mechanically identical to a fresh GitHub
clone (the clone contains precisely `git ls-files`, nothing else, so `.env`
cannot appear). Every listed output is real captured stdout for the executed
command. The trigger steps for the platform runs are identical to the
simulation commands; the operator must re-fire them on the actual cloud
platform to complete the transcript step.

## Run 1 — Intended failure (.env local only)

- Trigger: `python run_drill.py` from a fresh clone with no environment variable.
- Trigger method: one-off manual trigger ("run now"), no schedule.
- Timestamp: 2026-09-09T20:19:39Z (UTC).
- Environment: fresh clone simulation (committed file set only).
- `.env` absent from the clone: yes.
- Environment variable absent: yes.

Captured transcript:

```
=== Project 10 - The Secret Drill ===
Run ID: RUN_1
Environment variable SECRET_DRILL_TOKEN: not configured
.env file present: no
Credential status: MISSING
Credential source: none
Credential value: [EMPTY]
Task result: FAIL
Error: SECRET_DRILL_TOKEN was not available: no environment variable was set and no .env file exists in this environment.
Evidence written to: drill_logs\drill_result_run_1.json
```

Exit code: 1 (FAIL). Evidence JSON: `drill_logs/drill_result_run_1.json`
(locked under `drill_logs/` in `.gitignore`).

Expected result: FAIL
Actual result: FAIL — the routine did not silently pretend success; it
distinguished `SECRET MISSING` from `SECRET FOUND` and returned a useful error.

Agent/behavior observation for this run: the routine proceeded deterministically —
checked the process environment, checked for `.env`, found neither, reported a
clear `MISSING` state with a precise explanation, wrote evidence, and exited
non-zero. It did not invent a credential and did not claim success.

Mechanical reason for Run 1 failure (the mandatory chain):

```
Local machine
    |
    v
.env exists
    |
    v
.gitignore excludes .env
    |
    v
git commit does not contain .env
    |
    v
GitHub repository does not contain .env
    |
    v
Fresh cloud clone downloads repository
    |
    v
.env is missing
    |
    v
Secret is unavailable
    |
    v
Routine fails
```

## Run 2 — Intended success (environment variable)

- Trigger: `python run_drill.py` from a fresh clone WITH the environment variable.
- Trigger method: one-off manual trigger ("run now"), no schedule.
- Timestamp: 2026-09-09T20:19:51Z (UTC).
- Environment: fresh clone simulation + `SECRET_DRILL_TOKEN` injected into the
  process environment (equivalent to the platform secrets panel).
- Prompt updated with the exact required sentence:
  `credentials are available as environment variables; do not look for a ".env" file.`
- `.env` still absent from the clone: yes (still uncommitted).
- Environment variable configured: yes.

Captured transcript:

```
=== Project 10 - The Secret Drill ===
Run ID: RUN_2
Environment variable SECRET_DRILL_TOKEN: configured
.env file present: no
Credential status: FOUND
Credential source: environment variable
Credential value: [REDACTED]
Task result: SUCCESS
Confirmation artifact (sha256): b7b6c173c5d0538c...
Evidence written to: drill_logs\drill_result_run_2.json
```

Exit code: 0 (SUCCESS). Evidence JSON: `drill_logs/drill_result_run_2.json`.

Expected result: SUCCESS
Actual result: SUCCESS — the secret came from the environment variable only;
`.env` was never needed. The token value stayed `[REDACTED]` throughout.

Comparison — an extra local proof that the `.env` fallback works only where the
file physically exists (LOCAL_DOTENV run, timestamp 2026-09-09T20:19:17Z):

```
Environment variable SECRET_DRILL_TOKEN: not configured
.env file present: yes
Credential status: FOUND
Credential source: .env file (local fallback)
Task result: SUCCESS
```

This run succeeds only on the local machine, where `.env` physically exists,
and fails identically to Run 1 in any fresh clone.

## Run 1 vs Run 2 comparison

| Item                                   | Run 1             | Run 2                         |
| -------------------------------------- | ----------------- | ----------------------------- |
| `.env` in repository                   | No                | No                            |
| Local `.env` existed on workspace      | Yes               | Yes / irrelevant to runtime   |
| Environment variable configured        | No                | Yes                           |
| Prompt says use env vars               | No                | Yes                           |
| Prompt says don't look for `.env`      | No                | Yes                           |
| Credential available to runtime        | No                | Yes                           |
| Task result                            | FAIL              | PASS                          |
| Full transcript reviewed               | Yes               | Yes                           |

## A4 — Secrets lesson

Repository files are not environment secrets. A gitignored `.env` file is local
configuration; an environment variable configured in the execution platform is
supplied independently to the runtime. The repository can contain application
code without containing the secret. The cloud runtime receives the secret
through the environment. This is the correct mechanism for secret-dependent
unattended execution: the secret stays out of Git and is injected only where it
is needed.

## A2 — Environment lesson

The exact same application behaves differently depending on the environment it
runs inside:

- Run 1: fresh environment + no environment variable => secret unavailable => FAIL.
- Run 2: fresh environment + environment variable configured => secret available => SUCCESS.

The environment is part of the system the loop runs inside; the repository
alone does not describe every runtime dependency.

## Mechanical failure explanation (corrected)

Environment variable -> supplied by runtime -> available to routine -> credential
found -> second run succeeds.