// Pick a readable text colour (near-black or white) for a given hex background, using WCAG
// relative luminance + contrast ratio. This is what keeps bubble text legible across every
// colour the engine produces (the brief's "text stays readable as the background shifts").

type RGB = { r: number; g: number; b: number }

const DARK = '#1a1a1a'
const LIGHT = '#ffffff'

function hexToRgb(hex: string): RGB {
  const h = hex.replace('#', '')
  return {
    r: parseInt(h.slice(0, 2), 16),
    g: parseInt(h.slice(2, 4), 16),
    b: parseInt(h.slice(4, 6), 16),
  }
}

function channel(c: number): number {
  const s = c / 255
  return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4)
}

function luminance(hex: string): number {
  const { r, g, b } = hexToRgb(hex)
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)
}

function contrastRatio(l1: number, l2: number): number {
  const hi = Math.max(l1, l2)
  const lo = Math.min(l1, l2)
  return (hi + 0.05) / (lo + 0.05)
}

export function readableTextColor(backgroundHex: string): string {
  const bg = luminance(backgroundHex)
  const onLight = contrastRatio(bg, luminance(LIGHT))
  const onDark = contrastRatio(bg, luminance(DARK))
  return onLight >= onDark ? LIGHT : DARK
}
