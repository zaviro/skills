---
name: integrate-remote-handoffs
description: Audit and integrate one or more remote handoff candidates into current local work while preserving logical change boundaries, choosing independent or joint validation, publishing an authorized integration target, and retiring consumed remote candidates. Use when work arrives through temporary branches, bookmarks, refs, patches, or forks from another machine, cloud workspace, or agent and Codex must inspect, adapt, validate, accept, publish, or clean up those handoffs.
---

# Integrate Remote Handoffs

Consume arbitrary remote handoff candidates without assuming a branch naming
scheme, version-control system, deployment platform, or candidate count. Treat
repository-local instructions and specialized version-control, build,
deployment, and recovery skills as authoritative.

## Establish authority and a stable baseline

Separate authorization for these effects:

- reading or fetching remote state;
- creating or rewriting local changes;
- moving or publishing an integration target;
- deleting source candidates;
- deploying or activating the result.

Do not infer publication, deletion, force-update, deployment, or cross-machine
authority from a request to inspect or integrate.

Before mutation:

1. Read repository instructions and route to its version-control and validation
   skills.
2. Record the working tree, current logical change, parent, local unpublished
   stack, workspaces, bookmarks or branches, remotes, and operation or reflog
   recovery point.
3. Preserve unrelated and unknown work. Stop when ownership cannot be
   established safely.
4. Distinguish the current working tip from the planned candidate-integration
   tip and record any unrelated descendants between them.
5. Record every candidate's exact remote name and server object ID, then fetch
   only the required candidates.
6. Recheck the server IDs after fetching so a stale tracking ref cannot define
   the integration.

In a strictly read-only audit, do not fetch. Use a live remote lookup to compare
the server object ID with any existing tracking ref, label tracking freshness
and local object availability separately, and stop before integration when the
required object is unavailable locally.

Use parallel read-only reviews when candidates are independent. Isolate
parallel writers with the repository's supported workspace mechanism before
allowing them to edit or run snapshotting version-control commands.

## Build a candidate ledger

Audit every candidate from its actual common ancestor, not only its tip. Record:

| Field | Evidence |
| --- | --- |
| Source | Remote, exact ref, object ID, and freshness check |
| Tracking | Live server ID, local tracking ID, and object availability |
| Boundary | Logical changes and whether each can land or roll back alone |
| Scope | Files, generated artifacts, imports, consumers, hosts, and services |
| Intent | User-visible behavior and invariants the candidate claims |
| Relationship | Dependencies and semantic or textual overlap with local work and other candidates |
| Risk | Credentials, licenses, input locks, migrations, destructive effects, control channels |
| Validation | Static checks, builds, runtime checks, deployment, and recovery needed |

Inspect full diffs and change descriptions. A clean textual merge is not
evidence of semantic compatibility. Check assumptions that may differ between
the producer and consumer environments, including tool versions, option names,
package ownership, import graphs, permissions, and ignored files.

## Choose integration and validation shape

Classify the candidates before applying them:

| Relationship | Integration | Validation |
| --- | --- | --- |
| Independent, low overlap | Preserve separate logical changes in a chosen order | Share expensive final checks when behavior remains attributable |
| Ordered dependency | Apply in dependency order and retain useful boundaries | Validate independently landable intermediate states, then the combination |
| Inseparable intent | Combine only when separate landing or rollback is not reasonable | Validate the combined boundary |
| Conflict or high-risk interaction | Integrate incrementally and resolve explicitly | Validate in stages to isolate failures |

Do not create one change per remote ref mechanically. Split a candidate that
contains several independently landable intents; combine candidates only when
the repository's change-boundary test requires it.

One expensive build, test deployment, or activation may cover several
candidates only when:

- one final candidate tree contains every integrated change;
- no candidate requires observation of an intermediate runtime state;
- the final check reaches every affected consumer;
- candidate-specific behavior checks still identify what passed;
- failure can be isolated without deleting or hiding a candidate.

## Integrate into owned local changes

Preserve source refs and source objects while integrating. Prefer the
repository-native operation that copies or replays audited logical changes onto
the recorded local tip without modifying the source candidate. Record every new
logical ID and its parent.

Maintain a source-to-local coverage map. For every source logical change or
material diff section, record whether it was preserved, adapted, or intentionally
omitted, the destination local change, and the reason. Treat an unexplained
missing source section as an integration failure.

Adapt each local change to the consumer repository:

- resolve both textual and semantic conflicts;
- preserve one declaration owner for packages, services, and generated files;
- retain unaffected consumers of shared files;
- translate version-specific configuration without weakening behavior;
- keep credentials, state-version, lockfile, licensing, and host-scope policy;
- place compatibility repairs in the change whose behavior requires them.

After each mutation, inspect the exact diff, descendants, conflicts, workspaces,
and recovery log. Never drop a candidate silently because the combined result
fails.

## Validate with an evidence ledger

Run boundary-local formatting and cheap checks in the owning change. Then
validate the ordered final tree according to repository policy.

Track for every candidate:

- structural or static checks;
- required consumer evaluations;
- complete builds;
- task-specific behavior checks;
- interaction checks with other candidates;
- deployment or activation state;
- recovery evidence and remaining uncertainty.

If a shared final check fails, isolate whether the cause is one candidate, its
adaptation, or an interaction. Fix the owning boundary and rerun every check
whose input changed. Do not publish a partially evidenced stack.

## Publish, verify, then retire

Proceed only with explicit authority for the exact target and source refs.

1. Refresh the target and all live candidates; stop on concurrent movement.
2. Reconfirm the intended integration tip rather than assuming the current
   working tip is the publication target.
3. Inspect the entire exact outgoing ancestor range, including unrelated
   descendants, empty or undescribed changes, transient add/remove pairs,
   conflicts, and the final tree.
4. Move only the authorized integration target to the verified local tip.
5. Dry-run and push only that target with the version-control system's
   lease/concurrency protection.
6. Verify the server target equals the intended object.
7. Delete consumed source candidates one at a time, using exact names and a
   dry run when available.
8. Verify each source ref is absent before deleting the next.

Never force a target or bulk-delete refs unless the user explicitly authorized
that exact effect and repository policy permits it. Source-ref deletion never
authorizes discarding integrated local changes or recovery history.

## Report the integration

Return:

- source refs and recorded object IDs;
- resulting logical changes and order;
- adaptations made during consumption;
- per-candidate and combined validation evidence;
- deployment or activation result and recovery point;
- published target and verified server object;
- deleted and retained source refs;
- unresolved risks or intentionally skipped checks.
