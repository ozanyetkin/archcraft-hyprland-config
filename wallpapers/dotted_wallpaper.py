#!/usr/bin/env python3
"""
Dotted Wallpaper Generator

Creates a simple rectangular grid of filled circles (dots) on a black background.
Designed for tiling window managers with proper spacing considerations.

Features:
- Supports multiple resolutions (1920x1200, 3840x2160, or custom)
- 32px safe space at top for status bar
- 12px spacing between dots (matching window gaps)
- Gray dots on black background
"""

import argparse

from PIL import Image, ImageDraw


def create_dotted_wallpaper(
    width=1920,
    height=1200,
    dot_radius=1,
    dot_spacing=48,
    top_margin=32,
    dot_color=(80, 80, 80),
    bg_color=(0, 0, 0),
    output_file="dotted_wallpaper.png",
):
    """
    Create a dotted wallpaper with a rectangular grid of filled circles.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        dot_radius: Radius of each dot in pixels
        dot_spacing: Spacing between dot centers in pixels
        top_margin: Safe space at top for status bar in pixels
        dot_color: RGB tuple for dot color
        bg_color: RGB tuple for background color
        output_file: Output filename
    """
    # Create black background
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Calculate grid starting position (center the grid)
    # Account for top margin in vertical centering
    effective_height = height - top_margin

    # Calculate how many dots fit horizontally and vertically
    dots_h = (width - 2 * dot_radius) // dot_spacing
    dots_v = (effective_height - 2 * dot_radius) // dot_spacing

    # Calculate actual grid dimensions
    grid_width = dots_h * dot_spacing
    grid_height = dots_v * dot_spacing

    # Center the grid horizontally, and vertically in the effective area
    start_x = (width - grid_width) // 2
    start_y = top_margin + (effective_height - grid_height) // 2

    # Draw dots in a rectangular grid
    for row in range(dots_v + 1):
        for col in range(dots_h + 1):
            x = start_x + col * dot_spacing
            y = start_y + row * dot_spacing

            # Draw filled circle
            draw.ellipse(
                [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                fill=dot_color,
                outline=dot_color,
            )

    # Save the image
    img.save(output_file, "PNG")
    print(f"Wallpaper saved to: {output_file}")
    print(f"Resolution: {width}x{height}")
    print(f"Dots: {(dots_h + 1) * (dots_v + 1)} ({dots_h + 1}x{dots_v + 1} grid)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a dotted wallpaper with customizable parameters"
    )

    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Width of the wallpaper in pixels (default: 1920)",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=1200,
        help="Height of the wallpaper in pixels (default: 1200)",
    )

    parser.add_argument(
        "--preset",
        choices=["1920x1200", "3840x2160", "fhd", "uhd", "4k"],
        help="Use a preset resolution (overrides --width and --height)",
    )

    parser.add_argument(
        "--dot-radius",
        type=int,
        default=3,
        help="Radius of each dot in pixels (default: 3)",
    )

    parser.add_argument(
        "--dot-spacing",
        type=int,
        default=12,
        help="Spacing between dot centers in pixels (default: 12)",
    )

    parser.add_argument(
        "--top-margin",
        type=int,
        default=32,
        help="Safe space at top for status bar in pixels (default: 32)",
    )

    parser.add_argument(
        "--dot-color",
        type=str,
        default="80,80,80",
        help="Dot color as R,G,B (default: 80,80,80)",
    )

    parser.add_argument(
        "--bg-color",
        type=str,
        default="0,0,0",
        help="Background color as R,G,B (default: 0,0,0)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="dotted-wallpaper.png",
        help="Output filename (default: dotted-wallpaper.png)",
    )

    args = parser.parse_args()

    # Handle preset resolutions
    width = args.width
    height = args.height

    if args.preset:
        presets = {
            "1920x1200": (1920, 1200),
            "3840x2160": (3840, 2160),
            "fhd": (1920, 1080),
            "uhd": (3840, 2160),
            "4k": (3840, 2160),
        }
        width, height = presets[args.preset]

    # Parse colors
    dot_color = tuple(map(int, args.dot_color.split(",")))
    bg_color = tuple(map(int, args.bg_color.split(",")))

    # Create wallpaper
    create_dotted_wallpaper(
        width=width,
        height=height,
        dot_radius=args.dot_radius,
        dot_spacing=args.dot_spacing,
        top_margin=args.top_margin,
        dot_color=dot_color,
        bg_color=bg_color,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
