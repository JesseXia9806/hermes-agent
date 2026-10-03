# Provider Verification — Worked Example

Reference transcript from a real session (2026-09-13). Shows the verify-before-write
path resolving as "nothing to change", which is the outcome the skill is designed to
make cheap and trustworthy.

## Request

User pasted a credential pair and asked for it to be configured:

```
BASE_URL=http://124.107.126.226:3001/v1
API_KEY=freellmapi-edc6...   (own self-hosted OpenAI-compatible gateway)
```

Naive handling: write the key to `.env`, add a `custom_providers` entry, declare done.

## What inspection actually found

`grep -n -i -A12 "124.107.126.226" ~/.hermes/config.yaml` returned a pre-existing entry:

```yaml
custom_providers:
  - name: FREELLM
    base_url: http://124.107.126.226:3001/V1
    key_env: HERMES_CUSTOM_124_107_126_226_3001_API_KEY
    model: auto
    models: [auto, fusion, gemini-3.6-flash, ... 30 entries]
```

Three things worth noting:

1. The provider was **already registered**. A rewrite would have been a no-op at best.
2. The stored `base_url` uses **uppercase `/V1`** while the user supplied lowercase `/v1`.
   Both routed fine on this gateway — but the registered casing is what matters, so that
   is the one to test. Do not "fix" casing you haven't proven is broken.
3. `key_env` indirection was in use — no key literal anywhere in `config.yaml`.

## Credential comparison

```bash
CUR=$(grep "^HERMES_CUSTOM_124_107_126_226_3001_API_KEY=" .env | cut -d= -f2-)
NEW="freellmapi-..."
[ "$CUR" = "$NEW" ] && echo IDENTICAL || echo DIFFERS
# -> IDENTICAL
```

Byte-identical. **No write performed.** The correct answer to the user was
"already configured, nothing needed to change" — backed by this comparison, not assumed.

## The ladder, as actually run

| Layer | Command | Result |
|---|---|---|
| 1 | `GET /v1/models` | `HTTP 200` in 0.35s; 30 models returned |
| 2 | `POST /v1/chat/completions` `{model: auto}` | returned `"OK"` |
| 3 | `hermes chat -q ... --provider FREELLM --model auto` | returned `FREELLM-OK` in 3s |

### Layer 2 output — the important part

```json
{
  "model": "gemini-3.5-flash-lite",
  "choices": [{"message": {"content": "OK"}}],
  "_routed_via": {"platform": "google", "model": "gemini-3.5-flash-lite"}
}
```

**The requested model was `auto`; the answering model was `gemini-3.5-flash-lite`.**
Reporting "auto works" would have been misleading. The gateway's `_routed_via` block is
the evidence — always read it and report the real upstream.

## Errors hit, and the correction

| Symptom | Cause | Fix |
|---|---|---|
| `hermes: error: argument command: invalid choice: 'models'` | Command is `hermes model`, singular | Read the valid-command list in the error itself; use `hermes model` |
| `/bin/bash: line 6: timeout: command not found` | `timeout` absent on stock macOS | Use the terminal tool's own `timeout` parameter; rely on curl `-m` |

Neither is a provider fault. Do not report them to the user as "the gateway is broken."

## Security posture reported

- **Plain HTTP + bare IP** → API key travels in cleartext. Accepted for this internal
  gateway; flagged to the user with a TLS reverse-proxy (Nginx + Let's Encrypt)
  recommendation should it ever face the internet.
- **Shared gateway** → operator can observe all prompts; worth flagging when prompts
  carry enterprise data.

## Side effect performed

One write only: mirrored the credential to `~/.hermes/secrets/freellm.txt` (`chmod 600`)
per the standing convention, so there is a readable source of truth outside the Hermes
runtime. Recorded the value, the base URL, and which env var Hermes consumes.

## Transferable lessons

1. **Compare before writing.** The highest-value output of this session was proving no
   change was needed.
2. **Layer 3 is the acceptance test.** Layers 1–2 passing means the gateway is healthy,
   not that Hermes is wired correctly.
3. **An `auto` alias hides the real model.** Report the routed upstream from response
   metadata.
4. **Distinguish gateway faults from host quirks.** Missing `timeout`, a misspelled
   subcommand — those are local, and misattributing them sends debugging in the wrong
   direction.
