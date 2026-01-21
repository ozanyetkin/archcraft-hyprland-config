from PIL import Image, ImageDraw
import os

# ================= CONFIGURATION =================
# We define each monitor's specs explicitly based on your output
MONITORS = [
    {
        "name": "DP-1",
        "width": 3840,
        "height": 2160,
        "scale": 1.5,
        "bar_logical_height": 38,
        "gap_logical": 12,
        "line_width_base": 2,
    },
    {
        "name": "eDP-1",
        "width": 1920,
        "height": 1200,
        "scale": 1.0,
        "bar_logical_height": 38,
        "gap_logical": 12,
        "line_width_base": 2,
    },
]

# Shared Aesthetics
DEPTH = 6  # Recursion depth
COLOR_LINE = (53, 53, 53)  # #353535
COLOR_BG = (0, 0, 0)  # Pure Black Background


# ================= RECURSIVE DRAWING FUNCTION =================
def draw_recursive(draw, x, y, w, h, level, line_width, color):
    if level == 0:
        return

    mid_x = x + (w / 2)
    mid_y = y + (h / 2)

    # Vertical Split Line
    draw.line([(mid_x, y), (mid_x, y + h)], fill=color, width=line_width)

    # Horizontal Split Line
    draw.line([(x, mid_y), (x + w, mid_y)], fill=color, width=line_width)

    # Recurse
    new_w = w / 2
    new_h = h / 2

    draw_recursive(draw, x, y, new_w, new_h, level - 1, line_width, color)
    draw_recursive(draw, x + new_w, y, new_w, new_h, level - 1, line_width, color)
    draw_recursive(draw, x, y + new_h, new_w, new_h, level - 1, line_width, color)
    draw_recursive(
        draw, x + new_w, y + new_h, new_w, new_h, level - 1, line_width, color
    )


# ================= MAIN LOOP =================
for m in MONITORS:
    print(f"Processing {m['name']}...")

    # 1. Calculate Physical Dimensions
    # We round to ensure pixel-perfect integer coordinates
    scale = m["scale"]
    bar_px = int(m["bar_logical_height"] * scale)
    gap_px = int(m["gap_logical"] * scale)

    # Calculate Line Thickness
    # We scale the line thickness too so it looks visually similar on both screens
    line_width = int(m["line_width_base"] * scale)
    if line_width < 1:
        line_width = 1

    # 2. Define the "Tiling Container" area
    # This is the area where windows actually live
    container_x = gap_px
    container_y = bar_px + gap_px
    container_w = m["width"] - (gap_px * 2)
    container_h = m["height"] - (bar_px + (gap_px * 2))

    # 3. Create Image
    img = Image.new("RGB", (m["width"], m["height"]), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # 4. Draw
    print(
        f"  - Container Area: {container_w}x{container_h} (Offset: {container_x}, {container_y})"
    )
    draw_recursive(
        draw,
        container_x,
        container_y,
        container_w,
        container_h,
        DEPTH,
        line_width,
        COLOR_LINE,
    )

    # 5. Save
    filename = f"wallpaper_{m['name']}.png"
    img.save(filename)
    print(f"  - Saved to {filename}")

print("\nAll Done! Move these files to your wallpaper folder.")
