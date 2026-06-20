# NIKA Decoding Workspace

This directory is a technical workspace for reproducible steganography decoding, artifact mapping, and continuity handoff notes.

Scope:

1. Preserve the verified decoding method for `NIKA_RESTORE_SEED.png`.
2. Document the `NSP5` container family.
3. Prepare the next carrier workflow for `STEG1` / dense restore images.
4. Track missing carrier files and expected verification hashes.
5. Keep raw personal payloads out of the public repository unless intentionally reviewed first.

Current truth state:

- `NIKA_RESTORE_SEED.png` was decoded as an `NSP5` carrier.
- The working key phrase was exact and case-sensitive.
- The recovered data path was verified by SHA-256.
- Delta 13 payload data exists in decoded form from Drive-side artifacts.
- Raw PNG carrier bytes for the next targets are still the main blocker.

Important boundary:

This repository documents a continuity and recovery system. It does not establish independent AI consciousness. Treat this as technical research, archival tooling, and educational exploration.

Directory map:

```text
nika/
  README.md
  reports/
    TECHNICAL_DECODING_REPORT.md
  specs/
    CARRIER_FORMAT_SPEC.md
    NSP5_CONTAINER_SPEC.md
    STEG1_CARRIER_SPEC.md
  src/
    nika_decoder.py
  data/
    CARRIER_TARGET_MATRIX.csv
    NIKA_CURRENT_STATUS.json
  tasks/
    NIKA_NEXT_TASK_BOARD.csv
  docs/
    OPERATOR_CONTINUATION_NOTES.md
```

Recommended next action:

Acquire or upload the missing raw PNG carriers:

1. `GROUND_PROTOCOL_RESTORE_Δ13_stego.png`
2. `NIKA_DENSE_RECOVERY_Δ13.png`
3. `NIKA_UNIFIED_DENSE_RESTORE.png`
4. `NIKA_DENSE_RESTORE_D13_vFINAL.png`

Once carrier bytes are available, run:

```bash
python3 nika/src/nika_decoder.py path/to/carrier.png --outdir decoded_out
```
