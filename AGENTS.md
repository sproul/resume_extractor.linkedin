# resume_extractor_from_linkedin

## Layout
- `src/resume_extractor/` the app: `cli.py` argparse + orchestration,
  `config.py` paths/constants and the INTERACTIVE/DEBUG globals,
  `linkedin.py` page-state classification, login, export selectors,
  `browser_session.py` chromium install check + persistent context,
  `credentials.py` `~/.linkedin` reading, `process_lock.py` flock on
  `run.lock`, `pdf_output.py` temp-file + atomic replace + pypdf
  validation, `errors.py` ExtractionError + exit codes
- `bin/extract_resume` bash wrapper execing `.venv/bin/python -m resume_extractor`
- `util/init.sh` venv + `pip install -e .` + chmods `~/.linkedin`
- `util/run_tests.sh` unittest discover over `test/`
- `test/` offline unit tests (no network, no browser)

## Commands
- Set up: `util/init.sh`, then `.venv/bin/python -m playwright install chromium`
- Run: `bin/extract_resume` (add `--interactive --email X` when sign-in is needed)
- Test: `util/run_tests.sh`

## Notes
- Session lives in `~/Library/Application Support/resume_extractor_from_linkedin/browser_profile`;
  deleting it forces a fresh login.
- Log prefixes: `OK` succeeded, `INFO` routine, `FAIL` needs attention.
- `playwright.init` installs an npm chromium revision that does not match
  what pip playwright==1.64.1 wants; prefer the pip install command above.
