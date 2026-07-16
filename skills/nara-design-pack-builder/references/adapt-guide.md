# Adapting a framework component to standalone token JSX

This is the rulebook for `SKILL.md` Step 4 — turning one confirmed component from the source design system into
a **dependency-light, standalone** version that `nara-design-studio`'s runtime can mount directly (in-browser
Babel + CDN React, nothing else). Apply these rules to one component at a time; verify it mounts before moving
to the next (`SKILL.md` §5).

"Dependency-light" here means: no app store, no router, no context providers the pack doesn't itself supply, no
build-time CSS pipeline. It does **not** mean "no React" — React itself (via the CDN global) is the one runtime
dependency every pack component is allowed to assume.

---

## 1. Strip store/router/context imports

Anything that couples the component to the *host application* — rather than to the design system itself — has
to go, because the pack's only host is the studio's own page, not the source app.

| Coupling found in the source | Replace with |
|---|---|
| `connect()` / `useSelector` / `useDispatch` (Redux), `useStore` (Zustand/MobX) | Plain props. The value the store used to provide becomes a prop the caller passes in. |
| `<Link>` / `useNavigate()` / `useParams()` / `useLocation()` (react-router) | A plain `href` prop rendered as an `<a>`, or an `onNavigate`/`onClick` callback prop. Never import `react-router-dom` in an adapted component. |
| `useContext(AppThemeContext)` / any app-defined React Context | Either a prop with a sensible default, or — if the context genuinely belongs to the design system itself (e.g. a `ToastProvider`) — a *pack-local* context the bundle also defines and exposes, not the app's original one. |
| `useQuery` / `useSWR` / any data-fetching hook | Data becomes a prop. The adapted component renders what it's given; it does not fetch. |
| App-specific i18n hook (`useTranslation()`) | A `label`/`text` prop carrying the already-resolved string, or a plain default string literal. |

**Keep:** anything that is genuinely part of the *design system's own* API — a compound-component context used
only to pass state between a component's own subparts (e.g. a `<Tabs>`/`<Tabs.Panel>` pair), a hook the DS ships
for its own components (e.g. a focus-trap hook used only inside a `<Modal>`). The test is: "does this import
come from the app, or from the design system?" — only the former gets stripped.

## 2. Drive styling from tokens, not a build step

The studio's runtime has no bundler — no webpack, no Vite, no PostCSS, no CSS Modules loader, no
styled-components/emotion Babel plugin. Whatever styling mechanism the source component used, translate it
into one of these two forms:

- **Inline style object reading CSS custom properties**, e.g.:

  ```jsx
  const styles = {
    root: {
      background: 'var(--ds-surface)',
      borderRadius: 'var(--ds-radius-200)',
      color: 'var(--ds-ink)',
    },
  };
  ```

- **A scoped `<style>` block** (a plain string injected once, e.g. via a module-level `<style>` tag or a
  `useInsertionEffect`) for anything inline styles can't express cleanly — pseudo-classes (`:hover`, `:focus`),
  media queries, keyframe animations. The block's own rules still read tokens as `var(--ds-*)`; only the
  *mechanism* for hover/media is different from inline styles, not the token discipline.

**No build-time CSS-in-JS.** If the source component used `styled-components`/`emotion`'s `css` template
literal or `styled.div\`...\``, do not ship that dependency — it requires a build step (or a runtime library
load) the studio's page doesn't provide. Convert its rules into one of the two forms above. If a component's
CSS-in-JS usage is so dynamic (runtime theme functions computing values from arbitrary props, not just token
lookups) that a clean conversion isn't realistic this pass, that's exactly the case `SKILL.md` §11 (Honesty
note) means — flag it, don't force a broken conversion.

## 3. Expose on `window.<namespace>`

Every adapted component is a named property on the pack's namespace global, not a default export a bundler
would resolve for you:

```js
// inside _ds_bundle.js, after all component definitions
window.DS = window.DS || {};
window.DS.Button = Button;
window.DS.Table = Table;
```

Use the exact `namespace` string declared in `_ds_manifest.json` (see `manifest-schema.md`) — the studio's
template reads `window[manifest.namespace]`, so a mismatch here means every candidate that tries to mount the
pack's components silently gets `undefined`.

## 4. Keep prop names

Do not rename a component's public prop API during adaptation, even if a prop name looks awkward or you'd
choose differently. The pack's whole value is that the studio-rendered output *is* reference code an
implementer copies against the real component — a renamed prop breaks that the moment someone diffs the
adapted version against the source repo. If a prop genuinely can't be honored standalone (it depended on
something stripped in §1), keep the prop in the signature, document in the `.d.ts` and `.prompt.md` that it's
currently a no-op standalone, and say why — don't silently drop it from the type.

## 5. Companion files — one `.d.ts` + one `.prompt.md` per component

Every adapted component ships two companion files alongside its `.jsx`, named identically:

### `<Name>.d.ts` — typed props, no `any`

```ts
// Button.d.ts
export interface ButtonProps {
  /** Visual emphasis. Maps to the DS's own variant enum. */
  variant: 'primary' | 'secondary' | 'ghost';
  /** Disabled state; when true, onClick never fires. */
  disabled?: boolean;
  /** Click handler. Replaces the source app's router-aware onClick. */
  onClick?: (event: MouseEvent) => void;
  children: React.ReactNode;
}

export declare function Button(props: ButtonProps): JSX.Element;
```

Use a real union type, a documented interface, or a generic — never `any` as a stand-in for "I didn't figure out
the real type." If the source prop's real type is genuinely unknown (e.g. an opaque object passed through
untouched), narrow it as far as you honestly can (`Record<string, unknown>`, a documented `unknown` with a
comment) rather than reaching for `any`.

### `<Name>.prompt.md` — a short usage note

```md
# Button

Primary action trigger. Use `variant="primary"` for the single main action on a screen; `secondary`/`ghost`
for supporting actions. Standalone version drops the source app's router-aware navigation — pass a plain
`onClick` instead of relying on an internal `href`.

**Example:**
\`\`\`jsx
<DS.Button variant="primary" onClick={() => save()}>Save</DS.Button>
\`\`\`
```

Keep it to what a screen-designing agent actually needs: when to reach for the component, which props matter,
one runnable example. This is not component documentation for its own sake — it's the thing that lets
`nara-design-studio` (or a human) use the component correctly without re-reading its adapted source.

## 6. When a component can't adapt cleanly

Don't force it. If, after a genuine attempt, a component is still coupled to something in §1 that has no
reasonable prop-based substitute (e.g. it reads five different pieces of global app state and re-derives its
own layout from them), or its styling is runtime CSS-in-JS too dynamic for §2's two forms — stop adapting it,
and record it as `status: "flagged"` in the manifest's `components[]` entry (`manifest-schema.md`) with a
one-line reason. This keeps the pack honest about what it actually offers, per `SKILL.md` §11.
