#!/usr/bin/env python3
"""
Lumixan - A modern brightness and color temperature control tool for Linux
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3
    HAS_APPINDICATOR = True
except (ValueError, ImportError):
    HAS_APPINDICATOR = False
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import subprocess
import os
import re

class BrightnessControl:
    """Handle brightness control operations"""
    
    def __init__(self):
        self.display = None
        self.max_brightness = 100
        self.current_brightness = 100
        self.current_temperature = 6500  # Neutral white
        self.detect_display()
    
    def detect_display(self):
        """Detect the display device"""
        try:
            # Try xrandr first
            result = subprocess.run(['xrandr', '--verbose'], 
                                  capture_output=True, text=True, check=True)
            
            # Find connected displays
            for line in result.stdout.split('\n'):
                if ' connected' in line:
                    match = re.search(r'^(\S+)\s+connected', line)
                    if match:
                        self.display = match.group(1)
                        break
            
            if self.display:
                self.current_brightness = self.get_brightness()
                return True
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Fallback to backlight
        backlight_path = '/sys/class/backlight'
        if os.path.exists(backlight_path):
            backlights = os.listdir(backlight_path)
            if backlights:
                self.display = os.path.join(backlight_path, backlights[0])
                try:
                    with open(os.path.join(self.display, 'max_brightness'), 'r') as f:
                        self.max_brightness = int(f.read().strip())
                    with open(os.path.join(self.display, 'brightness'), 'r') as f:
                        current = int(f.read().strip())
                        self.current_brightness = int((current / self.max_brightness) * 100)
                    return True
                except (IOError, PermissionError):
                    pass
        
        return False
    
    def get_brightness(self):
        """Get current brightness level (0-100)"""
        if not self.display:
            return 100
        
        # Check if using backlight
        if self.display.startswith('/sys/class/backlight'):
            try:
                with open(os.path.join(self.display, 'brightness'), 'r') as f:
                    current = int(f.read().strip())
                    return int((current / self.max_brightness) * 100)
            except (IOError, PermissionError):
                return 100
        
        # Using xrandr
        try:
            result = subprocess.run(['xrandr', '--verbose'], 
                                  capture_output=True, text=True, check=True)
            
            in_display = False
            for line in result.stdout.split('\n'):
                if self.display in line and ' connected' in line:
                    in_display = True
                elif in_display and 'Brightness:' in line:
                    match = re.search(r'Brightness:\s+([\d.]+)', line)
                    if match:
                        brightness = float(match.group(1))
                        return int(brightness * 100)
                    break
                elif in_display and line and not line.startswith('\t'):
                    break
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return 100
    
    def set_brightness(self, value):
        """Set brightness level (50-100)"""
        if not self.display:
            return False
        
        value = max(50, min(100, value))  # Clamp between 50-100
        
        # Check if using backlight
        if self.display.startswith('/sys/class/backlight'):
            try:
                brightness_value = int((value / 100) * self.max_brightness)
                brightness_file = os.path.join(self.display, 'brightness')
                
                # Try direct write first
                try:
                    with open(brightness_file, 'w') as f:
                        f.write(str(brightness_value))
                    self.current_brightness = value
                    return True
                except PermissionError:
                    # Try with pkexec
                    subprocess.run(['pkexec', 'tee', brightness_file], 
                                 input=str(brightness_value).encode(), 
                                 check=True, capture_output=True)
                    self.current_brightness = value
                    return True
            except (IOError, subprocess.CalledProcessError):
                return False
        
        # Using xrandr
        try:
            brightness_value = value / 100
            subprocess.run(['xrandr', '--output', self.display, 
                          '--brightness', str(brightness_value)], 
                         check=True, capture_output=True)
            self.current_brightness = value
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def set_color_temperature(self, temp):
        """Set color temperature in Kelvin (1000-6500)"""
        if not self.display or self.display.startswith('/sys/class/backlight'):
            # Color temp only works with xrandr
            if not self.display:
                return False
            return False
        
        temp = max(1000, min(6500, temp))  # Clamp between 1000-6500K
        
        # Convert temperature to RGB gamma values
        # Warmer = more red, less blue
        # 6500K = neutral (1.0, 1.0, 1.0)
        # Lower K = warmer (more red/yellow)
        
        if temp >= 6500:
            red = 1.0
            green = 1.0
            blue = 1.0
        else:
            # Simplified color temperature to RGB conversion
            factor = temp / 6500.0
            red = 1.0
            green = 0.7 + (0.3 * factor)  # Reduce green slightly for warmth
            blue = factor  # Reduce blue for warmth
        
        try:
            subprocess.run(['xrandr', '--output', self.display,
                          '--gamma', f'{red}:{green}:{blue}'],
                         check=True, capture_output=True)
            self.current_temperature = temp
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


class BrightnessApp(Gtk.Window):
    """Main application window"""
    
    def __init__(self, start_hidden=False):
        super().__init__(title="Lumixan")
        
        self.brightness_ctrl = BrightnessControl()
        self.update_timeout = None
        self.temp_update_timeout = None
        self.indicator = None
        
        # Window properties - compact size for small screens
        self.set_default_size(420, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(True)
        
        # Set minimum size to ensure usability
        self.set_size_request(380, 420)
        
        # Set window icon
        try:
            # Try custom icon first
            icon_theme = Gtk.IconTheme.get_default()
            if icon_theme.has_icon('brightness-control'):
                icon = icon_theme.load_icon('brightness-control', 48, 0)
                self.set_icon(icon)
            else:
                # Try loading from local file
                script_dir = os.path.dirname(os.path.abspath(__file__))
                icon_path = os.path.join(script_dir, 'brightness-control.svg')
                if os.path.exists(icon_path):
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 48, 48)
                    self.set_icon(pixbuf)
                else:
                    # Fallback to system icon
                    icon = icon_theme.load_icon('display-brightness', 48, 0)
                    self.set_icon(icon)
        except Exception as e:
            pass  # Icon is optional
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Build UI
        self.build_ui()
        
        # Update initial value
        self.update_brightness_display()
        
        # Setup system tray indicator
        self.setup_indicator()
        
        # Handle window close to minimize to tray
        self.connect('delete-event', self.on_window_delete)
        
        # Start hidden if requested
        if start_hidden:
            self.hide()
    
    def apply_dark_theme(self):
        """Apply modern dark theme styling"""
        css_provider = Gtk.CssProvider()
        css = b"""
        window {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }
        
        .main-container {
            background: rgba(26, 26, 46, 0.95);
            border-radius: 16px;
            padding: 20px;
            margin: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        
        .title-label {
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 6px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .subtitle-label {
            color: #a0a0c0;
            font-size: 12px;
            margin-bottom: 16px;
        }
        
        .brightness-value {
            color: #4ecdc4;
            font-size: 42px;
            font-weight: bold;
            margin: 12px 0;
            text-shadow: 0 0 20px rgba(78, 205, 196, 0.5);
        }
        
        .percentage-label {
            color: #4ecdc4;
            font-size: 20px;
            font-weight: 500;
        }
        
        scale {
            margin: 12px 0;
            min-height: 32px;
        }
        
        scale trough {
            min-height: 8px;
            border-radius: 4px;
            background: linear-gradient(90deg, #2d3561 0%, #3d4574 100%);
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        scale highlight {
            border-radius: 6px;
            background: linear-gradient(90deg, #4ecdc4 0%, #44a8a0 100%);
            box-shadow: 0 0 12px rgba(78, 205, 196, 0.4);
        }
        
        scale slider {
            min-height: 22px;
            min-width: 22px;
            border-radius: 11px;
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
            border: 2px solid #4ecdc4;
        }
        
        scale slider:hover {
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
            box-shadow: 0 6px 16px rgba(78, 205, 196, 0.5);
        }
        
        .button-box {
            margin-top: 12px;
        }
        
        button {
            min-height: 38px;
            padding: 0 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .preset-button {
            background: linear-gradient(135deg, #3d4574 0%, #2d3561 100%);
            color: #ffffff;
            border: 2px solid #4a5280;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        
        .preset-button:hover {
            background: linear-gradient(135deg, #4a5280 0%, #3d4574 100%);
            border-color: #4ecdc4;
            box-shadow: 0 6px 12px rgba(78, 205, 196, 0.3);
        }
        
        .preset-button:active {
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .info-label {
            color: #7a7a9a;
            font-size: 10px;
            margin-top: 10px;
        }
        
        .icon-image {
            margin-bottom: 10px;
        }
        
        .section-divider {
            margin: 16px 0;
            border-top: 1px solid rgba(78, 205, 196, 0.2);
        }
        
        .section-title {
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            margin: 10px 0 6px 0;
        }
        
        .temp-value {
            color: #ff9a56;
            font-size: 28px;
            font-weight: bold;
            margin: 8px 0;
        }
        
        .temp-label {
            color: #ff9a56;
            font-size: 14px;
        }
        """
        
        css_provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def build_ui(self):
        """Build the user interface"""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.get_style_context().add_class('main-container')
        
        # Icon - Load from SVG file
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, 'brightness-control.svg')
            if os.path.exists(icon_path):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 48, 48)
                icon_image = Gtk.Image.new_from_pixbuf(pixbuf)
                icon_image.get_style_context().add_class('icon-image')
                main_box.pack_start(icon_image, False, False, 0)
            else:
                # Fallback to emoji
                icon_label = Gtk.Label(label="☀")
                icon_label.set_markup('<span font="36">☀</span>')
                main_box.pack_start(icon_label, False, False, 0)
        except Exception as e:
            # Fallback to emoji if image loading fails
            icon_label = Gtk.Label(label="☀")
            icon_label.set_markup('<span font="36">☀</span>')
            main_box.pack_start(icon_label, False, False, 0)
        
        # Title
        title = Gtk.Label(label="Lumixan")
        title.get_style_context().add_class('title-label')
        main_box.pack_start(title, False, False, 0)
        
        # Subtitle
        if self.brightness_ctrl.display:
            if self.brightness_ctrl.display.startswith('/sys/class/backlight'):
                display_name = os.path.basename(self.brightness_ctrl.display)
            else:
                display_name = self.brightness_ctrl.display
            subtitle = Gtk.Label(label=f"Display: {display_name}")
        else:
            subtitle = Gtk.Label(label="No display detected")
        subtitle.get_style_context().add_class('subtitle-label')
        main_box.pack_start(subtitle, False, False, 0)
        
        # Brightness value display (show as 25-100 but actual is 50-100)
        value_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        value_box.set_halign(Gtk.Align.CENTER)
        
        self.brightness_label = Gtk.Label(label="100")
        self.brightness_label.get_style_context().add_class('brightness-value')
        value_box.pack_start(self.brightness_label, False, False, 0)
        
        percent_label = Gtk.Label(label="%")
        percent_label.get_style_context().add_class('percentage-label')
        value_box.pack_start(percent_label, False, False, 0)
        
        main_box.pack_start(value_box, False, False, 0)
        
        # Brightness slider container (constrain width)
        brightness_slider_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        brightness_slider_box.set_halign(Gtk.Align.CENTER)
        
        # Brightness slider (actual: 50-100, display: 25-100)
        self.brightness_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 50, 100, 1
        )
        self.brightness_scale.set_size_request(400, -1)  # Max width 400px
        self.brightness_scale.set_hexpand(False)
        # Ensure initial value is at least 50
        initial_value = max(50, self.brightness_ctrl.current_brightness)
        self.brightness_scale.set_value(initial_value)
        self.brightness_scale.set_draw_value(False)
        self.brightness_scale.connect('value-changed', self.on_brightness_changed)
        
        brightness_slider_box.pack_start(self.brightness_scale, False, False, 0)
        main_box.pack_start(brightness_slider_box, False, False, 0)
        
        # Preset buttons (display 25, 50, 75, 100 but map to 50, 62.5, 75, 100)
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.get_style_context().add_class('button-box')
        
        presets = [
            ("25%", 50),   # Display 25%, actual 50%
            ("50%", 67),   # Display 50%, actual 67%
            ("75%", 83),   # Display 75%, actual 83%
            ("100%", 100)  # Display 100%, actual 100%
        ]
        
        for label, value in presets:
            button = Gtk.Button(label=label)
            button.get_style_context().add_class('preset-button')
            button.connect('clicked', self.on_preset_clicked, value)
            button_box.pack_start(button, True, True, 0)
        
        main_box.pack_start(button_box, False, False, 0)
        
        # Info label
        info = Gtk.Label(label="Brightness display: 25% - 100% (actual minimum: 50% for safety)")
        info.get_style_context().add_class('info-label')
        main_box.pack_start(info, False, False, 0)
        
        # Section divider
        divider = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        divider.get_style_context().add_class('section-divider')
        main_box.pack_start(divider, False, False, 0)
        
        # Color Temperature Section
        temp_title = Gtk.Label(label="🌡 Color Temperature")
        temp_title.get_style_context().add_class('section-title')
        main_box.pack_start(temp_title, False, False, 0)
        
        # Check if color temperature is supported
        self.temp_supported = (self.brightness_ctrl.display and 
                              not self.brightness_ctrl.display.startswith('/sys/class/backlight'))
        
        if self.temp_supported:
            # Temperature value display
            temp_value_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            temp_value_box.set_halign(Gtk.Align.CENTER)
            
            self.temp_label = Gtk.Label(label="6500")
            self.temp_label.get_style_context().add_class('temp-value')
            temp_value_box.pack_start(self.temp_label, False, False, 0)
            
            temp_unit = Gtk.Label(label="K")
            temp_unit.get_style_context().add_class('temp-label')
            temp_value_box.pack_start(temp_unit, False, False, 0)
            
            main_box.pack_start(temp_value_box, False, False, 0)
            
            # Temperature slider container (constrain width)
            temp_slider_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            temp_slider_box.set_halign(Gtk.Align.CENTER)
            
            # Temperature slider (1000K = warm/red, 6500K = neutral/white)
            self.temp_scale = Gtk.Scale.new_with_range(
                Gtk.Orientation.HORIZONTAL, 2000, 6500, 100
            )
            self.temp_scale.set_size_request(400, -1)  # Max width 400px
            self.temp_scale.set_hexpand(False)
            self.temp_scale.set_value(6500)
            self.temp_scale.set_draw_value(False)
            self.temp_scale.connect('value-changed', self.on_temp_changed)
            
            temp_slider_box.pack_start(self.temp_scale, False, False, 0)
            main_box.pack_start(temp_slider_box, False, False, 0)
            
            # Temperature preset buttons
            temp_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            temp_button_box.set_halign(Gtk.Align.CENTER)
            temp_button_box.get_style_context().add_class('button-box')
            
            temp_presets = [
                ("🔥 Warm", 2700),
                ("🌅 Sunset", 4000),
                ("☀️ Day", 5500),
                ("❄️ Cool", 6500)
            ]
            
            for label, value in temp_presets:
                button = Gtk.Button(label=label)
                button.get_style_context().add_class('preset-button')
                button.connect('clicked', self.on_temp_preset_clicked, value)
                temp_button_box.pack_start(button, True, True, 0)
            
            main_box.pack_start(temp_button_box, False, False, 0)
            
            # Temperature info
            temp_info = Gtk.Label(label="Lower temperature = warmer/less blue light (better for night)")
            temp_info.get_style_context().add_class('info-label')
            main_box.pack_start(temp_info, False, False, 0)
        else:
            # Not supported message
            not_supported = Gtk.Label(label="Color temperature control requires xrandr")
            not_supported.get_style_context().add_class('info-label')
            main_box.pack_start(not_supported, False, False, 0)
        
        # Add to window directly (no scrolling)
        overlay = Gtk.Overlay()
        overlay.add(main_box)
        self.add(overlay)
    
    def setup_indicator(self):
        """Setup system tray indicator"""
        if not HAS_APPINDICATOR:
            return
        
        # Get icon path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'brightness-control.svg')
        
        # Create indicator
        self.indicator = AppIndicator3.Indicator.new(
            "brightness-control",
            "brightness-control" if os.path.exists('/usr/share/icons/hicolor/scalable/apps/brightness-control.svg') else icon_path,
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_title("Lumixan")
        
        # Create menu
        menu = Gtk.Menu()
        
        # Show/Hide window item
        show_item = Gtk.MenuItem(label="Show/Hide Window")
        show_item.connect('activate', self.toggle_window)
        menu.append(show_item)
        
        # Separator
        menu.append(Gtk.SeparatorMenuItem())
        
        # Quick brightness presets
        brightness_menu = Gtk.MenuItem(label="Brightness")
        brightness_submenu = Gtk.Menu()
        
        for label, value in [("25%", 50), ("50%", 67), ("75%", 83), ("100%", 100)]:
            item = Gtk.MenuItem(label=label)
            item.connect('activate', lambda w, v=value: self.set_brightness_from_menu(v))
            brightness_submenu.append(item)
        
        brightness_menu.set_submenu(brightness_submenu)
        menu.append(brightness_menu)
        
        # Quick temperature presets (if supported)
        if self.brightness_ctrl.display and not self.brightness_ctrl.display.startswith('/sys/class/backlight'):
            temp_menu = Gtk.MenuItem(label="Color Temperature")
            temp_submenu = Gtk.Menu()
            
            for label, value in [("Warm (2700K)", 2700), ("Sunset (4000K)", 4000), 
                                ("Day (5500K)", 5500), ("Cool (6500K)", 6500)]:
                item = Gtk.MenuItem(label=label)
                item.connect('activate', lambda w, v=value: self.set_temp_from_menu(v))
                temp_submenu.append(item)
            
            temp_menu.set_submenu(temp_submenu)
            menu.append(temp_menu)
        
        # Separator
        menu.append(Gtk.SeparatorMenuItem())
        
        # Quit item
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect('activate', self.quit_app)
        menu.append(quit_item)
        
        menu.show_all()
        self.indicator.set_menu(menu)
    
    def toggle_window(self, widget=None):
        """Toggle window visibility"""
        if self.get_visible():
            self.hide()
        else:
            self.show_all()
            self.present()
    
    def on_window_delete(self, widget, event):
        """Handle window close - minimize to tray instead of quit"""
        if HAS_APPINDICATOR and self.indicator:
            self.hide()
            return True  # Prevent window from closing
        return False  # Allow window to close if no tray
    
    def set_brightness_from_menu(self, value):
        """Set brightness from tray menu"""
        self.brightness_ctrl.set_brightness(value)
        if hasattr(self, 'brightness_scale'):
            self.brightness_scale.set_value(value)
        self.update_brightness_display()
    
    def set_temp_from_menu(self, value):
        """Set temperature from tray menu"""
        self.brightness_ctrl.set_color_temperature(value)
        if hasattr(self, 'temp_scale'):
            self.temp_scale.set_value(value)
        if hasattr(self, 'update_temp_display'):
            self.update_temp_display()
    
    def quit_app(self, widget=None):
        """Quit the application"""
        Gtk.main_quit()
    
    def on_brightness_changed(self, scale):
        """Handle brightness slider changes"""
        value = int(scale.get_value())
        
        # Cancel any pending update
        if self.update_timeout:
            GLib.source_remove(self.update_timeout)
        
        # Schedule update with small delay to avoid too many calls
        self.update_timeout = GLib.timeout_add(100, self.apply_brightness, value)
    
    def apply_brightness(self, value):
        """Apply brightness change"""
        self.brightness_ctrl.set_brightness(value)
        self.update_brightness_display()
        self.update_timeout = None
        return False  # Don't repeat
    
    def on_preset_clicked(self, button, value):
        """Handle preset button clicks"""
        self.brightness_scale.set_value(value)
    
    def update_brightness_display(self):
        """Update the brightness value display (map 50-100 to 25-100)"""
        actual = int(self.brightness_ctrl.current_brightness)
        # Map 50-100 actual to 25-100 display
        display = int(((actual - 50) / 50) * 75 + 25)
        self.brightness_label.set_text(str(display))
    
    def on_temp_changed(self, scale):
        """Handle temperature slider changes"""
        if not self.temp_supported:
            return
        
        value = int(scale.get_value())
        
        # Cancel any pending update
        if self.temp_update_timeout:
            GLib.source_remove(self.temp_update_timeout)
        
        # Schedule update with small delay
        self.temp_update_timeout = GLib.timeout_add(100, self.apply_temperature, value)
    
    def apply_temperature(self, value):
        """Apply temperature change"""
        self.brightness_ctrl.set_color_temperature(value)
        self.update_temp_display()
        self.temp_update_timeout = None
        return False  # Don't repeat
    
    def on_temp_preset_clicked(self, button, value):
        """Handle temperature preset button clicks"""
        if self.temp_supported:
            self.temp_scale.set_value(value)
    
    def update_temp_display(self):
        """Update the temperature value display"""
        if self.temp_supported:
            current = int(self.brightness_ctrl.current_temperature)
            self.temp_label.set_text(str(current))


def main():
    """Main entry point"""
    import sys
    
    # Check for --tray argument
    start_hidden = '--tray' in sys.argv or '--hidden' in sys.argv
    
    app = BrightnessApp(start_hidden=start_hidden)
    app.connect('destroy', Gtk.main_quit)
    
    if not start_hidden:
        app.show_all()
    
    Gtk.main()


if __name__ == '__main__':
    main()
