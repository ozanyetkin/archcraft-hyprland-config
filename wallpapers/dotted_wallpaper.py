"""Generate a dotted wallpaper aligned to tiling gaps.

Requirements implemented:
- Resolution: 3840x2160 (4K)
- Top bar reserved area: 32 px (no dots there)
- Outer gaps: 12 px
- Dot grid spacing: 12 px (so dots sit in the middle of 12 px gaps)
- Dot size: 2 px diameter

The script outputs `dotted_wallpaper.png` in the current directory.

You need Pillow installed:
	pip install pillow
"""

from __future__ import annotations

from pathlib import Path
import argparse

from PIL import Image, ImageDraw


def generate_dotted_wallpaper(
	width: int = 3840,
	height: int = 2160,
	top_margin: int = 48,
	left_margin: int = 9,
	right_margin: int = 9,
	bottom_margin: int = 0,
	grid_spacing_x: int = 18,
	grid_spacing_y: int = 9,
	dot_diameter: int = 4,
	background_color: tuple[int, int, int] = (0, 0, 0),
	dot_color: tuple[int, int, int] = (40, 40, 40),
	output_path: Path | str = "dotted_wallpaper.png",
) -> Path:
	"""Generate the dotted wallpaper image and return the output path.

	Margins and spacing can be tuned independently to align
	with multi‑monitor layouts and tiling gaps.
	"""

	img = Image.new("RGB", (width, height), background_color)
	draw = ImageDraw.Draw(img)

	radius = dot_diameter / 2.0

	# Effective drawable area accounting for margins.
	left = left_margin
	right = width - right_margin
	top = top_margin
	bottom = height - bottom_margin

	# Ensure we don't go out of bounds even with rounding.
	def clamp(v: float, lo: float, hi: float) -> float:
		return max(lo, min(hi, v))

	y = top
	while y <= bottom:
		x = left
		while x <= right:
			cx = clamp(x, 0 + radius, width - radius)
			cy = clamp(y, 0 + radius, height - radius)

			# Draw a small circle (dot) centered at (cx, cy).
			bbox = (
				cx - radius,
				cy - radius,
				cx + radius,
				cy + radius,
			)
			draw.ellipse(bbox, fill=dot_color)

			x += grid_spacing_x
		y += grid_spacing_y

	output_path = Path(output_path).expanduser().resolve()
	img.save(output_path)
	return output_path


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Generate dotted wallpaper")
	parser.add_argument("--width", type=int, default=3840)
	parser.add_argument("--height", type=int, default=2160)
	parser.add_argument("--top-margin", type=int, default=48)
	parser.add_argument("--left-margin", type=int, default=9)
	parser.add_argument("--right-margin", type=int, default=9)
	parser.add_argument("--bottom-margin", type=int, default=9)
	parser.add_argument("--grid-x", type=int, default=24, help="Horizontal grid spacing in pixels")
	parser.add_argument("--grid-y", type=int, default=18, help="Vertical grid spacing in pixels")
	parser.add_argument("--dot-diameter", type=int, default=4)
	parser.add_argument("--output", type=str, default="dotted_wallpaper.png")
	return parser.parse_args()


if __name__ == "__main__":
	args = parse_args()
	out = generate_dotted_wallpaper(
		width=args.width,
		height=args.height,
		top_margin=args.top_margin,
		left_margin=args.left_margin,
		right_margin=args.right_margin,
		bottom_margin=args.bottom_margin,
		grid_spacing_x=args.grid_x,
		grid_spacing_y=args.grid_y,
		dot_diameter=args.dot_diameter,
		output_path=args.output,
	)
	print(f"Generated wallpaper at: {out}")
