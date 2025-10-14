#!/bin/bash

# Lumixan - Uninstallation Script

set -e

echo "=========================================="
echo "  Lumixan - Uninstallation"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run this script as root"
    echo "It will ask for sudo password when needed"
    exit 1
fi

echo "Removing application files..."

# Remove application directory
sudo rm -rf /opt/brightness-control

# Remove launcher scripts
sudo rm -f /usr/local/bin/lumixan
sudo rm -f /usr/local/bin/brightness-control

# Remove desktop entry
sudo rm -f /usr/share/applications/brightness-control.desktop

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    sudo update-desktop-database /usr/share/applications/
fi

# Optionally remove udev rules
read -p "Remove backlight udev rules? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo rm -f /etc/udev/rules.d/90-backlight.rules
    sudo udevadm control --reload-rules
    echo "Udev rules removed"
fi

echo ""
echo "=========================================="
echo "  Uninstallation Complete!"
echo "=========================================="
echo ""
