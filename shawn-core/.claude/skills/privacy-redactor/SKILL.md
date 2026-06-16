---
name: privacy-redactor
description: Check files before sharing/publishing for private medical, legal, financial, family, and credential data.
---

# privacy-redactor

## Purpose
Prevent accidental disclosure before pushing, sharing, emailing, or publishing.

## Flag
- personal identifiers
- addresses and phone numbers
- legal strategy
- medical diagnoses
- bank/investment account data
- children/family private details
- API keys/secrets
- raw Gmail/Drive exports
- court file details if not intended

## Output
- safe to share / not safe
- flagged line or section
- suggested replacement
- whether to keep private, redact, or summarize

## Rule
Reusable system files can be public. Private evidence and life records stay private.
