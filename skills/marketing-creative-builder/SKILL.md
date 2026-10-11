---
name: marketing-creative-builder
description: Build a channel-ready marketing creative pack from an approved launch contract, brand inputs, product evidence, and available screenshots or assets. Use for captions, carousels, short-video scripts, stories, ad variants, outreach drafts, landing copy, briefs, alt text, UTM metadata, and a production manifest. It creates artifacts but never publishes or contacts users.
---

# Marketing Creative Builder

## Purpose

Translate an approved commercial strategy into reusable, measurable creative assets without changing the strategy or making unsupported claims.

## Invocation Boundary

- Require a commercial launch contract or an equivalent approved brief containing audience, objective, channel, CTA, claims, and constraints.
- Do not choose a new market, audience, offer, price, or positioning silently.
- Do not publish, schedule, message, upload, buy media, or edit external accounts.
- Do not require that the product was built by the MVP Factory.

## Workflow

### 1. Verify inputs

Confirm channel, placement, campaign/experiment ID, audience, awareness stage, primary message, allowed proof, prohibited claims, CTA, destination, language, tone, visual assets, and approval owner. Return missing strategic decisions to `$commercial-launch-architect`.

Read the approved brief and search supporting product/brand materials for the intended claims. Expand each relevant passage to its qualifications and inspect table headers, units, periods, captions, and footnotes before using numbers or visuals. Use the available reading tools; note unreadable or unchecked proof instead of inferring it from a summary. Preserve source locations in the claim/proof register for the quality check.

### 2. Create a message system

Define the core promise, problem framing, proof, objection response, CTA, and 3-5 reusable message angles. Label unproven angles as hypotheses. Avoid fake urgency, fake scarcity, invented testimonials, and claims that exceed product evidence.

### 3. Build channel-specific artifacts

Follow `references/channel-specs.md`. Produce only requested formats, such as:

- Instagram/TikTok short-video hook, shot list, voiceover, on-screen text, caption, cover, and CTA;
- carousel slide copy, visual direction, caption, and alt text;
- stories with frame sequence and interaction prompt;
- static/post copy and visual brief;
- paid-ad variants only when paid media is explicitly in scope;
- creator outreach or customer-contact drafts, never sent automatically;
- landing/store-listing copy tied to the same message and conversion event.

When final bitmap generation is requested, invoke the available `imagegen` skill/tool for the image work. This skill remains responsible for the brief, claims, channel fit, variants, and QA.

### 4. Design real variants

Follow `references/experiment-variants.md`. Change one decision-driving dimension per experiment where possible: hook, proof, problem frame, format, or CTA. Do not label cosmetic differences as distinct hypotheses.

### 5. Add measurement metadata

Record campaign, creative, variant, channel, placement, CTA, destination, UTM values, hypothesis, primary metric, and pass/fail rule. Keep link metadata out of visible copy when the channel handles it separately.

### 6. QA and package

Use `references/creative-quality.md`. Produce the manifest defined in `assets/creative-pack-manifest.schema.json`, with source files, previews, dimensions/duration, copy, alt text, claims, approvals, and publication readiness.

## Required Output

- creative strategy summary tied to the launch contract;
- channel-ready copy and production instructions;
- visual/video briefs and generated assets when requested;
- genuine experiment variants;
- accessibility fields;
- UTM and measurement metadata;
- claim/proof register;
- manifest with status `draft`, `review_required`, or `approved_for_routing`.

## Hard Stops

Do not mark a pack ready when a claim lacks evidence, required brand/product assets are missing, a platform format is unknown, regulated wording lacks approval, or the CTA/destination is unresolved.
