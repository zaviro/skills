---
name: updating-plugin-model
description: Use when updating model lists, aliases, or runtime mappings in plugin-based AI tools such as OpenCode and OpenClaw, especially when provider model names changed, local config and runtime disagree, plugin releases lag behind provider support, or real runtime verification is needed.
---

# Updating Plugin Model

## Overview

Update model integration by checking four layers in order: config, plugin, runtime, and exposure. Prioritize OpenCode and OpenClaw workflows first, then reuse the same method for similar tools.

## Workflow

1) Identify the active layers.
- Config layer: files such as `opencode.json` or `openclaw.json`
- Plugin layer: model maps, aliases, request normalization, reasoning rules, prompt family routing
- Runtime layer: provider actually recognizes and accepts the model
- Exposure layer: CLI, gateway, agent, or UI actually shows the model

2) Validate upstream before editing.
- Check releases, PRs, issues, or official docs first.
- Treat the user-provided model name as a candidate, not a fact.

3) Resolve three names.
- User-facing name
- Tool/config name
- Provider API name
- Add aliases only when the wrong name is common and worth preserving.

4) Edit the minimum necessary layer.
- If the provider path already supports the model, prefer config-only changes.
- Patch plugin internals only when config-only changes cannot surface the model.
- For agent/gateway tools such as OpenClaw, expose the model only after the lower provider path is confirmed.

5) Verify end to end.
- Validate file syntax.
- Verify the host tool now lists the model.
- Run a real model call.
- Classify the result as `success`, `provider_denied`, `network_tls_error`, or `config_gap`.

## Preferred Paths

### OpenCode

- Check `~/.config/opencode/opencode.json`
- Check installed plugin version and local plugin dist files when model mapping is suspect
- Use:
  - `opencode providers list`
  - `opencode models`
  - `opencode run "healthcheck" -m <provider>/<model>`

### OpenClaw

- Check `~/.openclaw/openclaw.json`
- Remember OpenClaw may only expose a model that is already valid in the underlying OpenCode/provider path
- Use:
  - `openclaw status`
  - `openclaw models status --status-plain`
  - `openclaw models list`
- If OpenClaw still hides the model, compare:
  - configured model allowlist
  - current default/fallback model set
  - underlying provider/runtime success in `opencode run`

### Similar Tools

Find the equivalents of:
- model config file
- plugin or adapter package
- provider credential source
- model list/status command
- real inference command

If the tool has both a lower model runtime and a higher agent/UI layer, verify the lower layer first.

## Decision Rules

- If upstream plugin already supports the requested model IDs, change only local config.
- If the host tool already knows the model but does not expose it, patch the exposure layer only.
- If runtime accepts the provider model but the tool rejects the local model name, fix naming or alias mapping.
- If runtime rejects the model with auth or enablement errors, keep the config future-ready and report the external blocker.
- If the failure is TLS, proxy, or certificate related, treat it as an environment issue instead of a model-map issue.

## Common Mistakes

- Updating display names without checking provider-true IDs
- Patching plugin code before proving config-only changes are insufficient
- Editing multiple cache copies and creating drift
- Assuming “listed in config” means “callable at runtime”
- Forgetting that OpenClaw exposure can lag behind OpenCode/provider support

## Reference

Use `references/plugin-model-update-checklist.md` for the compact checklist and verification matrix.
