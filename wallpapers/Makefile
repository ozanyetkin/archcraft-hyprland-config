# Makefile for Hyprland Dotted Wallpaper Generator
# Common tasks for wallpaper generation and management

.PHONY: help default dense sparse test apply clean variants interactive debug install

PYTHON := python3
SCRIPT := irregular_dotted_wallpaper.py
PRESET := 4k
OUTPUT := wallpaper.png

# Default target
help:
	@echo "Hyprland Dotted Wallpaper Generator - Make Targets"
	@echo "=================================================="
	@echo ""
	@echo "Quick Generation:"
	@echo "  make default      - Generate default wallpaper (balanced)"
	@echo "  make dense        - Generate dense grid (more dots)"
	@echo "  make sparse       - Generate sparse grid (fewer dots)"
	@echo "  make debug        - Generate with debug grid lines"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Generate and preview"
	@echo "  make variants     - Generate 12 test variants"
	@echo "  make interactive  - Run interactive generator"
	@echo ""
	@echo "Application:"
	@echo "  make apply        - Apply wallpaper with swww"
	@echo "  make apply-hypr   - Apply with hyprpaper"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - Remove generated wallpapers"
	@echo "  make install      - Install Python dependencies"
	@echo "  make check        - Check dependencies"
	@echo ""
	@echo "Configuration:"
	@echo "  PRESET=4k         - Resolution (fhd/qhd/4k)"
	@echo "  OUTPUT=file.png   - Output filename"
	@echo ""
	@echo "Examples:"
	@echo "  make default"
	@echo "  make dense OUTPUT=my_wallpaper.png"
	@echo "  make test PRESET=qhd"
	@echo ""

# Default wallpaper (balanced settings)
default:
	@echo "Generating default wallpaper..."
	$(PYTHON) $(SCRIPT) --preset $(PRESET) -o $(OUTPUT)
	@echo "✓ Done: $(OUTPUT)"

# Dense grid (more dots for complex layouts)
dense:
	@echo "Generating dense wallpaper..."
	$(PYTHON) $(SCRIPT) --preset $(PRESET) --max-depth 10 --min-spacing 4 -o $(OUTPUT)
	@echo "✓ Done: $(OUTPUT)"

# Sparse grid (minimal look)
sparse:
	@echo "Generating sparse wallpaper..."
	$(PYTHON) $(SCRIPT) --preset $(PRESET) --max-depth 6 --min-spacing 12 -o $(OUTPUT)
	@echo "✓ Done: $(OUTPUT)"

# Debug version with grid lines
debug:
	@echo "Generating debug wallpaper with grid lines..."
	$(PYTHON) $(SCRIPT) --preset $(PRESET) --show-grid -o debug_$(OUTPUT)
	@echo "✓ Done: debug_$(OUTPUT)"

# Small dots (subtle)
small:
	@echo "Generating wallpaper with small dots..."
	$(PYTHON) $(SCRIPT) --preset $(PRESET) --dot-radius 1 -o $(OUTPUT)
	@echo "✓ Done: $(OUTPUT)"

# Large dots (prominent)
large:
	@echo "Generating wallpaper with large dots..."
	$(PYTHON) $(SCRIPT) --preset $(PRESET) --dot-radius 3 -o $(OUTPUT)
	@echo "✓ Done: $(OUTPUT)"

# Blue theme
blue:
	@echo "Generating blue theme wallpaper..."
	$(PYTHON) $(SCRIPT) --preset $(PRESET) --dot-color 70,130,180 --bg-color 10,15,20 -o $(OUTPUT)
	@echo "✓ Done: $(OUTPUT)"

# High contrast
contrast:
	@echo "Generating high contrast wallpaper..."
	$(PYTHON) $(SCRIPT) --preset $(PRESET) --dot-color 150,150,150 --bg-color 0,0,0 -o $(OUTPUT)
	@echo "✓ Done: $(OUTPUT)"

# Subtle dark gray
subtle:
	@echo "Generating subtle dark gray wallpaper..."
	$(PYTHON) $(SCRIPT) --preset $(PRESET) --dot-color 90,90,90 --bg-color 15,15,15 -o $(OUTPUT)
	@echo "✓ Done: $(OUTPUT)"

# Generate and preview
test: default
	@echo "Generated: $(OUTPUT)"
	@if command -v feh > /dev/null; then \
		echo "Opening preview with feh..."; \
		feh $(OUTPUT) & \
	elif command -v sxiv > /dev/null; then \
		echo "Opening preview with sxiv..."; \
		sxiv $(OUTPUT) & \
	else \
		echo "Install feh or sxiv for preview"; \
	fi

# Generate multiple variants
variants:
	@echo "Generating 12 wallpaper variants..."
	./generate_variants.sh
	@echo "✓ Check variants/ directory"

# Interactive generator
interactive:
	./create_wallpaper.sh

# Apply with swww
apply:
	@if command -v swww > /dev/null; then \
		echo "Applying wallpaper with swww..."; \
		swww img $(OUTPUT); \
		echo "✓ Wallpaper applied"; \
	else \
		echo "Error: swww not found"; \
		echo "Install: yay -S swww"; \
		exit 1; \
	fi

# Apply with hyprpaper
apply-hypr:
	@if command -v hyprctl > /dev/null; then \
		echo "Applying wallpaper with hyprpaper..."; \
		hyprctl hyprpaper wallpaper ",$(PWD)/$(OUTPUT)"; \
		echo "✓ Wallpaper applied"; \
	else \
		echo "Error: hyprctl not found"; \
		exit 1; \
	fi

# Generate and apply in one step
quick: default apply

# Clean generated files
clean:
	@echo "Cleaning generated wallpapers..."
	rm -f wallpaper*.png irregular_dotted_wallpaper.png debug*.png test*.png
	rm -rf variants/
	@echo "✓ Cleaned"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	@if command -v pip > /dev/null; then \
		pip install Pillow; \
	elif command -v pacman > /dev/null; then \
		sudo pacman -S python-pillow; \
	else \
		echo "Please install Pillow manually"; \
		exit 1; \
	fi
	@echo "✓ Dependencies installed"

# Check dependencies
check:
	@echo "Checking dependencies..."
	@echo -n "Python 3: "
	@if command -v python3 > /dev/null; then \
		python3 --version; \
	else \
		echo "NOT FOUND"; \
	fi
	@echo -n "Pillow: "
	@if python3 -c "import PIL" 2>/dev/null; then \
		python3 -c "import PIL; print(PIL.__version__)"; \
	else \
		echo "NOT FOUND"; \
	fi
	@echo -n "swww: "
	@if command -v swww > /dev/null; then \
		echo "FOUND"; \
	else \
		echo "NOT FOUND (optional)"; \
	fi
	@echo -n "hyprctl: "
	@if command -v hyprctl > /dev/null; then \
		echo "FOUND"; \
	else \
		echo "NOT FOUND (optional)"; \
	fi

# Resolution-specific targets
fhd:
	$(MAKE) default PRESET=fhd OUTPUT=wallpaper_1080p.png

qhd:
	$(MAKE) default PRESET=qhd OUTPUT=wallpaper_1440p.png

4k:
	$(MAKE) default PRESET=4k OUTPUT=wallpaper_4k.png

uhd:
	$(MAKE) default PRESET=uhd OUTPUT=wallpaper_uhd.png

# Quick presets combining settings
minimal: sparse small

detailed: dense large

professional: subtle
	@echo "Professional theme created"

cyberpunk: blue dense
	@echo "Cyberpunk theme created"

# All-in-one: generate, test, and apply
all: default test apply

# Show current configuration
config:
	@echo "Current Configuration:"
	@echo "  Resolution: $(PRESET)"
	@echo "  Output: $(OUTPUT)"
	@echo "  Script: $(SCRIPT)"
	@echo "  Python: $(PYTHON)"

# Generate with custom Hyprland settings
custom:
	@read -p "Enter gaps_out [12]: " gaps_out; \
	read -p "Enter gaps_in [6]: " gaps_in; \
	read -p "Enter border_size [4]: " border_size; \
	read -p "Enter top_bar [32]: " top_bar; \
	gaps_out=$${gaps_out:-12}; \
	gaps_in=$${gaps_in:-6}; \
	border_size=$${border_size:-4}; \
	top_bar=$${top_bar:-32}; \
	$(PYTHON) $(SCRIPT) --preset $(PRESET) \
		--gaps-out $$gaps_out \
		--gaps-in $$gaps_in \
		--border-size $$border_size \
		--top-bar $$top_bar \
		-o $(OUTPUT); \
	echo "✓ Custom wallpaper generated"
