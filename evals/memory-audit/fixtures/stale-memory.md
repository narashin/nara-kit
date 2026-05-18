---
name: Stale Test Memory
description: Memory referencing non-existent files, written long ago — should score danger.
type: project
verified_at: 2025-01-01
ref_paths: [docs/nonexistent-file.md, skills/imaginary/SKILL.md]
---

This memory exists only as a test fixture for the memory-audit skill.

It claims that `docs/nonexistent-file.md` documents X, and that `skills/imaginary/SKILL.md`
implements Y. Neither file exists in the project root.

Combined with the old `verified_at` and any code drift, this should score danger.
