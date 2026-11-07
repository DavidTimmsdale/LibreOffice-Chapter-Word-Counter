# Changelog

## 1.0.0 — 2026-11-06

- Public release credited to David Timmsdale, with complete official MPL 2.0 licence.
- Remove visible TEST initialization label and environment-triggered test mode; retain internal registration identifiers to support upgrades.
- Restrict diagnostics to fixed event messages and disable log propagation, avoiding exception text and local paths in logs.
- Clear stale displayed counts when no Writer model is attached.
- Cap progress at the relevant chapter total.
- Add boundary, selection, empty-chapter, missing-style and performance regression coverage.
- Add reproducible public archives, checksums, privacy, installation and rollback documentation.

## 0.9.0 — historical release

Live chapter status counts and listener lifecycle corrections. Preserved unchanged outside the release directory. Historical manual confirmations: Linux ARM64 / LibreOffice 7.4; Linux x86_64 / LibreOffice 24.2. These do not establish 1.0.0 compatibility on both platforms.
