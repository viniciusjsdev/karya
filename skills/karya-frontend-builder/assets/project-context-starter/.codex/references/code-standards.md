# Code Standards

- Use TypeScript strict mode and avoid unjustified `any`.
- Use explicit names such as `CaseListPage.tsx`, `useCaseListViewModel.ts`, and `case.service.ts`.
- Prefer one principal component or hook per file.
- Use the `@/` alias for source imports.
- Keep user-facing copy in the product language and code identifiers consistently in English.
- Keep functions focused and make data transformations testable outside JSX.
- Review files above roughly 250 lines or files mixing UI, data access, state, and business logic.
- Do not create wrappers, abstractions, or shared utilities without a concrete reuse or boundary benefit.
- Keep errors typed and normalize infrastructure failures before presenting UI feedback.
- Format with Prettier and require lint, typecheck, tests, and build before completion.
