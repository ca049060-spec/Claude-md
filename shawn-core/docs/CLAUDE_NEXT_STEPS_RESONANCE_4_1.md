# Claude Next Steps — Resonance Phase 4.1

## Current state

Phase 4.1 is installed in the repo.

The first current-signal record is frozen in:

`datasets/prospective_signal_registry.json`

Signal id:

`psig-20260616-ai-generated-content-flood`

## Do not rebuild

Do not rerun old build prompts.
Do not move to Phase 5 yet.
Do not change the model until the registry has reviewed signals.

## Commands to run locally

From repo root:

```cmd
cd C:\Users\spias\Claude-md
git pull
python shawn-core\scripts\score_live_signal.py psig-20260616-ai-generated-content-flood
python shawn-core\scripts\review_matured_signals.py
python shawn-core\scripts\audit_hindsight_leakage.py
python shawn-core\scripts\compare_to_baselines.py
```

## Expected output before 2026-08-15

- score script prints the frozen signal details
- review script says no matured signals yet
- audit script says no obvious leakage
- baseline script says baseline comparison is not valid yet

## Claude prompt to use next

```text
Load shawn-core.

Do not rebuild anything.

Run the Phase 4.1 verification commands:

1. python shawn-core\scripts\score_live_signal.py psig-20260616-ai-generated-content-flood
2. python shawn-core\scripts\review_matured_signals.py
3. python shawn-core\scripts\audit_hindsight_leakage.py
4. python shawn-core\scripts\compare_to_baselines.py

Then tell me:
1. Did the registry load?
2. Did the frozen signal print?
3. Are any matured signals due?
4. Did the audit find leakage?
5. Is baseline comparison valid yet?
6. What is the one next action?

Do not create files.
Do not modify files.
Do not move to Phase 5.
```

## Next real action

Wait for the first review date or register a second current public signal using the same no-hindsight protocol.
