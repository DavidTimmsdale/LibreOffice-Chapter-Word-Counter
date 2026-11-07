# Release validation report — 1.0.0

Date: 2026-11-06. Author: David Timmsdale. Identifier: `org.dtimmsdale.chaptercounter`.

## Disposition

Pre-publication audit record: public release artifacts prepared; all available automated tests pass at audit time. Publication status is recorded on GitHub. v0.9.0 and original project files preserved. Validation is limited to Linux ARM64, LibreOffice 7.4.7.2, system Python 3.11 UNO, headless backend. Manual desktop qualification and v1.0.0 testing on Linux x86_64 / LibreOffice 24.2 remain outstanding; this is not a claim of universal release readiness.

Historical manual v0.9.0 confirmations supplied by the release requester: Linux ARM64 / LibreOffice 7.4; Linux x86_64 / LibreOffice 24.2. The second environment was not available for v1.0.0.

## Test results

Installed the actual OXT with `unopkg` into a fresh disposable profile, then tested its real registered controller via loopback UNO. A fresh disposable test profile was used. No normal installation, normal profile, or manuscript was opened or modified. The initial sandbox-only source installation and loopback connection failed due to process/socket restrictions; approved execution outside the sandbox succeeded. These infrastructure failures were not treated as passes.

- `registered.py`: PASS automatic job insertion, exact word-count placement and actual accessible initial label. Adapted the old development-label assertion for the production initial display.
- `live.py`: PASS real displayed counts, heading exclusion, chapter start/end, backward cross-chapter selection, insert/delete, modification events, style removal/restoration, independent documents and read-only counting.
- `insertion.py`: PASS exact placement and idempotence.
- `lifecycle.py`: PASS rebinding, listener removal, repeated disposal, mouse pass-through, documented word rules. Added regression for clearing stale displayed counts on unsupported-model rebinding; production initialization label replaces the obsolete TEST assertion.
- `regression.py`: PASS missing Chapter style, consecutive empty chapters, exact chapter boundaries, forward/backward cross-chapter selections, progress bounds and 10,000/30,000-word totals.
- All existing executable test suites were run from the release copy; `connection.py` is their shared helper. No baseline tests were edited.
- Python syntax, all XML/XCU, manifest targets, ZIP CRCs, unique member names, package allowlist, licence equality and archive metadata: PASS.

The first benchmark run failed because the fixture body inherited the Chapter style. It was fixed by explicitly styling the body Standard. All final suites exited zero. Seven synchronous counting calls per size, through a local UNO bridge, on synthetic whitespace prose; timings include bridge overhead, exclude selection/typing event latency, and are not performance guarantees:

```
BENCHMARK 10000 words: median 16.57 ms; max 18.99 ms; 7 synchronous calls
BENCHMARK 30000 words: median 31.64 ms; max 31.98 ms; 7 synchronous calls
```

## Code and privacy review

Preserved the exact `Chapter` delimiter, word rules and placement after `.uno:StateWordCount`. Progress is defensively capped at its chapter total. Removed visible development labels and the environment-driven static mode; internal V09/statusbartest registration names remain for upgrades. Fixed stale counts when no Writer model is attached. Reviewed selection/modification/frame listeners and disposal; lifecycle tests verify cleanup. Exception handlers report fixed event labels without exception values or tracebacks. Log propagation is disabled. A failure to create the profile log can still prevent component initialization; no alternate writable path is attempted.

No extension network, telemetry, subprocess or manuscript-transmission API was found. Logs are bounded local event diagnostics, not manuscript records. Test-only UNO socket access is loopback. All source, XML, build, test, documentation, historical release members and existing logs were inspected; 44 baseline files/archive members were scanned, including two bytecode caches. The containing Git repository has no historical objects for this project path (the project is untracked), so there is no project history to audit. Unrelated parent-project working changes were not touched.

Security findings below contain file, line, category and remediation status only; no discovered values are reproduced:

| File | Line | Category | Remediation status |
|---|---:|---|---|
| src/chaptercounter.py | 69, 93, 115, 128, 151, 157 | Exception diagnostics could expose private paths or exception data | Release copy uses fixed messages; tracebacks removed; propagation disabled |
| original/chaptercounter.py | 75–76 | Legacy home-directory error logging and raw exception data | Historical original preserved; excluded from both public archives |
| test-results/development.log | 12–20 | Private diagnostic tracebacks and cache paths | Historical log preserved; excluded from public archives |
| src/__pycache__/chaptercounter.cpython-311.pyc | 0 | Compiled cache metadata | Excluded from public archives |
| tests/__pycache__/connection.cpython-311.pyc | 0 | Compiled cache metadata | Excluded from public archives |
| tests/connection.py | 8 | Loopback connection endpoint | Retained solely as documented disposable-profile test infrastructure |
| src/*.xml, src/*.xcu, src/META-INF/manifest.xml | 2, 7 | Public XML namespace identifiers | Reviewed; retained |
| README.md, TEST-REPORT.md | 3, 11, 30, 47–60 | Historical environment identifiers, paths and reference URLs | Baseline preserved; replaced by public release documentation |

No passwords, API keys, private keys, tokens, credentials, private connection strings, emails, private hostnames, account identifiers or personal absolute home paths were detected in the public artifacts. Public author/extension identifiers are intentionally retained. Numeric software versions and XML namespace URLs are not network activity. Historical logs and cache files are excluded regardless of whether they contain sensitive values.

Final audit opened the actual OXT (9 entries) and source ZIP (19 entries), read every member, checked metadata and explicit membership, parsed every Python/XML file, checked manifest references, and checked for credentials, email/personal paths, network/transmission code and embedded binary data. ZIP names are relative, with fixed timestamps and permissions, no comments or extra fields. No profiles, private logs, caches, unrelated source, old packages or filesystem ownership metadata are included.

## Licence and reproducibility

Complete official MPL 2.0 downloaded from [Mozilla](https://www.mozilla.org/media/MPL/2.0/index.txt), including both exhibits, unchanged in LICENSE and the OXT. David Timmsdale attribution is in source, metadata, README and changelog. Source is supplied in the public source archive. `python3 build.py` rebuilds both archives from explicit allowlists with deterministic timestamps and permissions. SHA256SUMS covers both distributable archives; verify with `sha256sum -c SHA256SUMS` from this directory.

The preserved v0.9.0 OXT SHA-256 still equals its existing SHA256SUMS entry:
`c5cdb557cebbf85353dc5de6ff9af2896cb1189d668a7c3accb53a8a6f9c2383`.

## Remaining limitations

Manual desktop mouse/window behavior, accessibility layout at different scales, non-main-body stories, embedded tables, language-specific CJK/Thai counts, fields and tracked deletions remain unqualified. Counting rescans the active chapter on events and can affect responsiveness in larger manuscripts. No native Writer statistics parity is claimed. No v1.0.0 validation on LibreOffice 24.2 was performed. Installation/rollback is documented but rollback in the normal profile was deliberately not exercised.
