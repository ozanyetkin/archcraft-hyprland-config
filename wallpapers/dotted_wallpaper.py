#!/usr/bin/env python3
"""
Dotted Wallpaper Generator for Hyprland

Creates a uniform grid of dots that align with Hyprland window gaps.
The dots are placed at regular intervals, ensuring they align with window
boundaries regardless of how windows are tiled.

Configuration:
- gaps_out: 12px (space from screen edges)
- gaps_in: 6px (space between windows, 12px total gap)
- Top bar: 32px safe space
"""

import argparse

from PIL import Image, ImageDraw


def create_dotted_wallpaper(
    width=3840,
    height=2160,
    dot_radius=2,
    dot_spacing=240,  # Spacing between dots (window tile size + gap)
    gaps_out=12,
    top_bar=32,
    dot_color=(80, 80, 80),
    bg_color=(0, 0, 0),
    output_file="dotted_wallpaper.png",
):
    """
    Create a dotted wallpaper with uniform grid spacing.

    The dots are placed at regular intervals starting from the screen edges,
    aligned with Hyprland's gap system. This ensures dots appear at window
    corners regardless of the tiling layout.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        dot_radius: Radius of each dot in pixels
        dot_spacing: Distance between dots in pixels (should match window tile size)
        gaps_out: Hyprland gaps_out value (space from screen edges)
        top_bar: Top bar height in pixels
        dot_color: RGB tuple for dot color
        bg_color: RGB tuple for background color
        output_file: Output filename
    """
    # Create black background
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Starting positions (accounting for gaps_out)
    start_x = gaps_out
    start_y = top_bar + gaps_out

    # Calculate number of dots that fit
    available_width = width - 2 * gaps_out
    available_height = height - top_bar - 2 * gaps_out

    # Number of dots in each direction
    dots_x = int(available_width / dot_spacing) + 1
    dots_y = int(available_height / dot_spacing) + 1

    dot_positions = []

    # Generate dot grid
    for row in range(dots_y + 1):
        y = start_y + row * dot_spacing
        if y > height - gaps_out:
            break

        for col in range(dots_x + 1):
            x = start_x + col * dot_spacing
            if x > width - gaps_out:
                break

            dot_positions.append((x, y))

    # Draw all dots
    for x, y in dot_positions:
        draw.ellipse(
            [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
            fill=dot_color,
            outline=dot_color,
        )

    # Save the image
    img.save(output_file, "PNG")
    print(f"✓ Wallpaper saved to: {output_file}")
    print(f"  Resolution: {width}x{height}")
    print(f"  Dot spacing: {dot_spacing}px")
    print(f"  Total dots: {len(dot_positions)}")
    print(f"  Grid: ~{dots_x}x{dots_y}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a dotted wallpaper aligned with Hyprland window gaps",
        epilog="Example: python3 dotted_wallpaper.py --preset 4k --spacing 240",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=3840,
        help="Width of the wallpaper in pixels (default: 3840)",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=2160,
        help="Height of the wallpaper in pixels (default: 2160)",
    )

    parser.add_argument(
        "--preset",
        choices=[
            "1920x1200",
            "1920x1080",
            "2560x1440",
            "3840x2160",
            "fhd",
            "qhd",
            "uhd",
            "4k",
        ],
        help="Use a preset resolution (overrides --width and --height)",
    )

    parser.add_argument(
        "--dot-radius",
        type=int,
        default=2,
        help="Radius of each dot in pixels (default: 2)",
    )

    parser.add_argument(
        "--spacing",
        type=int,
        default=240,
        help="Distance between dots in pixels (default: 240)",
    )

    parser.add_argument(
        "--gaps-out",
        type=int,
        default=12,
        help="Hyprland gaps_out value in pixels (default: 12)",
    )

    parser.add_argument(
        "--top-bar",
        type=int,
        default=32,
        help="Top bar height in pixels (default: 32)",
    )

    parser.add_argument(
        "--dot-color",
        type=str,
        default="80,80,80",
        help="Dot color as R,G,B (default: 80,80,80 for gray)",
    )

    parser.add_argument(
        "--bg-color",
        type=str,
        default="0,0,0",
        help="Background color as R,G,B (default: 0,0,0 for black)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="dotted_wallpaper.png",
        help="Output filename (default: dotted_wallpaper.png)",
    )

    args = parser.parse_args()

    # Handle preset resolutions
    width = args.width
    height = args.height

    if args.preset:
        presets = {
            "1920x1200": (1920, 1200),
            "1920x1080": (1920, 1080),
            "2560x1440": (2560, 1440),
            "3840x2160": (3840, 2160),
            "fhd": (1920, 1080),
            "qhd": (2560, 1440),
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
        dot_spacing=args.spacing,
        gaps_out=args.gaps_out,
        top_bar=args.top_bar,
        dot_color=dot_color,
        bg_color=bg_color,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
