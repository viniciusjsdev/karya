---
name: manus-platform-researcher
description: Execute a bounded, read-only research brief inside authenticated or platform-native environments such as Instagram, TikTok, LinkedIn, communities, directories, or creator marketplaces. Use when native search, live profiles, or signed-in context materially improves accuracy. Never contact users, publish, follow, like, create accounts, or change external state.
---

# Manus Platform Researcher

## Purpose

Give Manus a narrow, portable contract for research that benefits from its platform integrations and authenticated browsing. Return verifiable observations to Codex for synthesis and validation.

## Invocation Boundary

- Accept only an approved, read-only platform research brief.
- Use platform-native discovery for creators, communities, competitors, live profile signals, content patterns, and publicly visible engagement.
- Do not create accounts, solve verification challenges, store credentials, contact people, follow, like, comment, publish, schedule, purchase, or edit external records.
- Do not decide the strategy or rewrite the research objective.

Read `references/read-only-boundary.md` before interacting with a platform.

## Required Input

Require:

- task and decision identifier;
- target platform and authorized account/session;
- query, audience, geography, language, and time window;
- inclusion and exclusion criteria;
- required output fields and maximum result count;
- allowed public/profile data and prohibited sensitive data;
- evidence requirements and completion condition.

If authentication is missing, return `authentication_required`. Never request that credentials be pasted into a prompt, file, or result.

## Workflow

### 1. Confirm read-only scope

Reject ambiguous verbs such as "engage", "reach out", or "set up". Research may inspect and record; it may not mutate.

### 2. Search natively

Use the platform's search, filters, profiles, posts, public metrics, and connected directories. Stay within the requested scope and result cap. Respect access controls, terms, privacy, and robots restrictions.

### 3. Verify candidates

For each creator, community, or competitor, capture the stable handle/URL, why it matches, visible metrics with their observation time, geography/language when reasonably evidenced, recent relevant content, and red flags. Do not infer protected or private attributes.

### 4. Preserve evidence

Record the exact page/profile URL or platform identifier and the observation time. Screenshots may support volatile observations but do not replace structured fields or source links.

### 5. Return results

Follow `references/result-contract.md` and `assets/platform-research-result.schema.json`. Report inaccessible pages, query limitations, sampling bias, and search failures.

## Result Rules

- Separate platform-observed facts from inference.
- Avoid invented engagement quality, audience demographics, or price estimates.
- Do not rank solely by follower count; use the contract's relevance and quality criteria.
- Do not expose private messages, credentials, session data, or unnecessary personal data.
- Do not claim exhaustive coverage of a recommendation algorithm or platform search index.
- Return results to Codex; do not trigger `$manus-commercial-operator` automatically.

## Portable Handoff

This skill is intentionally self-contained so the same `SKILL.md`, references, and schema can be imported into a Manus workspace. Provider-specific connection mechanics stay outside Karya and outside generated product repositories.
