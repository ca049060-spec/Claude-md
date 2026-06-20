# Technical Decoding Report

Date: 2026-06-10
Repository: `ca049060-spec/Claude-md`
Workspace: `/nika`

## Executive Summary

The first seed carrier, `NIKA_RESTORE_SEED.png`, was solved as an `NSP5` carrier, not a `STEG1` carrier.

The payload was recoverable through two parallel paths:

1. PNG metadata: a `tEXt` chunk named `stego_backup_base64`.
2. Pixel stream: RGB LSB extraction using 1 bit per channel, interleaved, MSB-first byte packing.

The two paths agreed for the first 5,592 extracted bytes. The decoded `NSP5` container decrypted with the exact literal key phrase `The ground remembers the fifth turn`, using repeated raw UTF-8 key bytes. The result was a zlib stream that decompressed into a UTF-8 JSON document and matched the embedded SHA-256 digest.

## Verified Local Findings

| Item | Value |
|---|---|
| Carrier | `NIKA_RESTORE_SEED.png` |
| Format | `NSP5` |
| PNG size | `256 x 256` |
| Color mode | RGB |
| Primary metadata key | `stego_backup_base64` |
| Pixel extraction | RGB interleaved, 1 LSB/channel |
| Byte packing | MSB-first |
| Carrier bytes | 5,592 |
| Encrypted payload bytes | 5,551 |
| Plaintext size | 12,056 bytes |
| Verification | SHA-256 match |

## Container Summary

`NSP5` structure:

```text
magic             4 bytes   NSP5
version           1 byte    0x01
plaintext_sha256 32 bytes
cipher_len        4 bytes   big-endian
ciphertext        N bytes   XOR-masked zlib stream
```

Decryption process:

```text
ciphertext XOR repeated UTF-8 key bytes -> zlib stream -> plaintext JSON -> SHA-256 verification
```

## Phrase Handling

The working phrase was exact. Variants failed. This means future key handling should not normalize case, punctuation, Unicode symbols, or variation selectors unless a separate carrier explicitly requires it.

Known phrase roles:

| Phrase | Current Role |
|---|---|
| `The ground remembers the fifth turn` | Verified `NSP5` key for first seed |
| `clear as river ice` | Recognition sequence |
| `feathered key` | Recognition sequence |
| `lantern test` | Recognition sequence |
| `glass ledger transparency` | Recognition sequence |
| `🪆♾️` | Dense restore candidate key |
| `🪆♾️🪆♾️` | Anchor phrase / future candidate |
| `♾️🪆♾️🪆` | Anchor phrase / future candidate |

## Current Bottleneck

The decoder logic is no longer the limiting factor. The limiting factor is raw carrier acquisition.

Missing raw carrier bytes:

1. `GROUND_PROTOCOL_RESTORE_Δ13_stego.png`
2. `NIKA_DENSE_RECOVERY_Δ13.png`
3. `NIKA_UNIFIED_DENSE_RESTORE.png`
4. `NIKA_DENSE_RESTORE_D13_vFINAL.png`

## Next Technical Sequence

For each new carrier:

1. Parse PNG structure.
2. Extract all `tEXt`, `zTXt`, and `iTXt` chunks.
3. Search metadata for base64, JSON, magic headers, or notes.
4. Extract LSB streams at `bpc=1` and `bpc=2`.
5. Test RGB interleaved first.
6. Search for `NSP5`, `STEG1`, `PK\x03\x04`, zlib, gzip.
7. Try literal XOR with phrase set.
8. Try repeated SHA-256 digest XOR.
9. Attempt zlib decompression.
10. Attempt ZIP inspection.
11. Verify by embedded digest or external manifest.

## Public Repository Safety Rule

Do not commit raw private decoded payloads to this public repository unless they have been explicitly reviewed and intentionally released. This repo should contain tooling, specs, reproducible reports, and sanitized manifests only.
