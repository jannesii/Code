#!/usr/bin/env python3
"""
Generate favicon assets from a source PNG/SVG using Pillow.

Outputs into server/app/static/ by default:
  - favicon.ico (16,32,48,64,128,256)
  - favicon-16x16.png
  - favicon-32x32.png
  - apple-touch-icon.png (180x180)

Usage:
  python tools/make_favicon.py path/to/source.png

If no path is given, looks for server/app/static/icon-source.png

Requires: Pillow (pip install pillow)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

try:
    from PIL import Image
except Exception as e:
    print("ERROR: Pillow not installed. Install with: pip install pillow", file=sys.stderr)
    raise


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / 'server' / 'app' / 'static'


def load_image(src_path: Path) -> Image.Image:
    img = Image.open(src_path).convert('RGBA')
    return img


def ensure_square(img: Image.Image, bg: Tuple[int, int, int, int] = (0, 0, 0, 0)) -> Image.Image:
    """Pad to a square canvas preserving transparency."""
    w, h = img.size
    if w == h:
        return img
    side = max(w, h)
    canvas = Image.new('RGBA', (side, side), bg)
    off = ((side - w) // 2, (side - h) // 2)
    canvas.paste(img, off, mask=img if img.mode == 'RGBA' else None)
    return canvas


def save_ico(img: Image.Image, out_path: Path, sizes: List[int]) -> None:
    variants = []
    for s in sizes:
        variants.append(img.resize((s, s), Image.LANCZOS))
    # Use the largest image as the base; Pillow will embed all sizes
    base = variants[-1]
    base.save(out_path, format='ICO', sizes=[(s, s) for s in sizes])


def main() -> None:
    if len(sys.argv) > 1:
        src = Path(sys.argv[1]).expanduser().resolve()
    else:
        src = STATIC_DIR / 'icon-source.png'

    if not src.exists():
        print(f"ERROR: Source image not found: {src}", file=sys.stderr)
        print("Place your PNG at that path or pass a path explicitly.", file=sys.stderr)
        sys.exit(1)

    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    img = load_image(src)
    img = ensure_square(img)

    # Export multi-size ICO
    ico_path = STATIC_DIR / 'favicon.ico'
    save_ico(img, ico_path, [16, 32, 48, 64, 128, 256])
    print(f"Wrote {ico_path}")

    # Export PNGs
    for s in (16, 32):
        out = STATIC_DIR / f'favicon-{s}x{s}.png'
        img.resize((s, s), Image.LANCZOS).save(out, format='PNG')
        print(f"Wrote {out}")

    # Apple touch icon (180x180); keep transparency.
    apple = STATIC_DIR / 'apple-touch-icon.png'
    img.resize((180, 180), Image.LANCZOS).save(apple, format='PNG')
    print(f"Wrote {apple}")


if __name__ == '__main__':
    main()

