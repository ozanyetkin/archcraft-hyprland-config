from PIL import Image, ImageDraw

# ================= CONFIGURATION =================
# Physical Screen Resolution
SCREEN_W = 3840
SCREEN_H = 2400

# Layout Configuration (Physical Pixels - Scaled 1.5x)
# Bar: 32px logical * 1.5 = 48px
BAR_HEIGHT = 54

# Outer Gap: 12px logical * 1.5 = 18px
GAP_OUTER = 18

# Inner Gap: 12px logical * 1.5 = 18px
# (This is the space BETWEEN windows)
GAP_INNER = 18

# Aesthetic Configuration
DEPTH = 6  # How many recursive splits to draw (5 is usually plenty)
LINE_WIDTH = 2  # Thickness of the grid lines (Try 18 to fill the gap entirely)
LINE_COLOR = (80, 80, 80)  # Grey
BG_COLOR = (10, 10, 10)  # Black/Dark Grey

# ================= SETUP =================
image = Image.new("RGB", (SCREEN_W, SCREEN_H), BG_COLOR)
draw = ImageDraw.Draw(image)

# Define the effective "Tiling Area"
# The wallpaper lines must be calculated relative to where windows actually go.
container_x = GAP_OUTER
container_y = BAR_HEIGHT + GAP_OUTER
container_w = SCREEN_W - (GAP_OUTER * 2)
container_h = SCREEN_H - (BAR_HEIGHT + GAP_OUTER * 2)


# ================= RECURSIVE FUNCTION =================
def draw_lines_recursive(x, y, w, h, level):
    if level == 0:
        return

    # Calculate the exact center of the current container
    mid_x = x + (w / 2)
    mid_y = y + (h / 2)

    # --- Draw Vertical Split Line ---
    # Draws a line from the top to bottom of the CURRENT section
    draw.line([(mid_x, y), (mid_x, y + h)], fill=LINE_COLOR, width=LINE_WIDTH)

    # --- Draw Horizontal Split Line ---
    # Draws a line from left to right of the CURRENT section
    draw.line([(x, mid_y), (x + w, mid_y)], fill=LINE_COLOR, width=LINE_WIDTH)

    # --- RECURSE ---
    # Split the area into 4 sub-quadrants and repeat
    new_w = w / 2
    new_h = h / 2

    # Top-Left
    draw_lines_recursive(x, y, new_w, new_h, level - 1)
    # Top-Right
    draw_lines_recursive(x + new_w, y, new_w, new_h, level - 1)
    # Bottom-Left
    draw_lines_recursive(x, y + new_h, new_w, new_h, level - 1)
    # Bottom-Right
    draw_lines_recursive(x + new_w, y + new_h, new_w, new_h, level - 1)


# ================= EXECUTE =================
print(f"Generating line grid for area: {container_w}x{container_h}...")
draw_lines_recursive(container_x, container_y, container_w, container_h, DEPTH)

filename = "recursive_lines_wallpaper.png"
image.save(filename)
print(f"Done! Saved to {filename}")
