# resume_extractor_from_linkedin

Exports the owner's LinkedIn profile (Resources -> Save to PDF) to
`~/Desktop/Nelson-Sproul-Resume.pdf` using Playwright and a persistent,
private browser profile.

## Setup

```bash
util/init.sh
```

Create the credentials file with the LinkedIn password on a single line:

```bash
printf '%s' 'PASSWORD' > ~/.linkedin && chmod 600 ~/.linkedin
```

Type it directly in a terminal rather than an editor to keep it out of
shell history files; add a leading space or use `HISTCONTROL` if your
shell records every command. `util/init.sh` also enforces mode 0600.

Install the browser the pinned Python playwright needs:

```bash
.venv/bin/python -m playwright install chromium
```

NOTE: `playwright.init` installs the *npm* playwright build, whose
chromium revision differs from what the pinned pip playwright==1.64.1
expects (1248 vs npm's 1254). If the extractor reports the browser as
missing, run the pip command above.

## Run

```bash
bin/extract_resume
```

Runs headless and unattended, reusing the stored session. On first use
or after the session expires:

```bash
bin/extract_resume --interactive --email you@example.com
```

A headed browser opens. If LinkedIn shows a checkpoint (code, CAPTCHA,
mobile approval), complete it by hand within `--checkpoint-seconds`
(default 300); the run then continues automatically. LinkedIn can require
this occasionally even with a stored password. In unattended mode a
checkpoint exits immediately with code 4.

Output override:

```bash
bin/extract_resume --output "/path with spaces/resume.pdf"
```

`--debug` adds INFO-level state logging (never credentials or cookies).

## State

- Browser profile and lock: `~/Library/Application Support/resume_extractor_from_linkedin/`
  (`browser_profile/`, `run.lock`), directory mode 0700.
- Password file: `~/.linkedin` (mode 0600 required).
- Both stay out of git.

## Exit codes

| code | meaning |
|------|---------|
| 0 | success |
| 2 | usage/config: bad args, missing email when login needed, missing/empty/multiline/wrong-mode credentials file |
| 3 | LinkedIn rejected the credentials |
| 4 | verification checkpoint required (unattended mode) |
| 5 | Resources / Save to PDF controls not found |
| 6 | browser or network failure, unexpected page |
| 7 | download was not a valid pdf |
| 8 | another run holds the lock |
| 9 | chromium not installed; run `.venv/bin/python -m playwright install chromium` |
| 10 | output path not writable; grant the terminal app Files and Folders / Desktop access in System Settings > Privacy & Security |

## Tests

```bash
util/run_tests.sh
```

## Notes and limitations

- Verified on this machine: headless unattended extraction works with the
  stored session, producing a 3-page PDF containing the profile name.
- The app calls `playwright.init` when chromium is missing, but that
  script installs a different chromium revision than pip playwright
  1.64.1 wants, so it will still fail with exit 9 and the message names
  the exact `playwright install chromium` command to run.
