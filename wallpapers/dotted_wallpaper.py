from PIL import Image, ImageDraw

# ================= CONFIGURATION =================
# 1. Screen Dimensions
SCREEN_W = 3840
SCREEN_H = 2400
SCALE = 1.5

# 2. Window Manager Settings (Use Logical values, script handles scaling)
BAR_HEIGHT = 48
GAP_OUTER = 18  # Space between screen edge and windows
GAP_INNER = 18  # Space between two windows (Visual size)
# Note: If your config says "gaps_in 6", the visual gap is often 6+6=12.
# We use 12 here to ensure the wallpaper gap matches the visual gap.

# 3. Visuals
RECURSION_DEPTH = 6  # How many times to split? (5 is usually enough for 4K)
DOT_SIZE = 2  # Radius (2 = 4px circle)
DOT_SPACING = 18  # How far apart dots are along the line
DOT_COLOR = (80, 80, 80)  # Light Grey
BG_COLOR = (10, 10, 10)  # Deep Dark Grey

# ================= SETUP =================
# Convert logical to physical pixels
bar_phys = int(BAR_HEIGHT * SCALE)
gap_out_phys = int(GAP_OUTER * SCALE)
gap_in_phys = int(GAP_INNER * SCALE)

image = Image.new("RGB", (SCREEN_W, SCREEN_H), BG_COLOR)
draw = ImageDraw.Draw(image)


# ================= RECURSIVE FUNCTION =================
def draw_splits(x, y, w, h, depth):
    if depth == 0:
        return

    # --- 1. Calculate Split Coordinates ---
    # The math: (Width - Gap) / 2

    # Vertical Split (splits width)
    child_w = (w - gap_in_phys) / 2
    split_x_center = x + child_w + (gap_in_phys / 2)

    # Horizontal Split (splits height)
    child_h = (h - gap_in_phys) / 2
    split_y_center = y + child_h + (gap_in_phys / 2)

    # --- 2. Draw Dots at these Split Lines ---

    # Draw Vertical Line (Line at X, spanning current height)
    # We iterate along the Y axis of the current block
    for dy in range(int(y), int(y + h), DOT_SPACING):
        # Draw dot centered at (split_x_center, dy)
        draw.ellipse(
            [
                split_x_center - DOT_SIZE,
                dy - DOT_SIZE,
                split_x_center + DOT_SIZE,
                dy + DOT_SIZE,
            ],
            fill=DOT_COLOR,
        )

    # Draw Horizontal Line (Line at Y, spanning current width)
    # We iterate along the X axis of the current block
    for dx in range(int(x), int(x + w), DOT_SPACING):
        # Draw dot centered at (dx, split_y_center)
        draw.ellipse(
            [
                dx - DOT_SIZE,
                split_y_center - DOT_SIZE,
                dx + DOT_SIZE,
                split_y_center + DOT_SIZE,
            ],
            fill=DOT_COLOR,
        )

    # --- 3. Recurse ---
    # We need to simulate splits in all 4 resulting quadrants
    # to catch every possible window configuration.

    # Top-Left Box
    draw_splits(x, y, child_w, child_h, depth - 1)

    # Top-Right Box
    draw_splits(split_x_center + (gap_in_phys / 2), y, child_w, child_h, depth - 1)

    # Bottom-Left Box
    draw_splits(x, split_y_center + (gap_in_phys / 2), child_w, child_h, depth - 1)

    # Bottom-Right Box
    draw_splits(
        split_x_center + (gap_in_phys / 2),
        split_y_center + (gap_in_phys / 2),
        child_w,
        child_h,
        depth - 1,
    )


# ================= EXECUTION =================

# Define the "Root" container (The area inside the outer gaps and bar)
root_x = gap_out_phys
root_y = bar_phys + gap_out_phys
root_w = SCREEN_W - (2 * gap_out_phys)
root_h = SCREEN_H - bar_phys - (2 * gap_out_phys)

print(f"Generating recursive grid for area: {int(root_w)}x{int(root_h)}")
print(f"Recursion Depth: {RECURSION_DEPTH}")

draw_splits(root_x, root_y, root_w, root_h, RECURSION_DEPTH)

# Optional: Draw the outer boundary (to see if it matches the outer gap)
# for px in range(int(root_x), int(root_x + root_w), DOT_SPACING):
#     draw.ellipse([px-1, root_y-1, px+1, root_y+1], fill=(100,0,0))

filename = "recursive_bsp_wallpaper.png"
image.save(filename)
print(f"Done! Saved as {filename}")
