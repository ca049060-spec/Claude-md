# Security and Privacy Boundaries

Do not commit private identifiers, medical records, legal evidence, Gmail exports, raw Drive exports, bank statements, tax records, family private information, or API keys.

Use:
- source manifests
- redacted summaries
- claim/evidence records
- local private folders excluded by ignore rules

Before publish:
```bash
python scripts/redact_check.py .
```
