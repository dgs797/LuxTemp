# LuxTemp - Feature Guide

## 🎨 Interface Overview

LuxTemp has a modern dark theme with two main sections:

### 1. Brightness Control Section (Cyan Accent)
```
☀ Brightness Control
Display: [Your Display Name]

        75%          ← Large display (mapped from actual brightness)
    
    ━━━━━●━━━━━━━    ← Slider (25% to 100% display)
    
    [25%] [50%] [75%] [100%]  ← Quick preset buttons
    
    Brightness display: 25% - 100% (actual minimum: 50% for safety)
```

**How it works:**
- Display shows: 25%, 50%, 75%, 100%
- Actual brightness: 50%, 67%, 83%, 100%
- This prevents the screen from going too dark while giving intuitive numbering

### 2. Color Temperature Section (Orange Accent)
```
    ─────────────────────────────
    
    🌡 Color Temperature
    
        6500K        ← Temperature display
    
    ━━━━━━━━━━━━━●   ← Temperature slider (1000K to 6500K)
    
    [🌙 Ember] [🔥 Warm] [🌅 Sunset] [☀️ Day] [❄️ Cool]  ← Temperature presets
    
    Lower temperature = warmer/less blue light (better for night)
```

**Temperature Guide:**
- **1000K (Ember)** 🌙 - Extreme warm mode, like f.lux Ember (maximum blue light reduction for late night)
- **2700K (Warm)** 🔥 - Very warm, strong blue light reduction (late night)
- **4000K (Sunset)** 🌅 - Moderate warmth (evening)
- **5500K (Day)** ☀️ - Slightly warm (comfortable daytime)
- **6500K (Cool)** ❄️ - Neutral white, no filtering (normal daylight)

## 🎯 Key Features

### Brightness Control
- **Range**: 25-100% display (50-100% actual)
- **Safety**: Minimum 50% prevents screen from being too dark
- **Real-time**: Changes apply immediately
- **Presets**: One-click buttons for common levels

### Color Temperature Control
- **Range**: 1000K (extreme warm) to 6500K (neutral)
- **Ember Mode**: 1000K extreme warm mode like f.lux Ember for maximum blue light reduction
- **Blue Light Filter**: Lower temperatures reduce blue light
- **Eye Comfort**: Reduces eye strain during night use
- **Like f.lux**: Similar to popular blue light reduction apps
- **Real-time**: Color changes apply immediately

### Window Features
- **Resizable**: Can be resized and maximized
- **Modern UI**: Dark gradient background with glowing effects
- **Custom Icon**: Beautiful sun icon with color temperature indicator
- **Responsive**: Smooth slider interactions

## 🔧 Technical Notes

### Display Detection
The app automatically detects your display using:
1. **xrandr** (preferred) - Works with most displays
2. **Backlight interface** (fallback) - Direct hardware control

### Color Temperature Support
- Requires xrandr (X11 display server)
- May not work with backlight-only systems
- App will show a message if not supported

### Permissions
- Backlight control may require video group membership
- Installer sets up permissions automatically
- May need to log out/in after first install

## 🚀 Quick Start

1. **Launch**: Search "LuxTemp" in app menu or run `luxtemp`
2. **Adjust Brightness**: Use slider or preset buttons (25%, 50%, 75%, 100%)
3. **Adjust Temperature**: Use temperature slider or presets (Warm, Sunset, Day, Cool)
4. **Night Mode**: Set to "Warm" (2700K) for comfortable night viewing
5. **Day Mode**: Set to "Cool" (6500K) for normal daylight colors

## 💡 Tips

- **For Night Use**: Lower both brightness and temperature
- **For Reading**: Medium brightness (50-75%) with warm temperature (2700-4000K)
- **For Daytime**: Higher brightness (75-100%) with cool temperature (5500-6500K)
- **For Movies**: Adjust to preference, usually medium brightness with neutral temperature
- **Resize Window**: Drag edges or maximize for better visibility

## 🎨 Color Scheme

- **Background**: Deep blue gradient (#1a1a2e to #16213e)
- **Brightness Accent**: Cyan (#4ecdc4) - represents brightness/light
- **Temperature Accent**: Orange (#ff9a56) - represents warmth
- **Text**: White and light gray for readability
- **Buttons**: Dark purple with hover effects
