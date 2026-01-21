from PIL import Image, ImageDraw
import random

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
    },
    {
        "name": "eDP-1",
        "width": 1920,
        "height": 1200,
        "scale": 1.0,
        "bar_logical_height": 38,
        "gap_logical": 12,
    },
]

# Shared Aesthetics
MIN_DEPTH = 2  # Minimum recursion depth (smaller shapes)
MAX_DEPTH = 6  # Maximum recursion depth (larger shapes)
RANDOM_SEED = 42  # Set to None for truly random, or a number for reproducible results
FILL_PROBABILITY = 0.7  # Probability (0-1) that a cell will be filled
CORNER_RADIUS = 20  # Corner radius for rounded rectangles

# Color Palette (RGB tuples)
COLOR_PALETTE = [
    (240, 113, 120),  # #f07178 (red)
    (195, 232, 141),  # #c3e88d (green)
    (255, 203, 107),  # #ffcb6b (yellow)
    (130, 170, 255),  # #82aaff (blue)
    (199, 146, 234),  # #c792ea (purple)
    (137, 221, 255),  # #89ddff (cyan)
]

COLOR_BG = (0, 0, 0)  # Pure Black Background


# ================= RECURSIVE SHAPE GENERATION =================
def draw_recursive_shapes(draw, x, y, w, h, level, min_level, padding):
    """
    Recursively subdivide space and randomly fill cells with rounded rectangles.
    
    Args:
        draw: ImageDraw object
        x, y: Top-left coordinates
        w, h: Width and height of current cell
        level: Current recursion depth
        min_level: Minimum depth to stop recursing
        padding: Padding between shapes
    """
    if level < min_level:
        # Base case: draw a filled rounded rectangle
        if random.random() < FILL_PROBABILITY:
            color = random.choice(COLOR_PALETTE)
            # Add padding to the shape
            x1 = int(x + padding)
            y1 = int(y + padding)
            x2 = int(x + w - padding)
            y2 = int(y + h - padding)
            
            if x2 > x1 and y2 > y1:  # Only draw if there's space
                draw.rounded_rectangle(
                    [(x1, y1), (x2, y2)],
                    radius=CORNER_RADIUS,
                    fill=color
                )
        return
    
    # Recursive case: subdivide and recurse
    mid_x = x + (w / 2)
    mid_y = y + (h / 2)
    new_w = w / 2
    new_h = h / 2
    
    # Recurse into four quadrants
    draw_recursive_shapes(draw, x, y, new_w, new_h, level - 1, min_level, padding)
    draw_recursive_shapes(draw, mid_x, y, new_w, new_h, level - 1, min_level, padding)
    draw_recursive_shapes(draw, x, mid_y, new_w, new_h, level - 1, min_level, padding)
    draw_recursive_shapes(draw, mid_x, mid_y, new_w, new_h, level - 1, min_level, padding)


# ================= MAIN LOOP =================
# Set random seed for reproducibility
if RANDOM_SEED is not None:
    random.seed(RANDOM_SEED)

for m in MONITORS:
    print(f"Processing {m['name']}...")

    # 1. Calculate Physical Dimensions
    # We round to ensure pixel-perfect integer coordinates
    scale = m["scale"]
    bar_px = int(m["bar_logical_height"] * scale)
    gap_px = int(m["gap_logical"] * scale)

    # Calculate padding for shapes
    padding = int(gap_px * 0.8)

    # 2. Define the "Tiling Container" area
    # This is the area where windows actually live
    container_x = gap_px
    container_y = bar_px + gap_px
    container_w = m["width"] - (gap_px * 2)
    container_h = m["height"] - (bar_px + (gap_px * 2))

    # 3. Create Image
    img = Image.new("RGB", (m["width"], m["height"]), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # 4. Draw recursive shapes
    print(
        f"  - Container Area: {container_w}x{container_h} (Offset: {container_x}, {container_y})"
    )
    draw_recursive_shapes(
        draw,
        container_x,
        container_y,
        container_w,
        container_h,
        MAX_DEPTH,
        MIN_DEPTH,
        padding,
    )

    # 5. Save
    filename = f"wallpaper_{m['name']}.png"
    img.save(filename)
    print(f"  - Saved to {filename}")

print("\nAll Done! Move these files to your wallpaper folder.")
