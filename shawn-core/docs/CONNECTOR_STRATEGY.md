# Connector Strategy

## Recommended connectors
1. Google Drive: source files and project archives.
2. Gmail: deadlines, counsel communications, run sheets, leads.
3. Google Calendar: dated commitments and review cycles.
4. GitHub: version-controlled tools.
5. Local filesystem: actual project repo and exports.
6. Browser/Playwright: website/testing/customer-view validation.
7. SQLite: commitments, evidence indexes, lead trackers.

## Permission model
- Start read-only.
- Draft before send.
- No irreversible action without explicit approval.
- Never publish private source files.

## Connector risks
- prompt injection from external documents
- accidental data disclosure
- duplicate stale files
- over-trusting recent modified timestamps
