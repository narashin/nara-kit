# DESIGN.md Template (Stitch Format)

This template shows the structure of a DESIGN.md file. When adopting, pick a brand template
from getdesign.md and replace tokens — do not fill this template from scratch.

## YAML Frontmatter — Token Definitions

```yaml
---
version: alpha
name: {Project Name}
description: {1-2 sentence design personality}

colors:
  primary: "#hex"          # Primary brand / CTA color
  ink: "#hex"              # Primary text color
  body: "#hex"             # Default body text
  body-strong: "#hex"      # Emphasized body text
  muted: "#hex"            # De-emphasized text (captions, footnotes)
  hairline: "#hex"         # Standard border/divider
  hairline-strong: "#hex"  # Emphasized border
  canvas: "#hex"           # Page background
  surface-card: "#hex"     # Card/container background
  surface-elevated: "#hex" # Elevated surface (nested cards, dropdowns)
  surface-soft: "#hex"     # Subtle surface variation
  on-primary: "#hex"       # Text on primary-colored surfaces
  on-dark: "#hex"          # Text on dark surfaces
  # Semantic
  positive: "#hex"         # Success states
  negative: "#hex"         # Error states
  warning: "#hex"          # Warning states
  info: "#hex"             # Informational states
  # Brand-specific accent colors
  accent-1: "#hex"
  accent-2: "#hex"

typography:
  display-xl:
    fontFamily: "{Font}, sans-serif"
    fontSize: 80px
    fontWeight: 700
    lineHeight: 1
    letterSpacing: 0
  display-lg:
    fontFamily: "{Font}, sans-serif"
    fontSize: 56px
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: 0
  display-md:
    fontFamily: "{Font}, sans-serif"
    fontSize: 40px
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: 0
  title-lg:
    fontFamily: "{Font}, sans-serif"
    fontSize: 24px
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: 0
  title-md:
    fontFamily: "{Font}, sans-serif"
    fontSize: 20px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0
  body-md:
    fontFamily: "{Font}, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
  body-sm:
    fontFamily: "{Font}, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
  caption:
    fontFamily: "{Font}, sans-serif"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0.5px
  button:
    fontFamily: "{Font}, sans-serif"
    fontSize: 14px
    fontWeight: 700
    lineHeight: 1
    letterSpacing: 0
  nav-link:
    fontFamily: "{Font}, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0

rounded:
  none: 0px
  xs: 2px
  sm: 4px
  md: 8px
  lg: 12px
  xl: 16px
  full: 9999px

spacing:
  xxs: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 40px
  xxl: 64px
  section: 96px

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: 12px 24px
    height: 40px
  button-secondary:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: 12px 24px
    height: 40px
  button-ghost:
    backgroundColor: transparent
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: 12px 24px
    height: 40px
  card:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: 24px
  text-input:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: 12px 16px
    height: 40px
  top-nav:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.nav-link}"
    height: 64px
---
```

## Markdown Body — Sections

After the YAML frontmatter `---`, write sections in this order:

### 1. Overview
- 2-3 paragraphs: design personality, mood, philosophy
- **Key Characteristics**: 5-7 bullet points with token references

### 2. Colors
- Group by role: Brand & Accent, Surface, Hairlines & Borders, Text, Semantic
- Each color: name, token ref, hex, usage description

### 3. Typography
- Font family rationale
- Hierarchy table (token, size, weight, line-height, letter-spacing, usage)
- Principles (weight contrast, spacing rules)

### 4. Layout
- Spacing system with base unit and scale
- Grid & container widths
- Whitespace philosophy

### 5. Elevation & Depth
- Shadow/surface level table
- Decorative depth elements

### 6. Shapes
- Border radius scale table with usage
- Shape language philosophy

### 7. Components
- Each component: token reference, full style spec, usage context
- Group: Navigation, Buttons, Cards, Inputs, Signature Components, Footer

### 8. Do's and Don'ts
- Do: 5-7 positive design rules
- Don't: 5-7 anti-patterns to avoid

### 9. Responsive Behavior
- Breakpoint table (name, width, key changes)
- Touch targets
- Collapsing strategy
- Image behavior

### 10. Iteration Guide
- AI agent rules for working with this design system
- Token reference conventions
- Component creation defaults

### 11. Known Gaps (optional)
- Limitations, unverified values, missing documentation
