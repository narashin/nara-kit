# Claim check: a second reader for change explanations

The writer of an explanation believes its own story, so it does not catch the claims it filled in to make the story flow. A claim check hands the finished file to a reader that did not write it. The reader returns suspicion candidates; it does not fix the file and does not rule on the document. The user decides what to fix.

## When it runs

| Audience | Claim check |
|---|---|
| Non-tech, External | Always, before delivery |
| Tech peer, New member | Only when asked ("검증해", "근거 확인", "verify") |

It applies to change scope only, because it needs the pinned `base..head`.

## How it runs

Spawn a fresh subagent with no part of this conversation: give it only the prompt below with the four slots filled. Never tell it which claims you doubt; a reader handed your suspicion confirms it.

No subagent tool on this host: run the same prompt yourself in a new step and label the receipt line `claim check (same context, weaker)`.

```text
You are checking an explanation document that someone else wrote about a code change. You did not write it. List claims that their evidence does not fully support. You produce suspicion candidates for a human; you do not rule on the document overall and you do not edit it.

Document: <absolute path to the HTML file>
Repository (read-only, never modify, never checkout): <absolute repo path>
Pinned comparison: base <base sha>, head <head sha>. Read code with `git -C <repo> show <sha>:<path>`; ignore the working tree. `base:path:line` means the base version.
Repository role: <what this repo is, e.g. "frontend only; the backend lives elsewhere">

1. Extract every factual claim in the visible text: headings, lead paragraphs, list items, table cells, captions, quiz answers. Skip framing sentences with no factual content.
2. For each claim, open the code it cites, or the code that would have to show it if uncited. Read the surrounding callers, rendering and data model until you know what the code does.
3. Flag a claim when any of these hold:
   - It describes base behavior the base code does not show, including a description that reads like the inverse of head rather than what base renders.
   - It carries a word that limits scope or count (only, all, none, single, no longer, and their equivalents in the document's language) that the code does not back.
   - It states behavior of another system (backend, external service, another repo) that this repository cannot show. On-screen notice text is evidence of what the screen says, not of where the work happens.
   - It reads a test fixture's input as something that happens in the real flow.
   - The cited lines exist but show less than the claim says.
4. Do not flag wording or style. Do not flag a claim you confirmed.

Output, under 500 words:
- Each flagged claim: the sentence quoted exactly, the rule it breaks, and the evidence as `sha:path:line` with one line on what that code does.
- One line: claims extracted, flagged, confirmed, undecided.
- Up to 3 undecided claims, with why.
```

## After it returns

- Recheck each flagged claim yourself against the cited code before reporting it; drop one only when the code confirms the original sentence, and say so.
- Do not rewrite the file on your own. List the flagged sentences in the receipt and ask which to fix. A fix the user approves follows the evidence rules in [change-html](change-html.md).
- Receipt line: `claim check: <flagged> flagged · <undecided> undecided` or `claim check: skipped (<audience>, not requested)`.

## What it does not catch

A sentence that is true in code but misread by this audience passes. "The old screen showed the last approval stage" is true, and a reader who cannot tell a stage from an approver still reads it as "one person". Only a reader who knows the domain catches that, so the receipt never presents a clean claim check as a verified document.

Measured 2026-11-05 on one planner-facing PR explanation with three known false claims: a fresh reader caught two of them and found one more the user had missed (on-screen notice text written up as where approval happens), both with and without hint words in its prompt. The third, true-but-misread kind was left undecided. On the corrected version it raised three flags, each backed by code. One run per condition: headroom, not proof.
