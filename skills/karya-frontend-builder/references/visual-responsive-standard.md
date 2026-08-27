# Visual and Responsive Standard

## Visual Foundation

Define the visual system before implementing many screens:

- semantic colors and surface hierarchy
- typography scale and weights
- spacing rhythm
- radius and elevation
- borders and focus rings
- motion duration and easing
- content width and breakpoints

Represent stable decisions as CSS custom properties. Keep product identity out of arbitrary one-off values scattered across components.

## PrimeReact

Choose one PrimeReact theme as the base, then apply product tokens and scoped overrides. Avoid global selectors tied to fragile internal markup unless no supported theming or pass-through API exists.

Use PrimeReact for complex interaction primitives such as DataTable, Dialog, Drawer/Sidebar, Menu, Toast, Calendar, Dropdown, MultiSelect, FileUpload, Tabs, and pagination. Use semantic HTML and lightweight custom components when a library primitive adds no value.

## Product-Specific UI

Make the primary screen the strongest visual and interaction surface. Use realistic hierarchy, purposeful density, concrete copy, varied data, and a recognizable product identity.

Avoid:

- generic hero copy unrelated to the product
- repeated equal-weight cards
- arbitrary gradients everywhere
- excessive glass effects
- empty dashboards filled only to occupy space
- desktop-only tables with no small-screen strategy

## Mobile First

Start at 360px and enhance progressively. Validate at least:

- 360 x 740
- 390 x 844
- 768 x 1024
- 1280 x 800
- 1440 x 900

Require:

- no accidental page-level horizontal scroll
- touch targets around 44px where practical
- usable forms and dialogs at mobile height
- safe-area padding for fixed mobile navigation
- tables using cards, column priorities, or explicit overflow
- charts with readable labels and sensible reduced detail
- wrapped long labels and resilient user content
- visible focus states and keyboard navigation

## States

Design loading, skeleton, empty, error, success, disabled, offline/mock, and permission-denied states as first-class UI. Do not leave these as generic text after the main screen is polished.

## Accessibility

Provide semantic landmarks, associated form labels, accessible names for icon buttons, logical heading order, sufficient contrast, keyboard-operable dialogs and menus, and `prefers-reduced-motion` handling.

Use color plus text/icon/shape to communicate status. Do not rely only on color.
