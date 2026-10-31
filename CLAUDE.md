# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git, commits and pull requests

These rules apply to every session, also to Claude Code on the web.

- **Author:** commits and PRs must look as if the maintainer made them alone. Before the first commit run `git config user.name "dktzde"` and `git config user.email "dktzde@users.noreply.github.com"`. No `Co-Authored-By`, no "Generated with Claude" in commits, PR texts, issues, changelog or README.
- **Branches:** no `claude/` prefix where the environment allows it (Claude Code on the web may force `claude/…`; that is accepted).
- **One topic = one branch = one PR.** One commit per sub-topic, test after each commit. Plan the commit split before the first push. Never force-push a pushed branch; fix mistakes with `git revert`.
- **This is a fork of `MTTPoll/handwise-ha`.** Open PRs against our fork with `gh pr create --repo dktzde/ha-mgc-mower --base main`, otherwise they land at the upstream. Branches for PRs to the upstream start from `upstream/main`, use only `## Unreleased` in the changelog and never contain `STATUS.md` or `CLAUDE.md`. PRs to the upstream only after a test on the real device and explicit approval by the maintainer.
- **Merge** only when the maintainer explicitly asks, always with a merge commit (no squash), so every commit can be reverted on its own.
- **Versions:** bump only for user-facing changes and only on our `main`; documentation-only changes get no new version. Change the version everywhere at the same time.
- **Changelog:** every version gets its date as `<sub>YYYY-MM-DD</sub>` under its heading. Versions by earlier authors are separated by a `---` line and a bold sentence naming them.
- **Language:** everything in the repository is English (code, comments, docs, commits, PR and issue texts). Commit messages in the imperative, e.g. `feat(scope): …`, `fix: …`, `docs: …`, `chore: …`, `ci: …`; in PRs to the upstream follow its style.
- **No secrets or private data** (tokens, passwords, IP addresses, radio addresses, serial numbers, entity IDs) in the repository; use placeholders.
- **README:** a credit line for Claude Code only after asking the maintainer.
- **Handover:** keep `STATUS.md` (create it if missing) with the current state, next steps, known issues, decisions and key files. Record what runs on the device with date and time, what was checked and what not. Update it after every step.
