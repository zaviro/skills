---
name: remote-handoff
description: Prepare the current discussed project change in GitHub for later local jj integration and machine-specific validation. Use whenever the user invokes /remote-handoff, asks to send the current plan/minimal implementation to GitHub for local verification, or wants cloud work handed back as a remote branch/change. Create a remote candidate branch and leave only the context the local agent actually needs; never merge it remotely by default.
---

# Remote Handoff

Turn the current conversation into a small remote candidate change that a local jj workflow can fetch, inspect, test on the real machine, rewrite if needed, and accept or discard.

## Resolve the target

Infer the repository and base branch from the current conversation before doing anything else.

Choose the base in this order:
1. A branch explicitly named for the current work.
2. The active integration branch clearly implied by the current discussion or repository workflow.
3. The repository default branch when there is no stronger evidence.

Read the remote state first and branch from the latest tip of that base. Do not choose an unrelated feature branch merely because its commit timestamp is newer.

If the repository itself cannot be identified from the conversation, connected project context, or available checkout, do not guess.

## Create the candidate

Create a branch named `cloud/<short-task-slug>` from the resolved base tip.

Treat the branch as transport for one logical jj change:
- implement the smallest complete version of the discussed solution;
- avoid unrelated refactors, formatting churn, dependency updates, or speculative extras;
- keep the final branch to one commit when practical; squash cloud exploration commits before handoff when that does not destroy information needed for review;
- never merge the branch into the base remotely;
- do not open a PR by default. If the environment requires a PR, leave it as Draft and do not merge it.

If a branch for exactly the same current handoff already exists, update that branch instead of creating parallel variants. Otherwise use a distinct slug rather than overwriting unrelated work.

## Validate only what the cloud can actually validate

Run cheap, relevant checks available in the remote environment, such as formatting, static analysis, unit tests, evaluation, or build checks.

Do not treat cloud checks as proof of host-specific behavior. For machine configuration, hardware integration, services, desktop behavior, networking, secrets, or other environment-dependent work, explicitly leave the real validation to the local agent.

## Leave the handoff in the commit description

The commit itself is the durable handoff. Keep its description terse because the local agent can read the diff.

Use this shape, omitting sections that add no information:

```text
<short change summary>

Handoff:
- Context: <only non-obvious design intent or constraint needed to interpret the diff>
- Validate locally: <specific commands and/or runtime behavior that must be checked on the real machine>
- Unverified: <only unresolved assumption, environment dependency, risk, or blocker>
```

Rules:
- `Validate locally` is normally required for this workflow.
- Omit `Context` when the diff and commit title already make the intent obvious.
- Omit `Unverified` when nothing material remains unverified beyond the listed local validation.
- Do not narrate implementation details that are obvious from the diff.
- Do not copy the whole conversation, generic rationale, or alternative designs into the commit.
- Mention cloud checks only when their result materially changes what the local agent should do next.

## Finish

Push the candidate branch and report only the identifiers needed to retrieve it, normally:

```text
branch: cloud/<short-task-slug>
base: <base-branch>
```

If useful, add the exact commit identifier. Do not claim the change is complete until the required local validation has happened.
