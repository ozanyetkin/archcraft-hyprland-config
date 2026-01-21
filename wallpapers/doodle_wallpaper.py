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
RANDOM_SEED = None  # Set to None for truly random, or a number for reproducible results
FILL_PROBABILITY = 0.5  # Probability (0-1) that a cell will be filled
CORNER_RADIUS = 20  # Corner radius for rounded rectangles
MAX_MERGE_SIZE = 3  # Maximum size of merged cells (1 = no merging, 2 = 2x2, 3 = 3x3, etc.)
RENDER_SCALE = 4  # Render at higher resolution and downsample for smoother edges
DRAW_GRID_LINES = False  # Set to True to draw grid lines for alignment verification
SHAPE_MARGIN = 0.5  # Margin multiplier for shapes (0.5 = half gap, 1.0 = full gap, etc.)

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
def draw_recursive_shapes(draw, x, y, w, h, level, min_level, padding, filled_cells, container_x, container_y, container_w, container_h, corner_radius):
    """
    Recursively subdivide space and randomly fill cells with rounded rectangles.
    Cells can be merged to create larger shapes. Prevents overlapping shapes and merging beyond boundaries.
    
    Args:
        draw: ImageDraw object
        x, y: Top-left coordinates
        w, h: Width and height of current cell
        level: Current recursion depth
        min_level: Minimum depth to stop recursing
        padding: Padding between shapes
        filled_cells: Set of filled cell coordinates to prevent overlaps
        container_x, container_y, container_w, container_h: Container boundaries
    """
    if level < min_level:
        # Base case: decide whether to fill and potentially merge
        cell_key = (int(x), int(y), int(w), int(h))
        
        # Skip if already filled
        if cell_key in filled_cells:
            return
        
        if random.random() < FILL_PROBABILITY:
            # Randomly decide merge size for width and height independently
            merge_w = random.randint(1, MAX_MERGE_SIZE)
            merge_h = random.randint(1, MAX_MERGE_SIZE)
            
            # Calculate merged dimensions
            merged_w = w * merge_w
            merged_h = h * merge_h
            
            # Check if merged area would exceed container boundaries
            merged_x2 = x + merged_w
            merged_y2 = y + merged_h
            container_x2 = container_x + container_w
            container_y2 = container_y + container_h
            
            exceeds_boundary = (merged_x2 > container_x2) or (merged_y2 > container_y2)
            
            # Check if merged area would overlap with filled cells
            can_merge = not exceeds_boundary
            if can_merge:
                for i in range(merge_w):
                    for j in range(merge_h):
                        check_key = (int(x + w * i), int(y + h * j), int(w), int(h))
                        if check_key in filled_cells:
                            can_merge = False
                            break
                    if not can_merge:
                        break
            
            if can_merge:
                # Mark all merged cells as filled
                for i in range(merge_w):
                    for j in range(merge_h):
                        filled_cells.add((int(x + w * i), int(y + h * j), int(w), int(h)))
                
                color = random.choice(COLOR_PALETTE)
                # Add padding to the shape
                x1 = int(x + padding)
                y1 = int(y + padding)
                x2 = int(x + merged_w - padding)
                y2 = int(y + merged_h - padding)
                
                if x2 > x1 and y2 > y1:  # Only draw if there's space
                    radius = min(int(corner_radius), (x2 - x1) // 2, (y2 - y1) // 2)
                    if radius < 0:
                        radius = 0
                    draw.rounded_rectangle(
                        [(x1, y1), (x2, y2)],
                        radius=radius,
                        fill=color
                    )
        return
    
    # Recursive case: subdivide and recurse
    mid_x = x + (w / 2)
    mid_y = y + (h / 2)
    new_w = w / 2
    new_h = h / 2
    
    # Draw grid lines if enabled (for debugging)
    if DRAW_GRID_LINES:
        line_color = (53, 53, 53)  # Dark gray
        line_width = max(1, int(2 * RENDER_SCALE))
        # Vertical line
        draw.line([(mid_x, y), (mid_x, y + h)], fill=line_color, width=line_width)
        # Horizontal line
        draw.line([(x, mid_y), (x + w, mid_y)], fill=line_color, width=line_width)
    
    # Recurse into four quadrants
    draw_recursive_shapes(draw, x, y, new_w, new_h, level - 1, min_level, padding, filled_cells, container_x, container_y, container_w, container_h, corner_radius)
    draw_recursive_shapes(draw, mid_x, y, new_w, new_h, level - 1, min_level, padding, filled_cells, container_x, container_y, container_w, container_h, corner_radius)
    draw_recursive_shapes(draw, x, mid_y, new_w, new_h, level - 1, min_level, padding, filled_cells, container_x, container_y, container_w, container_h, corner_radius)
    draw_recursive_shapes(draw, mid_x, mid_y, new_w, new_h, level - 1, min_level, padding, filled_cells, container_x, container_y, container_w, container_h, corner_radius)


# ================= MAIN LOOP =================
# Set random seed for reproducibility
if RANDOM_SEED is not None:
    random.seed(RANDOM_SEED)

for m in MONITORS:
    print(f"Processing {m['name']}...")

    # 1. Calculate Physical Dimensions at logical resolution first
    scale = m["scale"]
    bar_px_logical = int(m["bar_logical_height"] * scale)
    gap_px_logical = int(m["gap_logical"] * scale)

    # Define the "Tiling Container" area at logical resolution
    container_x_logical = gap_px_logical
    container_y_logical = bar_px_logical + gap_px_logical
    container_w_logical = m["width"] - (gap_px_logical * 2)
    container_h_logical = m["height"] - (bar_px_logical + (gap_px_logical * 2))

    # Now scale everything for high-resolution rendering
    bar_px = bar_px_logical * RENDER_SCALE
    gap_px = gap_px_logical * RENDER_SCALE
    container_x = container_x_logical * RENDER_SCALE
    container_y = container_y_logical * RENDER_SCALE
    container_w = container_w_logical * RENDER_SCALE
    container_h = container_h_logical * RENDER_SCALE

    # Calculate padding for shapes based on margin parameter
    padding = max(1, int(gap_px * SHAPE_MARGIN))

    # 3. Create Image at higher resolution
    img = Image.new(
        "RGB",
        (int(m["width"] * RENDER_SCALE), int(m["height"] * RENDER_SCALE)),
        COLOR_BG,
    )
    draw = ImageDraw.Draw(img)

    # 4. Draw recursive shapes
    print(
        f"  - Container Area: {container_w}x{container_h} (Offset: {container_x}, {container_y})"
    )
    filled_cells = set()
    corner_radius = max(1, int(CORNER_RADIUS * scale * RENDER_SCALE))
    draw_recursive_shapes(
        draw,
        container_x,
        container_y,
        container_w,
        container_h,
        MAX_DEPTH,
        MIN_DEPTH,
        padding,
        filled_cells,
        container_x,
        container_y,
        container_w,
        container_h,
        corner_radius,
    )

    # 5. Downsample to target resolution for smooth edges
    img = img.resize((m["width"], m["height"]), resample=Image.Resampling.LANCZOS)

    # 6. Save
    filename = f"wallpaper_{m['name']}.png"
    img.save(filename)
    print(f"  - Saved to {filename}")

print("\nAll Done! Move these files to your wallpaper folder.")
