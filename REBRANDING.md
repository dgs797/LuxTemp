# Rebranding: Lumixan → LuxTemp

## Summary
The application has been rebranded from **Lumixan** to **LuxTemp**.

## Name Meaning
- **Lux** - Unit of illuminance (light measurement)
- **Temp** - Temperature (color temperature)

## Files Updated

### Core Application
- ✅ `lumixan.py` → **`luxtemp.py`** (renamed)
  - Updated docstring
  - Changed window title to "LuxTemp"
  - Updated system tray title

### Desktop Integration
- ✅ `brightness-control.desktop`
  - Name: LuxTemp
  - Exec: luxtemp
  - Keywords: luxtemp

- ✅ `brightness-control-autostart.desktop`
  - Name: LuxTemp (Tray)
  - Exec: luxtemp --tray

### Installation Scripts
- ✅ `install.sh`
  - Updated all references to luxtemp.py
  - Creates `/usr/local/bin/luxtemp` as primary command
  - Creates symlinks for backward compatibility:
    - `lumixan` → `luxtemp`
    - `brightness-control` → `luxtemp`

- ✅ `uninstall.sh`
  - Removes all three commands (luxtemp, lumixan, brightness-control)

### Documentation
- ✅ `README.md` - All references updated
- ✅ `BRANDING.md` - Complete rebrand documentation
- ✅ `CHANGES.md` - Title updated
- ✅ `FEATURES.md` - All references updated
- ✅ `RESPONSIVE_DESIGN.md` - Title updated
- ✅ `SYSTEM_TRAY_GUIDE.md` - All references updated

## Command Reference

### Primary Command
```bash
luxtemp              # Launch with window
luxtemp --tray       # Launch in system tray
luxtemp --hidden     # Launch hidden
```

### Backward Compatibility (after installation)
```bash
lumixan              # Still works (symlink)
brightness-control   # Still works (symlink)
```

### Direct Execution
```bash
python3 luxtemp.py
./luxtemp.py
```

## Installation
After rebranding, users should:
1. Run `./install.sh` to install with new name
2. The app will appear as "LuxTemp" in application menu
3. Old commands (`lumixan`, `brightness-control`) will still work via symlinks

## What Users Will See
- **Application Menu**: LuxTemp
- **Window Title Bar**: LuxTemp
- **System Tray**: LuxTemp
- **Main Window Label**: "Brightness" (as requested)

## Notes
- Icon files remain named `brightness-control.svg` for compatibility
- Installation directory remains `/opt/brightness-control` for compatibility
- Desktop files remain named `brightness-control*.desktop` for compatibility
- Only user-facing names and commands have been updated
