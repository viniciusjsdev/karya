---
name: commercial-launch-architect
description: Turn an existing app, platform, service, product brief, or validated idea into an executable commercial launch contract. Use to define audience, positioning, offer, channels, account-setup information, campaign phases, KPIs, experiments, constraints, and handoffs. This skill plans only; it does not create accounts, publish, contact users, or require the MVP or Research factories.
---

# Commercial Launch Architect

## Purpose

Create the commercial source of truth for launching or testing a product with real users. The input may come from Karya, another development stack, an existing business, or a standalone concept.

## Invocation Boundary

- Run only when the user explicitly asks for launch, positioning, go-to-market, acquisition, social-account preparation, or a commercial plan.
- Do not require a market-research artifact. If one exists, consume it; if not, mark commercial assumptions and proceed at the requested confidence.
- Do not modify product scope or block MVP construction.
- Do not create accounts, publish content, contact people, authorize spending, or operate external platforms.

## Workflow

### 1. Establish launch context

Capture product state, available proof, launch geography/language, budget, timeline, team capacity, compliance/brand constraints, and the commercial decision to support.

### 2. Define audience and positioning

Identify user, buyer, trigger, desired outcome, current alternative, objections, and proof. Write one primary positioning statement and separate claims that are proven from claims that remain hypotheses.

### 3. Define the offer and conversion path

Specify offer, price or test condition, promise, risk reversal where valid, primary call to action, landing/store destination, onboarding step, and conversion event. Do not invent discounts, guarantees, testimonials, or performance claims.

### 4. Select channels

Choose channels based on audience access, content fit, feedback speed, operational capacity, and measurement. Avoid opening every social channel by default. Platform-native audience research can be requested through the Research Factory but is not automatically invoked.

### 5. Prepare account setup kits

For each approved channel, use `references/account-setup-kit.md` to produce:

- handle options and naming checks to perform;
- display name, category, bio, contact fields, and link with UTM plan;
- profile-image and cover brief;
- professional/business account configuration checklist;
- Meta/business-manager connection when relevant;
- security checklist including owner, recovery, and 2FA;
- first content set and pinned/highlight structure;
- steps the human owner must perform.

Account creation, username availability, password, email/SMS verification, CAPTCHA, identity verification, and 2FA remain human-controlled. Never place secrets in the contract.

### 6. Design launch phases

Use pre-launch, launch, and learning/iteration phases only when useful. Define deliverables, owner, dependency, approval, start/stop condition, and success metric for every phase.

### 7. Define measurement

Choose one primary commercial outcome, leading indicators, funnel steps, guardrails, attribution/UTM rules, reporting cadence, and precommitted experiment thresholds. Distinguish vanity metrics from decision metrics.

### 8. Produce the contract

Use `assets/commercial-launch-contract.template.md` and `references/launch-planning.md`. Make downstream handoffs explicit but inactive.

## Required Output

- launch objective and constraints;
- audience, positioning, objections, and proof register;
- offer and conversion journey;
- channel rationale and exclusions;
- account setup kit for each approved platform;
- campaign phases and content requirements;
- KPI/funnel/attribution plan;
- experiment backlog with thresholds;
- risk, approvals, and human-action register;
- optional handoffs to `$marketing-creative-builder`, `$karya-commercial-router`, or `$commercial-validation-analyst`.

## Quality Gate

The contract is not ready if it contains unsupported claims, unclear account ownership, missing CTA/conversion event, unapproved spend, hidden platform actions, secrets, or success criteria that cannot change a decision.
