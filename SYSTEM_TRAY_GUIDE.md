# LuxTemp - System Tray Integration Guide

## Overview
LuxTemp supports system tray integration, allowing it to run in the notification area (lower right corner) of your Linux desktop.

## Features

### System Tray Icon
- **Icon in notification area** - App appears in the lower right system tray
- **Quick access menu** - Right-click the icon for quick controls
- **Minimize to tray** - Closing the window minimizes to tray instead of quitting
- **Always running** - App stays in background for quick access

### Tray Menu Options
1. **Show/Hide Window** - Toggle the main window
2. **Brightness** submenu:
   - 25%, 50%, 75%, 100% presets
3. **Color Temperature** submenu (if supported):
   - Ember (1000K) - Extreme warm, like f.lux Ember mode
   - Warm (2700K)
   - Sunset (4000K)
   - Day (5500K)
   - Cool (6500K)
4. **Quit** - Exit the application and reset to defaults (100% brightness, 6500K temperature)

## Installation

### Install Dependencies
```bash
sudo apt install gir1.2-appindicator3-0.1
```

### Run the Installer
```bash
./install.sh
```

The installer will automatically install system tray support.

## Usage

### Start in System Tray
```bash
luxtemp --tray
```

This starts the app hidden in the system tray.

### Start with Window Visible
```bash
luxtemp
```

This starts the app with the window visible (traditional mode).

### From Application Menu
Search for "LuxTemp" in your application menu and click it.

## Autostart on Login

To have the app start automatically in the system tray when you log in:

### Option 1: Manual Setup
1. Copy the autostart file:
```bash
mkdir -p ~/.config/autostart
cp brightness-control-autostart.desktop ~/.config/autostart/
```

2. The app will now start in the system tray on every login

### Option 2: Using XFCE Settings
1. Open "Session and Startup" in XFCE settings
2. Go to "Application Autostart" tab
3. Click "Add" button
4. Fill in:
   - **Name**: LuxTemp
   - **Description**: Brightness and color temperature control
   - **Command**: `luxtemp --tray`
5. Click "OK"

## Behavior

### Window Closing
- **With system tray**: Clicking X minimizes to tray (app keeps running)
- **Without system tray**: Clicking X quits the app completely

### Quitting the App
- **From tray menu**: Select "Quit" to exit completely
- **Auto-reset on quit**: Brightness resets to 100%, temperature resets to 6500K
- **Why reset?**: Ensures your screen returns to normal settings when you're done

### Accessing the Window
- Click the tray icon and select "Show/Hide Window"
- Or run `luxtemp` again (will show existing window)

### Quick Adjustments
- Right-click the tray icon
- Select brightness or temperature preset
- Changes apply immediately without opening the window

## Troubleshooting

### No Tray Icon Appears
1. Check if AppIndicator is installed:
```bash
dpkg -l | grep appindicator3
```

2. Install if missing:
```bash
sudo apt install gir1.2-appindicator3-0.1
```

3. Restart the app

### Tray Icon Not Working in Some Desktop Environments
Some desktop environments don't support AppIndicator. The app will still work normally, but won't show a tray icon.

**Supported**:
- XFCE (with xfce4-indicator-plugin)
- GNOME (with TopIcons Plus extension)
- Ubuntu Unity
- KDE Plasma
- MATE
- Cinnamon

**May need additional setup**:
- Install indicator plugin for your desktop environment

## Benefits

1. **Always accessible** - Quick access from system tray
2. **No taskbar clutter** - Doesn't take up taskbar space
3. **Quick adjustments** - Change settings without opening window
4. **Background operation** - Stays running for instant access
5. **Autostart support** - Can start automatically on login

## Commands Summary

```bash
# Start with window visible
luxtemp

# Start in system tray (hidden)
luxtemp --tray

# Start in system tray (alternative)
luxtemp --hidden

# Enable autostart
cp brightness-control-autostart.desktop ~/.config/autostart/

# Backward compatibility (also works)
brightness-control
```

## Tips

- Use autostart to have the app always available in your system tray
- Use tray menu for quick brightness/temperature changes
- Open the window when you need precise control with sliders
- The app remembers your last settings
