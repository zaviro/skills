# Plugin Model Update Checklist

## 1. Baseline

- Identify the active tool: OpenCode, OpenClaw, or another plugin-based host
- Locate the active config file
- Locate the active plugin or adapter package if one exists
- Confirm whether multiple cache copies or hard-linked installs exist

## 2. Layer Map

Check these layers in order:

- `config`
- `plugin`
- `runtime`
- `exposure`

Do not patch an upper layer until the lower layer is understood.

## 3. Search-First Verification

- Check upstream releases
- Check relevant PRs and issues
- Check official docs for the provider model ID
- Treat naming conventions as hints only

## 4. Name Resolution

Record:

- `requested_name`
- `tool_model_id`
- `provider_api_id`
- `alias_needed`

## 5. Edit Scope

Prefer the smallest sufficient change:

- config only
- config + exposure
- config + plugin mapping
- config + plugin mapping + prompt/reasoning logic

## 6. OpenCode Checks

- Validate `~/.config/opencode/opencode.json`
- Check plugin version and local dist files
- Use:
  - `opencode providers list`
  - `opencode models`
  - `opencode run "healthcheck" -m <provider>/<model>`

## 7. OpenClaw Checks

- Validate `~/.openclaw/openclaw.json`
- Check configured/default/fallback models separately
- Use:
  - `openclaw status`
  - `openclaw models status --status-plain`
  - `openclaw models list`
- If needed, verify the lower OpenCode/provider path first

## 8. Verification Matrix

For each target model, record:

- `configured_id`
- `provider_api_id`
- `layers_changed`
- `runtime_status` (`success` | `provider_denied` | `network_tls_error` | `config_gap` | `unknown`)
- `notes`

## 9. Final Report Template

- Working now:
  - model A
- Pending external enablement:
  - model B
- Environment blockers:
  - model C
- Next trigger to revisit:
  - upstream release merged
  - provider rollout completed
