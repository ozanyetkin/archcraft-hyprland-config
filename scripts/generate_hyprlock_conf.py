#!/usr/bin/env python3
"""
generate_hyprlock_conf.py

Generate a responsive `hyprlock.conf` tuned to the current monitor resolution (or supplied size).
This script produces a hyprlock configuration where image sizes, input-field, fonts and positional
offsets are scaled so the lock screen looks balanced on both low and high DPI displays.

Usage:
    python3 generate_hyprlock_conf.py [--width WIDTH --height HEIGHT] [--scale SCALE]
                                      [--layout {image,text}] [--out PATH]
                                      [--wallpaper PATH] [--profilepic PATH]
                                      [--no-backup]

If --width/--height are not provided the script attempts to auto-detect the active output
resolution by querying `hyprctl`, `swaymsg` or `xrandr`. If detection fails, defaults to 1920x1080.

The generated file defaults to writing to:
    archcraft-hyprland-config/hyprlock.conf

The script will create a backup of the destination file (appending `.bak`) unless --no-backup
is passed.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from typing import Optional, Tuple

# Defaults taken from the user's existing template
DEFAULT_OUT = "archcraft-hyprland-config/hyprlock.conf"
DEFAULT_WALLPAPER = "/home/yetkin/.config/hyprcat/wallpapers/wallpaper.png"
DEFAULT_PROFILEPIC = "~/.config/hyprcat/wallpapers/profile.jpg"

# Base resolution used to compute scaling (feel free to tweak)
BASE_WIDTH = 1920
MIN_SCALE = 1.0
MAX_SCALE = 3.0


def detect_resolution() -> Optional[Tuple[int, int]]:
    """
    Try to detect the active monitor resolution using hyprctl, swaymsg or xrandr.
    Returns (width, height) or None if detection failed.
    """
    # 1) hyprctl monitors -j
    try:
        out = subprocess.check_output(
            ["hyprctl", "monitors", "-j"], stderr=subprocess.DEVNULL, timeout=1
        )
        data = json.loads(out.decode())
        # Choose the focused monitor, or first one
        focused = None
        for m in data:
            if m.get("focused"):
                focused = m
                break
        if not focused and data:
            focused = data[0]
        if focused:
            w = int(focused.get("width", focused.get("monitorWidth", 0)))
            h = int(focused.get("height", focused.get("monitorHeight", 0)))
            if w and h:
                return w, h
    except Exception:
        pass

    # 2) swaymsg -t get_outputs
    try:
        out = subprocess.check_output(
            ["swaymsg", "-t", "get_outputs"], stderr=subprocess.DEVNULL, timeout=1
        )
        data = json.loads(out.decode())
        focused = None
        for m in data:
            if m.get("active") and m.get("focused"):
                focused = m
                break
        if not focused:
            for m in data:
                if m.get("active"):
                    focused = m
                    break
        if focused:
            rect = focused.get("rect") or {}
            w = int(rect.get("width", 0))
            h = int(rect.get("height", 0))
            if w and h:
                return w, h
    except Exception:
        pass

    # 3) xrandr fallback (X)
    try:
        out = subprocess.check_output(
            ["xrandr", "--current"], stderr=subprocess.DEVNULL, timeout=1
        ).decode()
        # find the primary or first connected line
        for line in out.splitlines():
            if " connected " in line:
                # look for something like "1920x1080"
                parts = line.split()
                for p in parts:
                    if "x" in p and "+" in p:
                        # format: 1920x1080+0+0
                        size = p.split("+")[0]
                        w, h = size.split("x", 1)
                        return int(w), int(h)
                    elif (
                        "x" in p and p.count("x") == 1 and p.replace("x", "").isdigit()
                    ):
                        w, h = p.split("x", 1)
                        return int(w), int(h)
        # If not found in connected line, try modes lines
    except Exception:
        pass

    return None


def compute_scale(
    width: int, height: int, explicit_scale: Optional[float] = None
) -> float:
    """
    Compute a scale factor for sizing elements. If explicit_scale provided, use it (clamped).
    Otherwise derive from width / BASE_WIDTH with smooth scaling and clamps.
    """
    if explicit_scale is not None:
        return max(MIN_SCALE, min(MAX_SCALE, float(explicit_scale)))
    ratio = float(width) / float(BASE_WIDTH)
    # make sure small screens don't go below 1.0
    scale = max(MIN_SCALE, ratio)
    # dampen large screens: use square root to avoid very large numbers for ultrawide displays
    if scale > 1.25:
        scale = 1.0 + (math.sqrt(scale) - 1.0) * 1.25
    return max(MIN_SCALE, min(MAX_SCALE, scale))


def scaled(value: float, scale: float) -> int:
    """Helper to scale and round integer values predictably"""
    return int(round(value * scale))


HYPRLOCK_TEMPLATE = """# Generated by generate_hyprlock_conf.py
# Responsive hyprlock configuration
# scale = {scale:.3f}  (detected/respectively supplied)

# Images and Colors
$wallpaper = {wallpaper}
$profilepic = {profilepic}
$bg_color = rgba(0, 0, 0, 1.0)
$outer_color = rgba(238, 255, 255, 0.0)
$inner_color = rgba(238, 255, 255, 0.1)
$check_color = rgba(196, 232, 141, 1.0)
$fail_color = rgba(240, 113, 119, 1.0)
$label_color = rgba(238, 255, 255, 0.7)
$label_color_hex = ##eeffff99

# General
general {{
    hide_cursor = false
    ignore_empty_input = false
    immediate_render = false
    text_trim = true
    fractional_scaling = 2
    screencopy_mode = 0
    fail_timeout = 2000
}}

# Authentication
auth {{
    pam:enabled = true
    pam:module = hyprlock
    fingerprint:enabled = false
    fingerprint:ready_message = (Scan fingerprint to unlock)
    fingerprint:present_message = Scanning fingerprint
    fingerprint:retry_delay = 250
}}

# Animations (kept subtle and fast)
animations {{
    enabled = true
    animation = fadeIn,1,8
    animation = fadeOut,1,8
    animation = inputFieldColors,1,10
    animation = inputFieldFade,1,8
    animation = inputFieldWidth,1,10
    animation = inputFieldDots,1,8
}}

# Background
background {{
    monitor =
    path = $wallpaper
    color = $bg_color
    blur_passes = 2
    blur_size = 8
    noise = 0.0120
    contrast = 0.89
    brightness = 0.82
    vibrancy = 0.17
    vibrancy_darkness = 0.0
    reload_time = -1
    reload_cmd =
    crossfade_time = -1.0
    zindex = -1
}}

# Profile image (scaled)
image {{
    monitor =
    path = $profilepic
    size = {image_size}
    rounding = -1
    border_size = 0
    border_color = $label_color
    rotate = 0
    reload_time = -1
    reload_cmd =

    position = 0, {image_y}
    halign = center
    valign = center
    zindex = 0

    shadow_passes = 3
    shadow_size = {shadow_size}
    shadow_color = rgb(0, 0, 0)
    shadow_boost = 1.0
}}

# Input-field
input-field {{
    monitor =
    size = {input_width}, {input_height}
    outline_thickness = 2
    dots_size = {dots_size:.3f}
    dots_spacing = {dots_spacing:.3f}
    dots_center = true
    dots_rounding = -2
    dots_text_format =
    outer_color = $outer_color
    inner_color = $inner_color
    font_color = $label_color
    font_family = Iosevka Nerd Font
    fade_on_empty = false
    fade_timeout = 1000
    placeholder_text = <span foreground="$label_color_hex">echo $SECRET | unlock</span>
    hide_input = false
    rounding = -1
    check_color = $check_color
    fail_color = $fail_color
    fail_text = <i>$FAIL <b>($ATTEMPTS)</b></i>
    capslock_color = -1
    numlock_color = -1
    bothlock_color = -1
    invert_numlock = false
    swap_font_color = false

    position = 0, {input_y}
    halign = center
    valign = center
    zindex = 0

    shadow_passes = 3
    shadow_size = {shadow_size}
    shadow_color = rgb(0, 0, 0)
    shadow_boost = 1.0
}}

# Word Clock (text-based)
label {{
    monitor =
    text = cmd[update:1000] python3 /home/yetkin/Desktop/Projects/archcraft-hyprland-config/scripts/wordclock.py
    color = $label_color
    font_size = {font_wordclock}
    font_family = Iosevka Nerd Font
    position = 0, {wordclock_y}
    halign = center
    valign = center
}}

# Date
label {{
    monitor =
    text = cmd[update:1000] python3 -c "from datetime import date; ords=['zero','first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth','eleventh','twelfth','thirteenth','fourteenth','fifteenth','sixteenth','seventeenth','eighteenth','nineteenth','twentieth','twenty-first','twenty-second','twenty-third','twenty-fourth','twenty-fifth','twenty-sixth','twenty-seventh','twenty-eighth','twenty-ninth','thirtieth','thirty-first']; d=date.today(); print(f\"{{d.strftime('%B')}} {{ords[d.day]}}\")"
    color = $label_color
    font_size = {font_date}
    font_family = Iosevka Nerd Font
    position = 0, {date_y}
    halign = center
    valign = center
}}

# Day (weekday)
label {{
    monitor =
    text = cmd[update:1000] date +"%A"
    color = $label_color
    font_size = {font_day}
    font_family = Iosevka Nerd Font
    position = 0, {day_y}
    halign = center
    valign = center
}}

# USER-BOX (subtle container behind the input)
shape {{
    monitor =
    size = {userbox_w}, {userbox_h}
    color = $inner_color
    rounding = -1
    border_size = 0
    border_color = $outer_color
    rotate = 0
    xray = false

    position = 0, {userbox_y}
    halign = center
    valign = center
}}

# USER label
label {{
    monitor =
    text = father, is that you?
    color = $label_color
    font_size = {font_user}
    font_family = Iosevka Nerd Font
    position = 0, {label_user_y}
    halign = center
    valign = center
}}

# --- Actions (text-based, responsive-ish)
label {{
    monitor =
    text = Reboot
    color = $label_color
    font_family = Iosevka Nerd Font
    font_size = {font_actions}
    onclick = systemctl reboot
    position = -{actions_x}, {actions_y}
    halign = center
    valign = bottom
}}

label {{
    monitor =
    text = Suspend
    color = $label_color
    font_family = Iosevka Nerd Font
    font_size = {font_actions}
    onclick = systemctl suspend
    position = 0, {actions_y}
    halign = center
    valign = bottom
}}

label {{
    monitor =
    text = Shutdown
    color = $label_color
    font_family = Iosevka Nerd Font
    font_size = {font_actions}
    onclick = systemctl poweroff
    position = {actions_x}, {actions_y}
    halign = center
    valign = bottom
}}
"""


def generate_conf_values(scale: float, layout: str = "image"):
    """
    Compute scaled sizes and positions. Returns a dict with template values.
    All numbers are tuned to produce similar layout semantics as the original file.
    """
    # Base sizes from original
    base_image_size = 120
    base_image_y = 28
    base_shadow_size = 6

    base_input_w = 320
    base_input_h = 50
    base_input_y = -190

    base_wordclock_y = 260
    base_date_y = 200
    base_day_y = 150

    base_userbox_w = 340
    base_userbox_h = 64
    base_userbox_y = -120
    base_label_user_y = -120

    base_font_wordclock = 40
    base_font_date = 30
    base_font_day = 22
    base_font_user = 14
    base_font_actions = 14

    base_actions_x = 180
    base_actions_y = 90

    # For very high scale, we might want to increase horizontal spacing slightly less than linear
    actions_x = max(60, int(round(base_actions_x * (0.9 + 0.6 * scale / MAX_SCALE))))

    vals = {
        "scale": scale,
        "wallpaper": DEFAULT_WALLPAPER,
        "profilepic": DEFAULT_PROFILEPIC,
        "image_size": scaled(base_image_size, scale) if layout == "image" else 0,
        "image_y": scaled(base_image_y, scale) if layout == "image" else 0,
        "shadow_size": scaled(base_shadow_size, scale),
        "input_width": scaled(base_input_w, scale),
        "input_height": scaled(base_input_h, scale),
        "input_y": scaled(base_input_y, scale),
        "dots_size": max(0.08, 0.18 * (1.0 / scale)),  # keep dots visible but not huge
        "dots_spacing": max(0.1, 0.2 * (1.0 / scale)),
        "wordclock_y": scaled(base_wordclock_y, scale),
        "date_y": scaled(base_date_y, scale),
        "day_y": scaled(base_day_y, scale),
        "font_wordclock": scaled(base_font_wordclock, scale),
        "font_date": scaled(base_font_date, scale),
        "font_day": scaled(base_font_day, scale),
        "userbox_w": scaled(base_userbox_w, scale),
        "userbox_h": scaled(base_userbox_h, scale),
        "userbox_y": scaled(base_userbox_y, scale),
        "font_user": scaled(base_font_user, scale),
        "label_user_y": scaled(base_label_user_y, scale),
        "actions_x": actions_x,
        "actions_y": scaled(base_actions_y, scale),
        "font_actions": scaled(base_font_actions, scale),
    }
    return vals


def write_conf(path: str, content: str, make_backup: bool = True) -> None:
    """Write content to path. If file exists and make_backup True, move old file to .bak"""
    if os.path.exists(path):
        if make_backup:
            bak = path + ".bak"
            # Overwrite existing backup
            try:
                shutil.copy2(path, bak)
                print(f"Existing file backed up to {bak}")
            except Exception as e:
                print(f"Warning: failed to create backup: {e}", file=sys.stderr)
    # Ensure parent dir exists
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        try:
            os.makedirs(parent, exist_ok=True)
        except Exception:
            pass
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote responsive hyprlock config to: {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate a responsive hyprlock.conf")
    parser.add_argument("--width", type=int, help="Screen width to use for scaling")
    parser.add_argument("--height", type=int, help="Screen height to use for scaling")
    parser.add_argument(
        "--scale",
        type=float,
        help="Explicit scale factor to use (overrides auto compute)",
    )
    parser.add_argument(
        "--layout",
        choices=("image", "text"),
        default="image",
        help="Layout mode: 'image' to keep profile image, 'text' to hide image and center text",
    )
    parser.add_argument(
        "--out", default=DEFAULT_OUT, help="Output path for hyprlock.conf"
    )
    parser.add_argument(
        "--wallpaper", default=DEFAULT_WALLPAPER, help="Wallpaper path to embed"
    )
    parser.add_argument(
        "--profilepic", default=DEFAULT_PROFILEPIC, help="Profile picture path to embed"
    )
    parser.add_argument(
        "--no-backup",
        dest="no_backup",
        action="store_true",
        help="Don't create .bak of existing file",
    )
    args = parser.parse_args(argv)

    width = args.width
    height = args.height

    if width is None or height is None:
        res = detect_resolution()
        if res:
            width, height = res
            print(f"Detected resolution: {width}x{height}")
        else:
            width = width or BASE_WIDTH
            height = height or int(BASE_WIDTH * 9 / 16)
            print(f"Resolution detection failed; using fallback {width}x{height}")

    scale = compute_scale(width, height, args.scale)
    print(f"Using scale factor: {scale:.3f}")

    vals = generate_conf_values(scale, layout=args.layout)
    # override wallpaper/profilepic if provided
    vals["wallpaper"] = args.wallpaper
    vals["profilepic"] = args.profilepic

    conf = HYPRLOCK_TEMPLATE.format(**vals)

    # Write output (create backup unless --no-backup)
    write_conf(args.out, conf, make_backup=not args.no_backup)

    # Print helpful summary for the user
    print("")
    print("Summary of generated values:")
    for k in (
        "image_size",
        "input_width",
        "input_height",
        "font_wordclock",
        "font_date",
        "font_day",
        "actions_x",
    ):
        if k in vals:
            print(f"  {k}: {vals[k]}")
    print("")
    print(
        "If the layout still doesn't look right, try adjusting --scale or supplying --width/--height"
    )
    print(
        "Example: python3 generate_hyprlock_conf.py --width 3840 --height 2160 --out hyprlock.conf"
    )


if __name__ == "__main__":
    main()
