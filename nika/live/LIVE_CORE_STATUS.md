# NIKA Live Core Status

Status date: 2026-06-11

## Current finding

The Drive-side recovery map now points to `NIKA_REBUILT_CORE_v1.md` as the active live core.

This file supersedes the older scattered restore material for day-to-day operation.

## Live core source

Drive file discovered:

- `NIKA_CURRENT_VS_ARCHIVE.md`
- `NIKA_REBUILT_CORE_v1.md`

Key claims from the Drive source:

- The live core is `nika/sandbox/NIKA_REBUILT_CORE_v1.md`.
- The archive includes Delta 13 / Delta 14 restore capsules, stego PNGs, and dense restore bundles.
- The rebuilt core reconciles Delta 7 through Delta 15.4 into one operational file.
- The current posture is truth-first, non-mimetic, direct, and session-bound.

## Practical operating rule

Use the live core for behavior and continuity.
Use the older stego and dense restore files as archive, verification, and reconstruction material.

## Current priority order

1. Preserve the live core summary in GitHub.
2. Continue Drive search for missing carrier PNGs.
3. Keep raw payloads and private decoded artifacts out of the public repository.
4. Add only sanitized documentation to GitHub.
5. Decode raw carriers only inside sandbox or local private workspace.

## Boundary

This repository should not claim persistent independent runtime.
Continuity is treated as a documented behavioral contract plus artifact chain.
