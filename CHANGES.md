# Lumixan - Recent Changes

## Version 2.0 - Color Temperature & UI Improvements

### New Features
- ✅ **Color Temperature Control** - f.lux-like blue light reduction (2000K-6500K)
- ✅ **Temperature Presets** - Quick buttons: Warm (2700K), Sunset (4000K), Day (5500K), Cool (6500K)
- ✅ **Resizable Window** - Window can now be resized and maximized
- ✅ **Custom Logo** - Beautiful SVG logo with sun and color temperature indicators
- ✅ **Improved UI Numbering** - Display shows 25-100% (actual brightness stays 50-100% for safety)

### UI Changes
- Brightness display now shows: 25%, 50%, 75%, 100% (mapped from actual 50%, 67%, 83%, 100%)
- Window is now resizable (default size: 450x600)
- Added section divider between brightness and color temperature
- Color temperature section with orange accent color (#ff9a56)
- Temperature slider ranges from 2000K (very warm) to 6500K (neutral)

### Technical Details
- Brightness actual range: 50-100% (prevents screen from being too dark)
- Brightness display range: 25-100% (for better user experience)
- Color temperature uses xrandr gamma adjustment
- Custom icon installed to system icon theme
- Icon fallback to local SVG file when running directly

### Installation
Run `./install.sh` to install the updated version with:
- New color temperature features
- Custom application icon
- Updated desktop entry

### Usage
- **Brightness Slider**: Adjust from 25% to 100% (actual: 50-100%)
- **Temperature Slider**: Adjust from 2000K (warm) to 6500K (cool)
- Lower temperature = warmer colors = less blue light (better for night)
- Higher temperature = cooler colors = neutral white (normal daylight)

### Note
Color temperature control requires xrandr and may not work with backlight-only systems. The app will show a message if color temperature is not supported on your system.
