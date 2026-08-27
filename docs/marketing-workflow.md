# Marketing Factory Workflow

## Goal

Prepare a product for commercial contact, create its campaign assets, execute only approved platform actions, and learn from real results. The product may have been built by any stack.

## Sequence

1. `commercial-launch-architect` creates positioning, offer, channel plan, account setup kits, campaign phases, KPIs, attribution, and experiments.
2. The human owner creates and secures required accounts using the kit.
3. `marketing-creative-builder` creates approved channel-ready copy, creative briefs/assets, variants, accessibility fields, and a manifest.
4. `karya-commercial-router` routes the next bounded operation:
   - Codex for strategy/artifacts;
   - human for account/security/confirmation/spend;
   - `manus-commercial-operator` for exact connected-platform execution.
5. Manus or the human returns an execution receipt; submission alone is not success.
6. `commercial-validation-analyst` reconciles plan, execution, metrics, cost, and feedback, then returns `scale`, `iterate`, `pivot`, `pause`, or `stop`.

## Creating an Instagram or other app account

Codex produces the complete setup package: handle options, display name, category, bio, link/UTM, profile visual brief, contact fields, professional settings, Meta connection checklist, security/recovery steps, and first content.

The human performs live account creation, accepts terms, confirms username availability, enters organization-owned contact details, completes CAPTCHA/email/SMS/identity verification, creates the password, enables 2FA, stores recovery codes, and authorizes connectors. Those steps are not delegated to Manus.

## Platform research versus action

Finding influencers, communities, competitors, and content patterns is a read-only Research Factory task for `manus-platform-researcher`. Publishing, scheduling, approved contact, metrics retrieval, and CRM mutation are Commercial Factory tasks for `manus-commercial-operator`. Keep discovery and action separate.

## Credit control

Codex prepares strategy and final artifacts. Manus receives only the exact target, final content, timing, limits, confirmation, and expected receipt fields. Broad research, rewriting, optimization, and recipient discovery do not run inside the paid execution task.

The API coupling, portable skill IDs, connectors, structured outputs, asynchronous lifecycle, and human confirmation path are specified in `codex-manus-integration.md`.
