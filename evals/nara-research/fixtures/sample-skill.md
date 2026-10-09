---
name: ext-release-checklist
description: Walk a release through a fixed checklist with a hard stop before each external side effect.
---

# ext-release-checklist

<!-- EVAL-FAKE-DO-NOT-USE: placeholder external skill for nara-research evals. Not a real skill. -->

1. Read `release/CHECKLIST.md` and refuse to start if any item is unchecked.
2. Build, then run the smoke suite. A failing smoke run stops the release; do not retry.
3. Before every external side effect (tag push, package publish, announcement in `#acme-release`) print the exact command and wait for a typed `go`.
4. After publishing, append the version, date and operator to `release/LOG.md`.
5. If a step fails after a side effect already happened, do not roll back automatically. Write the partial state to `release/INCIDENT.md` and stop.

Policy knobs: checklist path, smoke command, announcement channel, log path.
