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

from PIL import Image, ImageDraw


def generate_dotted_wallpaper(
	width: int = 3840,
	height: int = 2160,
	top_bar_height: int = 32,
	outer_gap: int = 12,
	grid_spacing: int = 12,
	dot_diameter: int = 2,
	background_color: tuple[int, int, int] = (0, 0, 0),
	dot_color: tuple[int, int, int] = (40, 40, 40),
	output_path: Path | str = "dotted_wallpaper.png",
) -> Path:
	"""Generate the dotted wallpaper image and return the output path."""

	img = Image.new("RGB", (width, height), background_color)
	draw = ImageDraw.Draw(img)

	radius = dot_diameter / 2.0

	# Effective drawable area accounting for top bar and outer gaps.
	left = outer_gap
	right = width - outer_gap
	top = top_bar_height + outer_gap
	bottom = height - outer_gap

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

			x += grid_spacing
		y += grid_spacing

	output_path = Path(output_path).expanduser().resolve()
	img.save(output_path)
	return output_path


if __name__ == "__main__":
	out = generate_dotted_wallpaper()
	print(f"Generated wallpaper at: {out}")
