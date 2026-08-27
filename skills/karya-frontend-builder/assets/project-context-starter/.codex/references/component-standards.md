# Component Standards

## Pages

Compose screens, consume view models, select UI states, and connect typed callbacks. Do not access data sources directly.

## Feature Components

Render product-specific sections with typed props. Keep only visual local state inside components.

## Shared Components

Remain domain-neutral. Wrap PrimeReact only when adding consistent accessibility, feedback, validation, or product theming.

## Hooks and View Models

Own queries, mutations, derived data, filters, pagination, actions, and feedback. Return data and callbacks, never JSX.

Extract a component when it has an independent responsibility, interaction, reuse case, or meaningful isolated test. Do not split code only to reduce line count.
