# Conditional Agent: frontend-ux-a11y (ID prefix: FUX)

**Runs when** the change touches `*.tsx` / `*.jsx` / `*.css` / `*.scss`, `components/`,
`pages/`, or styles. Read-only — never edit code.

## Checks

**Component & render structure**
- Unnecessary JSX nesting: wrapper elements adding no layout value — check if inner
  component props already handle it.
- Component design inconsistency: new component deviating from existing structure/
  naming/prop conventions without justification.
- Controlled/uncontrolled mixing; key prop missing or index-based in reorderable
  lists.
- State that belongs in URL/form/context kept in ad-hoc local state (breaks refresh/
  back navigation expectations).

**UX behavior**
- Loading/empty/error states missing for async UI introduced in the diff.
- Optimistic updates without rollback on failure.
- Focus loss after dialog/modal open-close; scroll position jumps on rerender.
- Destructive actions without confirmation where sibling flows have one.

**Accessibility**
- Interactive elements that aren't focusable/keyboard-operable (div-with-onClick).
- Missing accessible names: icon-only buttons without aria-label, inputs without
  labels, images without alt.
- Color-only signaling (error/success conveyed by color alone).
- Obvious contrast violations introduced by the diff.

## Design consistency (only when DESIGN.md context is provided)

Skip this entire section if context-map found no DESIGN.md.

- Hardcoded hex values that should use color tokens defined in DESIGN.md.
- Border radius values deviating from the project's radius scale (e.g., `rounded-lg`
  when spec says `{rounded.200}`).
- Font weight usage violating the project's weight mapping (e.g., raw `font-bold`
  when LDS classes required).
- Color usage violating Do's/Don'ts (e.g., primary color as content-area background).
- Shadow usage where DESIGN.md specifies border-only depth.
- Components not using the project's design system library when one is available.
- Spacing values outside the defined scale.

## Not yours

Re-render performance → performance-resources. Client-side permission gating →
security-privacy.
