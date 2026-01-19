import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw


def generate_isometric_dots(
	width: int = 3840,
	height: int = 2400,
	background_color: tuple[int, int, int] = (0, 0, 0),
	dot_color: tuple[int, int, int] = (255, 255, 255),
	dot_radius: int = 3,
	spacing: int = 40,
	margin: int = 80,
	output: Path | str = "dotted_wallpaper.png",
) -> Path:
	"""Generate an isometric grid of dots on a solid background.

	The grid is a hexagonal/triangular lattice: each row is offset by half the
	horizontal spacing, and vertical spacing is spacing * sin(60°).
	All numeric parameters are in pixels.
	"""

	img = Image.new("RGB", (width, height), background_color)
	draw = ImageDraw.Draw(img)

	h_spacing = float(spacing)
	v_spacing = spacing * math.sin(math.radians(60))  # ≈ 0.866 * spacing

	y = float(margin)
	row_index = 0

	while y <= height - margin:
		# Stagger every other row by half the horizontal spacing
		x = float(margin) + (h_spacing / 2.0 if row_index % 2 else 0.0)

		while x <= width - margin:
			left = x - dot_radius
			top = y - dot_radius
			right = x + dot_radius
			bottom = y + dot_radius
			draw.ellipse((left, top, right, bottom), fill=dot_color)
			x += h_spacing

		y += v_spacing
		row_index += 1

	output_path = Path(output).expanduser().resolve()
	output_path.parent.mkdir(parents=True, exist_ok=True)
	img.save(output_path, format="PNG")
	return output_path


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Generate a parametric isometric dotted wallpaper.",
	)

	parser.add_argument("--width", type=int, default=3840, help="Image width in pixels.")
	parser.add_argument("--height", type=int, default=2400, help="Image height in pixels.")
	parser.add_argument("--dot-radius", type=int, default=3, help="Dot radius in pixels.")
	parser.add_argument(
		"--spacing",
		type=int,
		default=40,
		help="Base spacing between dots (horizontal); vertical spacing is spacing * sin(60°).",
	)
	parser.add_argument("--margin", type=int, default=80, help="Margin around the grid in pixels.")
	parser.add_argument(
		"--background",
		type=str,
		default="0,0,0",
		help="Background RGB as 'R,G,B' (0-255). Default: 0,0,0 (black)",
	)
	parser.add_argument(
		"--dot-color",
		type=str,
		default="255,255,255",
		help="Dot RGB as 'R,G,B' (0-255). Default: 255,255,255 (white)",
	)
	parser.add_argument(
		"--output",
		type=str,
		default="dotted_wallpaper.png",
		help="Output PNG path.",
	)

	return parser.parse_args()


def parse_rgb(value: str) -> tuple[int, int, int]:
	parts = value.split(",")
	if len(parts) != 3:
		raise ValueError(f"Invalid RGB value '{value}', expected 'R,G,B'.")
	rgb = tuple(int(p) for p in parts)
	if any(c < 0 or c > 255 for c in rgb):
		raise ValueError(f"RGB components must be between 0 and 255: {rgb}")
	return rgb  # type: ignore[return-value]


def main() -> None:
	args = parse_args()

	background = parse_rgb(args.background)
	dot_color = parse_rgb(args.dot_color)

	generate_isometric_dots(
		width=args.width,
		height=args.height,
		background_color=background,
		dot_color=dot_color,
		dot_radius=args.dot_radius,
		spacing=args.spacing,
		margin=args.margin,
		output=args.output,
	)


if __name__ == "__main__":
	main()

