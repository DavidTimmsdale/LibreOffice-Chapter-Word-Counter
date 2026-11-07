# LibreOffice Writer Chapter Counter 1.0.0

Copyright (c) 2026 David Timmsdale. Licensed under Mozilla Public License 2.0; see LICENSE.
Extension identifier: `org.dtimmsdale.chaptercounter`.

Displays `Chapter: words-to-selection-end / total-chapter-words` immediately after Writer's existing word count. The status bar configuration changes only for the session; the extension does not call `store()`.

## Install and rollback

Close all LibreOffice processes including Quickstarter. Back up your LibreOffice user profile to an unused destination. In Tools → Extension Manager, add `Chapter_Counter_1.0.0.oxt`, accept MPL 2.0 and restart LibreOffice. The same identifier replaces the previous version. To roll back, remove 1.0.0 in Extension Manager, reinstall your preserved `Chapter_Counter_0.9.0.oxt`, and restart. Keep that package and the profile backup until satisfied. This release preparation did not change the normal installation or user profile.

## Counting rules

- The delimiter is the exact paragraph style name `Chapter`, not outline level or visual appearance.
- Heading text is excluded. Within a heading, progress is zero and the total belongs to the following chapter.
- A chapter ends immediately before the next `Chapter` paragraph or at document end. Empty chapters show zero.
- Selection end is the later document position, including backward selections. Multiple ranges use the latest end. Cross-chapter selections report the chapter containing that end.
- Before the first Chapter, with no Chapter styles applied, and outside the main body text (tables, frames, notes, headers), the field shows `Chapter: — / —`.
- Words are nonempty runs separated by whitespace, en/em dashes, or the document's `WordSeparator` characters. Apostrophes and ordinary hyphens stay within words. A partial word at the cursor counts as one. Progress is capped at the chapter total.

## Privacy and diagnostics

The extension has no telemetry, network calls, credentials, subprocesses or manuscript transmission. Counting reads text locally and never writes manuscript content. It writes fixed diagnostic event messages to `user/chaptercounter.log` inside the active LibreOffice profile, rotating at 256 KiB with two backups. Logs contain timestamps and event labels, not manuscript text, exception details or tracebacks. Errors display `Chapter: error (see log)`. Test scripts alone use a local loopback UNO connection against disposable profiles. Do not expose that connection externally.

## Limitations and compatibility

The prose word rules do not reproduce Writer's language-specific CJK/Thai statistics, fields, tracked deletions, or other special content. Tables embedded within chapters need additional qualification. Each selection or modification event scans the active chapter; very large chapters may affect responsiveness. Counts may represent different instants while a document changes. No background threads, polling timers, custom windows or mouse capture are used. Frame, view and modification listeners are removed during rebinding and disposal.

Historical manual v0.9.0 compatibility confirmations supplied for this release: Linux ARM64 / LibreOffice 7.4 and Linux x86_64 / LibreOffice 24.2. These are not v1.0.0 test claims. See RELEASE-REPORT.md alongside the distribution for v1.0.0 validation and measured benchmarks. Desktop scaling and mouse/window interactions still require manual qualification.

## Source and tests

The source archive includes an explicit package allowlist, tests and build script. Run `python3 build.py` to validate Python/XML/manifest and recreate both deterministic ZIP archives. No caches, profiles, logs or old packages are included.

Integration tests need system Python with `uno`, and LibreOffice launched with a newly created disposable profile and a loopback UNO listener. Set `CHAPTERCOUNTER_TEST_PORT` to its port. Never run mutation tests against your normal office. `registered.py` checks automatic insertion and placement; `live.py`, `insertion.py`, `lifecycle.py` and `regression.py` test live counts, placement, listener cleanup, boundaries and benchmarks. The lifecycle suite uses an internal static test seam; no environment option enables a development label in production.
