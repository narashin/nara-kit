# Adopt Procedure — Token Replacement

## Step 1: Choose Template

Evaluate project design personality from existing artifacts:
- Color temperature (warm/cool/neutral)
- Surface mode (dark-first / light-first / dual)
- Spacing density (compact / comfortable / spacious)
- Shape language (sharp / rounded / mixed)
- Layout pattern (sidebar / single-column / grid)

Recommend 2-3 templates from [getdesign.md](https://getdesign.md/) matching these traits.

## Step 2: Install

```bash
npx getdesign@latest add <template-name>
```

## Step 3: Extract Project Tokens

Scan in parallel:

| Source | Extract |
|--------|---------|
| `tailwind.config.*` | Color palette, spacing, radius, shadows, font config |
| CSS/SCSS variables | Custom properties, overrides, global styles |
| Component library config | Base styles, theme overrides |
| `package.json` | UI framework, icon library, design system package |
| Key components (sample 5-8) | Button variants, card patterns, input styles, nav |
| Figma (if provided) | Visual theme, mood, distinctive characteristics |

## Step 4: Replace YAML Frontmatter

1. `colors:` → project actual colors. Map semantic roles (primary, surface, text, semantic)
2. `typography:` → project font hierarchy from design system preset
3. `rounded:` → project radius scale
4. `spacing:` → project spacing scale
5. `components:` → key component styles extracted from actual code

## Step 5: Rewrite Markdown Body

Replace all 9+ sections with project-specific content:
- **Overview**: project design personality + Key Characteristics
- **Colors**: actual colors + role descriptions
- **Typography**: actual fonts + hierarchy table + principles
- **Layout**: actual spacing/grid/container system
- **Elevation & Depth**: actual shadow/border depth strategy
- **Shapes**: actual radius scale + philosophy
- **Components**: actual component list + detailed styles
- **Do's and Don'ts**: project convention-based design guardrails
- **Responsive**: actual breakpoints + collapsing strategy
- **Iteration Guide**: AI agent rules for this project's stack

Preserve template's **writing style and structure** — replace values only.

## Step 6: Validate

- Check all `{colors.*}`, `{typography.*}`, `{rounded.*}`, `{spacing.*}` refs in body exist in frontmatter
- Output Completeness Score (see scoring.md)
- Save DESIGN.md to project root
