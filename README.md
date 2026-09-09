# Project 10 — The Secret Drill

## Difficulty
Easy to Medium

## Concepts
- A4 — Secrets
- A2 — The Environment

## Goal
Demonstrate the difference between a secret stored only in a local gitignored
`.env` file and a secret supplied by the execution environment as an
environment variable. The project intentionally shows the failure first
(Run 1) and the fix second (Run 2).

## /goal
Build a minimal secret-dependent routine and prove the difference between local
secret storage and environment-provided secrets. The drill must require the
credential `SECRET_DRILL_TOKEN`, and its status must be checkable:

```
SECRET FOUND   vs   SECRET MISSING
```

- Run 1 uses a fresh clone with no environment variable. The routine must FAIL.
- Run 2 uses the same fresh clone with the environment variable injected and a
  prompt that forbids `.env` hunting. The routine must SUCCEED.
- The full transcript of each run is the evidence — never just the status badge.

## /loop
```
Trigger
  |
  v
Fresh execution environment starts
  |
  v
Read repository (fresh clone)
  |
  v
Determine required credential (SECRET_DRILL_TOKEN)
  |
  v
Look for credential according to prompt/environment
  |
  v
Run secret-dependent task
  |
  v
Success OR failure
  |
  v
Write useful evidence/log
  |
  v
End run
```

Run 1 loop:

```
Trigger -> fresh cloud environment -> repo cloned from GitHub
-> .env is absent -> credential lookup fails -> task fails -> transcript inspected
```

Run 2 loop:

```
Trigger -> fresh cloud environment -> repo cloned
-> environment variable injected by execution environment
-> prompt says credentials are environment variables
-> agent reads environment variable -> secret-dependent task succeeds -> transcript inspected
```

The task: require `SECRET_DRILL_TOKEN`, verify it is present and non-empty, and
generate a harmless SHA-256 confirmation artifact. Success is real only when the
credential was actually available; a missing credential returns FAIL and a clear
error message.

## /schedule
This is a one-off verification drill, not a repeating schedule. Run it "now"
exactly twice with a one-off trigger:

1. **Run 1** — while the token exists only in the local gitignored `.env`.
2. **Run 2** — after the token is moved to the environment/secrets panel and the
   prompt is updated.

No daily/hourly/weekly schedule is needed for this drill.

The provided GitHub Actions workflows (`run1-fail.yml`, `run2-success.yml`)
are fired manually with the **"Run workflow"** button in the Actions tab (a
`workflow_dispatch` one-off trigger), so each run is a fresh clean runner.

- Run the `Secret Drill - Run 1 (expected failure)` workflow BEFORE adding the
  repo secret.
- Then add the repository secret `SECRET_DRILL_TOKEN` (Settings -> Secrets and
  variables -> Actions) with the same dummy value as the local `.env`.
- Finally run the `Secret Drill - Run 2 (expected success)` workflow.

## Secret Setup
- The variable name is `SECRET_DRILL_TOKEN`.
- Locally, `.env` contains a harmless dummy value under the key
  `SECRET_DRILL_TOKEN`. The value itself is not recorded in this document.
- `.gitignore` excludes `.env`, `.env.*`, `drill_logs/`, and Python caches.
- `.env` is NOT committed. `git check-ignore -v .env` returns
  `.gitignore:1:.env	.env`, and `git ls-files` lists only `.gitignore`,
  `prompts/`, and `run_drill.py`.
- The actual value is never printed. All output shows `[REDACTED]`.

## Run 1 — .env Failure
Run 1 is fired from a fresh clone with **no** environment variable configured.
A local `.env` exists on the workspace machine, but because `.env` is
gitignored it is never committed, so the fresh clone cannot contain it. The
routine reports `SECRET MISSING`, writes an error, and exits non-zero.

Reference evidence: `PROJECT_10_EVIDENCE.md` (Run 1), which includes the
captured transcript and the exit code.

## Transcript Observation
The routine checks the process environment first, then the working directory
for `.env`. In the fresh clone it finds neither. It reports `Credential status:
MISSING`, `Credential source: none`, and a precise error message. It does not
pretend success — the distinction between `SECRET FOUND` and `SECRET MISSING`
is explicit.

## Mechanical Reason for Failure
The first run fails because the only storage of the secret is a gitignored local
file:

```
.env exists locally
  -> .gitignore excludes .env
  -> git commit does not contain .env
  -> GitHub repository does not contain .env
  -> fresh cloud clone downloads repository
  -> .env is missing
  -> secret is unavailable
  -> routine fails
```

## Run 2 — Environment Variable Success
The same dummy token is placed into the platform's environment/secrets panel
under the name `SECRET_DRILL_TOKEN`. Nothing else changes in the repository:
`.env` is still uncommitted, `.env` still does not exist in the fresh clone.
On the next fresh run the runtime injects the variable, the routine reads it
from the environment, and the task succeeds.

## Prompt Instruction
The Run 2 prompt contains this exact sentence:

> credentials are available as environment variables; do not look for a `.env` file.

The prompt also instructs the agent not to search the repository for secret
files, not to recover secrets from files, not to hard-code the credential, and
to clearly report a missing environment variable rather than fabricate success.

## Transcript Observation
On Run 2 the routine reports `Environment variable SECRET_DRILL_TOKEN:
configured`, `.env file present: no`, `Credential status: FOUND`, `Credential
source: environment variable`, and `Task result: SUCCESS`. The full token value
was never printed; it appears as `[REDACTED]`.

## A4 — Secrets Lesson
Repository files are not the same as environment secrets. A gitignored `.env`
file is purely local configuration and cannot reach a fresh clone. An
environment variable configured on the execution platform is supplied
independently to the runtime. Application code lives in the repository; secrets
live in the runtime environment. Never commit a `.env` file or hard-code a token.

## A2 — Environment Lesson
The identical application behaves differently purely because of the environment
it runs in:

- Fresh environment + no environment variable = secret unavailable = FAIL.
- Fresh environment + environment variable configured = secret available = PASS.

The environment is part of the system the loop runs inside; the repository alone
does not describe every runtime dependency.

## Security
- The token is a harmless dummy value.
- `.env` is gitignored and never committed.
- The token is not hard-coded anywhere in the source.
- No committed file contains the token value (verified by content scan).
- The routine redacts the value in all output and logs.
- Evidence logs live under `drill_logs/`, which is also gitignored.

## Evidence
- `PROJECT_10_EVIDENCE.md` — full write-up of both runs, mechanics, and lessons.
- `drill_logs/drill_result_run_1.json` and `drill_logs/drill_result_run_2.json`
  — machine-readable outputs produced by the routine for each run.

Note: because this offline workstation has no access to a cloud platform, the
runs in the evidence file were executed as fresh-clone simulations using
`git archive HEAD` (which reproduces exactly the committed file set — the same
content a fresh GitHub clone would contain). The trigger steps for the platform
are identical; re-fire both runs there and append the platform transcripts to
`PROJECT_10_EVIDENCE.md` to complete the cloud verification.

## Final Result

```
RUN 1
Local: .env exists -> .gitignore excludes .env -> not committed -> not on GitHub
-> fresh clone has no .env -> secret unavailable -> routine FAILS -> transcript read

RUN 2
Environment panel: SECRET_DRILL_TOKEN configured -> fresh execution
-> prompt says credentials are environment variables -> agent reads env var
-> secret available -> routine SUCCEEDS -> transcript read
```

Conclusion: a gitignored `.env` file is local-only unless its value is supplied
to the runtime another way. A fresh cloud clone cannot see a file that was never
committed, while an environment variable configured in the runtime is available
independently of the repository.