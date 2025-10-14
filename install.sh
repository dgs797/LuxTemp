#!/bin/bash

# Brightness Control - Installation Script
# This script installs the brightness control application

set -e

echo "=========================================="
echo "  Brightness Control - Installation"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run this script as root"
    echo "It will ask for sudo password when needed"
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3 first:"
    echo "  sudo apt install python3"
    exit 1
fi

# Check for GTK dependencies
echo "Checking dependencies..."
if ! python3 -c "import gi" 2>/dev/null; then
    echo "Installing required dependencies..."
    sudo apt update
    sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
fi

# Install system tray support (optional but recommended)
echo "Installing system tray support..."
sudo apt install -y gir1.2-appindicator3-0.1 2>/dev/null || echo "Note: System tray support not available"

# Create installation directory
echo "Installing application..."
sudo mkdir -p /opt/brightness-control

# Copy application file
sudo cp lumixan.py /opt/brightness-control/
sudo chmod +x /opt/brightness-control/lumixan.py

# Create launcher script
sudo tee /usr/local/bin/lumixan > /dev/null <<'EOF'
#!/bin/bash
cd /opt/brightness-control
exec python3 lumixan.py "$@"
EOF

sudo chmod +x /usr/local/bin/lumixan

# Create symlink for backward compatibility
sudo ln -sf /usr/local/bin/lumixan /usr/local/bin/brightness-control

# Install icon
echo "Installing application icon..."
if command -v rsvg-convert &> /dev/null; then
    # Convert SVG to PNG if rsvg-convert is available
    rsvg-convert -w 128 -h 128 brightness-control.svg -o /tmp/brightness-control.png
    sudo mkdir -p /usr/share/icons/hicolor/128x128/apps
    sudo cp /tmp/brightness-control.png /usr/share/icons/hicolor/128x128/apps/brightness-control.png
    rm /tmp/brightness-control.png
else
    # Just install the SVG
    sudo mkdir -p /usr/share/icons/hicolor/scalable/apps
    sudo cp brightness-control.svg /usr/share/icons/hicolor/scalable/apps/brightness-control.svg
fi

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor/ 2>/dev/null || true
fi

# Install desktop entry
sudo cp brightness-control.desktop /usr/share/applications/
sudo chmod 644 /usr/share/applications/brightness-control.desktop

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    sudo update-desktop-database /usr/share/applications/
fi

# Setup udev rules for backlight access (if needed)
if [ -d /sys/class/backlight ]; then
    echo "Setting up backlight permissions..."
    sudo tee /etc/udev/rules.d/90-backlight.rules > /dev/null <<'EOF'
# Allow users in video group to change backlight brightness
ACTION=="add", SUBSYSTEM=="backlight", RUN+="/bin/chgrp video $sys$devpath/brightness", RUN+="/bin/chmod g+w $sys$devpath/brightness"
EOF
    
    # Add current user to video group
    sudo usermod -a -G video $USER
    
    # Reload udev rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger --subsystem-match=backlight
    
    echo ""
    echo "Note: You may need to log out and log back in for"
    echo "      backlight permissions to take effect."
fi

echo ""
echo "=========================================="
echo "  Lumixan Installation Complete!"
echo "=========================================="
echo ""
echo "You can now run the application by:"
echo "  1. Searching for 'Lumixan' in your application menu"
echo "  2. Running 'lumixan' in terminal"
echo "  3. Running 'lumixan --tray' for system tray mode"
echo ""
echo "Note: 'brightness-control' command also works (symlink)"
echo ""
echo "If backlight permissions were configured, please log out"
echo "and log back in for the changes to take effect."
echo ""
