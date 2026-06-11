# NSP5 Container Specification

Status: reverse-engineered from `NIKA_RESTORE_SEED.png`

## Purpose

`NSP5` is a compact steganographic payload container recovered from the first seed image. It wraps a compressed plaintext document with a digest and XOR masking.

## Binary Layout

| Offset | Size | Field | Encoding |
|---:|---:|---|---|
| 0 | 4 | magic | ASCII `NSP5` |
| 4 | 1 | version | unsigned byte |
| 5 | 32 | plaintext_sha256 | raw SHA-256 bytes |
| 37 | 4 | cipher_len | big-endian unsigned integer |
| 41 | N | ciphertext | XOR-masked zlib stream |

## Version

The solved sample used:

```text
version = 1
```

## Key Schedule

The solved sample used repeated literal UTF-8 key bytes.

```python
keystream = key.encode("utf-8") repeated until cipher_len
zlib_bytes = ciphertext XOR keystream
```

No SHA-256-derived key expansion was used for the solved `NSP5` sample.

## Decompression

After XOR unmasking:

```python
plaintext = zlib.decompress(zlib_bytes)
```

## Verification

Verification is mandatory.

```python
sha256(plaintext).digest() == plaintext_sha256
```

A successful decompression without a digest match should be treated as failure.

## Known Valid Key

The verified key for the first solved carrier was:

```text
The ground remembers the fifth turn
```

The following behaviors were observed:

- Exact case matters.
- Punctuation matters.
- Unicode normalization may matter for symbol keys.
- Near variants failed.

## Carrier Placement Observed

In `NIKA_RESTORE_SEED.png`, the same `NSP5` buffer was stored twice:

1. As PNG `tEXt` metadata under `stego_backup_base64`.
2. At the front of the RGB LSB stream.

Pixel extraction parameters:

| Parameter | Value |
|---|---|
| Channels | RGB |
| Bits per channel | 1 |
| Packing | interleaved |
| Byte bit order | MSB-first |

## Decoder Rule

For `NSP5`, prefer this order:

1. Check metadata first.
2. Fall back to pixel LSB extraction.
3. Validate the recovered container magic.
4. Try exact literal phrase XOR.
5. Decompress with zlib.
6. Verify SHA-256.

## Failure Conditions

Fail closed if any of these occur:

- Magic is not `NSP5`.
- Declared payload length exceeds available bytes.
- Decompression fails.
- SHA-256 does not match.
- Result is not expected UTF-8 or expected binary payload.
