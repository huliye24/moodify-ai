# MFY-CR-P01 — Branch Ancestry

Verified read-only on 2026-08-17 against the live repository.

```text
origin/main  = fa88b0b9  (huliye24/moodify-ai; PR #15 asset-extraction merge)
moodify/main = 5ccb3c6e  (huliye24/moodify stub, "Initial commit" — not the working line)
pr20_head    = 19d8a772  (codex/moodify-1.0-release-convergence; CLOSED unmerged 2026-08-11)
pr21_head    = e66cbf9d  (codex/mfy-data-factory-001; OPEN)
android_2_0_head (local) = 5bbc4972
android_2_0_head (moodify remote) = 0438c22f
classic_reconstruction_head = 5bbc4972
```

```text
PR20_IN_PR21         = NOT_MEANINGFUL (PR #20 closed; both PRs evaluated against HEAD instead)
PR20_HEAD_IN_HEAD    = YES  (19d8a772 is an ancestor of 5bbc4972)
PR21_HEAD_IN_HEAD    = YES  (e66cbf9d is an ancestor of 5bbc4972)
ANDROID_2_0_IN_CLASSIC = YES (classic branch created directly from android-2.0 HEAD, no squash, no rebase)
UNABSORBED_COMMITS   = none for PR #20/#21 heads
LOCAL_UNPUSHED       = 72c47c4d, 5bbc4972 (android-2.0 local HEAD is 2 commits ahead of moodify remote)
```

Method: `git merge-base --is-ancestor <oid> HEAD` for both PR heads; `git switch -c`
for the new branch (no squash / no rebase / no merge of historical PRs).

The new branch was created from the current HEAD of `codex/moodify-android-2.0`
(5bbc4972), NOT from `origin/main` (fa88b0b9). No wholesale merge of PR #15/#19
was performed; PR #20/#21 content is absorbed via the working line's own history.
