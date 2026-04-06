# New Window Prompt Template (For Batch Work)

Use this template in each new task window.

## Scope
- Read `BATCH_MANIFEST.csv` as the task list.
- I will tell you which batch to run (for example: `do B014`).
- Before editing, print the exact file list for the requested batch and wait for confirmation.

## Required Rules
1. Follow `DOC_STYLE.md` exactly.
2. PURPOSE block must be immediately below routine declaration.
3. Use declaration comments in `!! [units] description` format.
4. Keep accurate existing descriptions when possible.
5. Do not change runtime logic.
6. Keep this window limited to the batch file list only.
7. Keep batch size at 12 files max.
8. Use module-first ordering (module anchor before dependent routines).

## Output Requirements
- Produce exactly one commit for this batch.
- Commit message: `docs(batch-XX): normalize purpose + variable docs for <family>`
- Report:
  - files changed,
  - checks run,
  - any ambiguous variables left with `[n/a]`.
