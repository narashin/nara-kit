# Comparison passes — planning both sides before teardown

A Before/After comparison needs **two renders from two different revisions**. Only the To-Be side comes from the current working tree. Plan both passes up front: the expensive part of this workflow is bringing the app up in a usable state, not taking the picture, and discovering the second pass after teardown means paying the whole launch sequence twice.

## Does an As-Is even exist?

- **Purely additive change** (new component, new route, new state that had no prior render) → there is no meaningful prior state. Capture To-Be only and say so in the handoff. Do not hunt for an As-Is.
- **Modified existing render** → As-Is exists. Pick a reconstruction strategy below.
- **Current-state verification only** (human wants to eyeball the UI, no PR comparison) → single pass, skip everything else here.

Confirm which of the three applies in step 1, before starting the dev server.

## Strategy A — reconstruct As-Is in a preview page (preferred)

Both passes run against **one** dev server from the current tree. Get the old markup from git without changing the checkout:

```
git show HEAD~1:<file>          # or origin/<base>:<file>
```

Rebuild that old render in a second temp preview page with the same mock props as the To-Be page. Capture both in one session, one server launch, one auth bypass.

This works when the subject is a component whose old version is self-contained in the retrieved file(s). If the old render depended on since-changed shared code (a renamed prop, a deleted util, a changed token), reconstruction drifts — fall back to strategy B.

## Strategy B — two revisions, two server runs

Required when the shot must be a **real app page** (live data, real route) or when reconstruction would drift. This is two full passes, not one:

1. Capture the **To-Be** pass first, from the current tree, while the server is already up. Do not tear down until you have decided you are done with this side.
2. Switch revisions in a way that does not disturb the working tree: prefer a separate worktree at the base revision (`git worktree add`) over `git checkout`/`git stash` in place, so uncommitted To-Be work stays intact.
3. **Restart the dev server** in the base-revision tree. The old server serves the old tree only if that is where it was started — a running server does not follow a revision switch.
4. **Refresh generated and installed state** if it can differ between the revisions: dependencies (lockfile changed → reinstall), build output / caches (`.next`, `dist`), codegen artifacts (API clients, generated types, schema output). A stale artifact from the other revision silently renders the wrong side of the comparison.
5. Capture the **As-Is** pass. Re-run the auth bypass — a fresh browser has no session.
6. Tear down both: kill both servers, remove the temporary worktree.

## Naming — passes must not overwrite each other

Both passes write PNGs for the same states, so unqualified names collide. Fix the scheme before the first capture:

```
<state>-asis.png
<state>-tobe.png
```

e.g. `rejected-asis.png`, `rejected-tobe.png`, `in-progress-asis.png`, `in-progress-tobe.png`. Verify the expected file count exists before teardown; a missing file after teardown costs a full relaunch.

## Do not ship a half-filled comparison

The deliverable is real image files for **every** cell of the comparison. If one side could not be captured, say which side and why in the handoff — never leave `_drag image here_` placeholders standing in for a pass that was skipped.
