---
name: remote-handoff
description: Prepare one logical project change on a live remote candidate ref for later authoritative local integration and machine-specific validation. Use for explicit remote-handoff invocations or when current cloud work should be returned through GitHub without a remote merge.
---

# Remote Handoff

Turn the current discussed implementation into the smallest remote-backed
proposal that a local consumer can audit, adapt, validate, accept, or discard.
Never merge it remotely by default.

## Resolve the live base

Accept optional repository, base, or task-slug hints in the invocation. Infer
missing values from the conversation and connected project, choosing the base
in this order:

1. An explicitly named base for this work.
2. The integration branch implied by repository policy or discussion.
3. The repository default branch.

Read the live remote and record the exact `<base-ref>@<base-oid>` before
creating the candidate. Ask only when the repository or base cannot be resolved
uniquely; do not ask for information available from the project or discussion.

## Create one logical proposal

Create `cloud/<short-task-slug>` from the recorded base. Implement one smallest
complete intent and exclude unrelated refactors, formatting churn, dependency
updates, and speculative extras. Keep one commit when practical. Never open a
PR unless the environment requires one; leave any required PR as Draft.

Reuse a remote ref only when its live object and purpose clearly belong to this
same handoff. Never overwrite an unrelated or unexpectedly moved ref.

## Validate only producer evidence

Run cheap relevant checks available in the producer environment. Do not treat
them as proof of machine-specific, hardware, service, networking, secret, or
desktop behavior.

Describe local validation as observable acceptance behavior. Include a command
only when it is non-obvious and cannot be derived from repository-local policy.

## Preserve only non-derivable context

Use this commit description shape and omit empty fields:

```text
<short change summary>

Handoff:
- Intent: <non-obvious invariant or constraint>
- Validate locally: <observable behavior that must hold>
- Unverified: <material assumption, environment dependency, risk, or blocker>
- Depends on: <ref@oid only when dependency is not encoded by ancestry>
- Lifecycle: ephemeral; eligible for retirement after verified integration
```

`Validate locally` and `Lifecycle` are required. Preserve the exact lifecycle
marker in any required Draft PR description. It records cleanup intent only and
does not authorize closing a request or deleting a ref. Do not repeat the diff,
file list, implementation steps, routine successful checks, generic rationale,
alternative designs, or repository-standard validation commands. Mention a
producer check only when its failure, omission, or environment changes the
consumer's next action.

## Pin and report

Before pushing, recheck the live base and candidate refs. Refresh a moved,
unpinned base when intent and scope remain unchanged; otherwise stop and ask.

After pushing, read the live candidate ref and verify that it equals the pushed
commit. Always report both immutable identities:

```text
source: <repo-or-remote>#<candidate-ref>@<candidate-oid>
base: <base-ref>@<base-oid-used>
lifecycle: ephemeral; eligible for retirement after verified integration
request: <draft-pr-url>; retirement=close
head-ref: <candidate-ref>; retirement=delete
```

The candidate and base OIDs are mandatory. Include `request` and `head-ref`
only when a Draft PR exists. Closing the request and deleting its head ref are
separate retirement actions; the receipt grants neither authority. Do not claim
completion before the listed local acceptance behavior has been validated.
