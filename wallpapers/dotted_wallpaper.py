#!/usr/bin/env python3
"""
Dotted Wallpaper Generator for Hyprland

Two modes:

1. uniform (default)
   - Simple regular grid of dots with fixed spacing.

2. irregular
   - Simulates up to N levels of binary splits (like a tiling WM),
     respecting gaps_out, gaps_in, and border_size.
   - Collects all vertical and horizontal split positions and places
     dots at their intersections, creating an irregular grid that
     matches many plausible Hyprland layouts.

This file is tailored to your Hyprland-like config:

    border_size = 4
    gaps_in     = 6   (so "full" gap between windows is 12px)
    gaps_out    = 12
    top_bar     = 32
"""

import argparse
from dataclasses import dataclass
from typing import List, Set, Tuple

from PIL import Image, ImageDraw


@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def x1(self) -> int:
        return self.x + self.w

    @property
    def y1(self) -> int:
        return self.y + self.h


def split_rect(
    rect: Rect,
    vertical: bool,
    ratio: float,
    gaps_in: int,
) -> Tuple[Rect, Rect]:
    """
    Split a rect into two child rects, inserting gaps_in between them.

    vertical = True  -> left/right split
    vertical = False -> top/bottom split
    ratio in (0,1)   -> approximate size fraction of the first rect
    """
    if vertical:
        total_w = rect.w
        gap = gaps_in
        # raw split point
        split_x = rect.x + int(total_w * ratio)
        # adjust with gap: left [x, split_x - gap//2), right [split_x + gap//2, x1)
        left_x0 = rect.x
        left_x1 = max(left_x0, split_x - gap // 2)
        right_x0 = min(split_x + gap // 2, rect.x1)
        right_x1 = rect.x1

        left = Rect(left_x0, rect.y, max(0, left_x1 - left_x0), rect.h)
        right = Rect(right_x0, rect.y, max(0, right_x1 - right_x0), rect.h)
        return left, right
    else:
        total_h = rect.h
        gap = gaps_in
        split_y = rect.y + int(total_h * ratio)

        top_y0 = rect.y
        top_y1 = max(top_y0, split_y - gap // 2)
        bot_y0 = min(split_y + gap // 2, rect.y1)
        bot_y1 = rect.y1

        top = Rect(rect.x, top_y0, rect.w, max(0, top_y1 - top_y0))
        bottom = Rect(rect.x, bot_y0, rect.w, max(0, bot_y1 - bot_y0))
        return top, bottom


def generate_irregular_grid(
    width: int,
    height: int,
    gaps_out: int,
    gaps_in: int,
    border_size: int,
    top_bar: int,
    max_depth: int = 8,
) -> Tuple[Set[int], Set[int]]:
    """
    Simulate binary splits up to `max_depth`, collect all vertical and
    horizontal edge positions where splits/gaps occur.

    The resulting set of lines is made symmetric with respect to the
    center of the *usable* area (after accounting for top_bar and
    gaps_out). This gives a visually centered, mirrored pattern.
    """
    # initial usable rect (where windows can live)
    usable = Rect(
        gaps_out,
        top_bar + gaps_out,
        width - 2 * gaps_out,
        height - top_bar - 2 * gaps_out,
    )

    rects: List[Rect] = [usable]

    # usable area's center (not the full screen's)
    cx = usable.x + usable.w // 2
    cy = usable.y + usable.h // 2

    xs: Set[int] = set()
    ys: Set[int] = set()

    def add_vertical_line(x: int) -> None:
        # clamp into usable region
        if x < usable.x or x > usable.x1:
            return
        xs.add(x)
        # mirror around center
        xm = 2 * cx - x
        if usable.x <= xm <= usable.x1:
            xs.add(xm)

    def add_horizontal_line(y: int) -> None:
        if y < usable.y or y > usable.y1:
            return
        ys.add(y)
        ym = 2 * cy - y
        if usable.y <= ym <= usable.y1:
            ys.add(ym)

    # include usable outer edges (and their mirrors, though they mirror to themselves)
    add_vertical_line(usable.x)
    add_vertical_line(usable.x1)
    add_horizontal_line(usable.y)
    add_horizontal_line(usable.y1)

    # deterministic pattern of splits
    # ratios alternate to create irregular but balanced layout
    ratios = [0.5, 0.5, 0.6, 0.4, 0.55, 0.45, 0.65, 0.35]

    for depth in range(max_depth):
        new_rects: List[Rect] = []
        vertical = depth % 2 == 0  # even: vertical, odd: horizontal
        ratio = ratios[depth % len(ratios)]

        for r in rects:
            if r.w <= 2 * border_size + gaps_in or r.h <= 2 * border_size + gaps_in:
                # too small to split meaningfully
                new_rects.append(r)
                continue

            a, b = split_rect(r, vertical, ratio, gaps_in)

            if a.w > 0 and a.h > 0:
                new_rects.append(a)
                # add edges for symmetry
                add_vertical_line(a.x)
                add_vertical_line(a.x1)
                add_horizontal_line(a.y)
                add_horizontal_line(a.y1)

            if b.w > 0 and b.h > 0:
                new_rects.append(b)
                add_vertical_line(b.x)
                add_vertical_line(b.x1)
                add_horizontal_line(b.y)
                add_horizontal_line(b.y1)

        rects = new_rects

    return xs, ys


def create_dotted_wallpaper_uniform(
    width=3840,
    height=2160,
    dot_radius=2,
    dot_spacing=240,
    gaps_out=12,
    top_bar=32,
    dot_color=(80, 80, 80),
    bg_color=(0, 0, 0),
    output_file="dotted_wallpaper.png",
):
    """
    Original uniform grid mode: dots spaced regularly.
    """
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    start_x = gaps_out
    start_y = top_bar + gaps_out

    available_width = width - 2 * gaps_out
    available_height = height - top_bar - 2 * gaps_out

    dots_x = int(available_width / dot_spacing) + 1
    dots_y = int(available_height / dot_spacing) + 1

    dot_positions = []

    for row in range(dots_y + 1):
        y = start_y + row * dot_spacing
        if y > height - gaps_out:
            break
        for col in range(dots_x + 1):
            x = start_x + col * dot_spacing
            if x > width - gaps_out:
                break
            dot_positions.append((x, y))

    for x, y in dot_positions:
        draw.ellipse(
            [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
            fill=dot_color,
            outline=dot_color,
        )

    img.save(output_file, "PNG")
    print(f"✓ Wallpaper saved to: {output_file}")
    print(f"  Mode: uniform")
    print(f"  Resolution: {width}x{height}")
    print(f"  Dot spacing: {dot_spacing}px")
    print(f"  Total dots: {len(dot_positions)}")


def create_dotted_wallpaper_irregular(
    width=3840,
    height=2160,
    dot_radius=2,
    gaps_out=12,
    gaps_in=6,
    border_size=4,
    top_bar=32,
    max_depth=8,
    dot_color=(80, 80, 80),
    bg_color=(0, 0, 0),
    output_file="dotted_wallpaper.png",
):
    """
    Irregular grid mode: simulate binary splits and place dots at
    intersections of split lines.
    """
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    xs, ys = generate_irregular_grid(
        width=width,
        height=height,
        gaps_out=gaps_out,
        gaps_in=gaps_in,
        border_size=border_size,
        top_bar=top_bar,
        max_depth=max_depth,
    )

    xs_sorted = sorted(xs)
    ys_sorted = sorted(ys)

    dot_positions = []

    # Optionally thin out very dense intersections by enforcing a minimum spacing
    min_sep = 8  # pixels
    filtered_xs = []
    last = None
    for x in xs_sorted:
        if last is None or abs(x - last) >= min_sep:
            filtered_xs.append(x)
            last = x

    filtered_ys = []
    last = None
    for y in ys_sorted:
        if last is None or abs(y - last) >= min_sep:
            filtered_ys.append(y)
            last = y

    for x in filtered_xs:
        for y in filtered_ys:
            # stay within usable area (just in case)
            if x < gaps_out or x > width - gaps_out:
                continue
            if y < top_bar + gaps_out or y > height - gaps_out:
                continue

            dot_positions.append((x, y))
            draw.ellipse(
                [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                fill=dot_color,
                outline=dot_color,
            )

    img.save(output_file, "PNG")
    print(f"✓ Wallpaper saved to: {output_file}")
    print(f"  Mode: irregular")
    print(f"  Resolution: {width}x{height}")
    print(f"  Max depth: {max_depth}")
    print(f"  Unique X lines: {len(filtered_xs)}")
    print(f"  Unique Y lines: {len(filtered_ys)}")
    print(f"  Total dots: {len(dot_positions)}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a dotted wallpaper aligned with Hyprland-like tiling",
        epilog=(
            "Examples:\n"
            "  python3 dotted_wallpaper.py --preset 4k --mode uniform\n"
            "  python3 dotted_wallpaper.py --preset 4k --mode irregular --max-depth 8"
        ),
    )

    parser.add_argument(
        "--mode",
        choices=["uniform", "irregular"],
        default="uniform",
        help="Grid mode: 'uniform' (regular spacing) or 'irregular' (binary splits).",
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
        help="(uniform mode only) Distance between dots in pixels (default: 240)",
    )

    parser.add_argument(
        "--gaps-out",
        type=int,
        default=12,
        help="Hyprland gaps_out value in pixels (default: 12)",
    )

    parser.add_argument(
        "--gaps-in",
        type=int,
        default=6,
        help="Hyprland gaps_in value in pixels (default: 6)",
    )

    parser.add_argument(
        "--border-size",
        type=int,
        default=4,
        help="Border size used for tiling simulation (default: 4)",
    )

    parser.add_argument(
        "--top-bar",
        type=int,
        default=32,
        help="Top bar height in pixels (default: 32)",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=8,
        help="(irregular mode only) Maximum binary split depth (default: 8)",
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

    if args.mode == "uniform":
        create_dotted_wallpaper_uniform(
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
    else:
        create_dotted_wallpaper_irregular(
            width=width,
            height=height,
            dot_radius=args.dot_radius,
            gaps_out=args.gaps_out,
            gaps_in=args.gaps_in,
            border_size=args.border_size,
            top_bar=args.top_bar,
            max_depth=args.max_depth,
            dot_color=dot_color,
            bg_color=bg_color,
            output_file=args.output,
        )


if __name__ == "__main__":
    main()
