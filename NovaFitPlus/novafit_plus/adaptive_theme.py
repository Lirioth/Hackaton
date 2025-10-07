"""
Adaptive Theme System for NovaFit Plus
=====================================
Intelligent theme management that adapts to time of day, user preferences,
and system settings for optimal user experience.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any
import datetime as dt
import json
import platform
import subprocess

class ThemeMode:
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    SYSTEM = "system"

class AdaptiveThemeManager:
    """
    Advanced theme manager with automatic switching based on:
    - Time of day
    - System theme (Windows/macOS/Linux)
    - User preferences
    - Custom schedules
    """
    
    def __init__(self, apply_theme_callback: Callable[[str], None]):
        self.apply_theme_callback = apply_theme_callback
        self.config_file = "theme_config.json"
        
        # Default configuration
        self.config = {
            'mode': ThemeMode.AUTO,
            'auto_schedule': {
                'light_start': '06:00',  # 6 AM
                'dark_start': '18:00',   # 6 PM
            },
            'follow_system': True,
            'manual_override': False,
            'last_manual_theme': ThemeMode.LIGHT,
            'transition_enabled': True,
            'transition_duration': 2000,  # ms
        }
        
        self.current_theme = ThemeMode.LIGHT
        self.auto_check_job = None
        self.load_config()
        
    def load_config(self):
        """Load theme configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                saved_config = json.load(f)
                self.config.update(saved_config)
        except (FileNotFoundError, json.JSONDecodeError):
            # Use defaults
            pass
    
    def save_config(self):
        """Save theme configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save theme config: {e}")
    
    def get_system_theme(self) -> Optional[str]:
        """Detect system theme preference"""
        system = platform.system().lower()
        
        try:
            if system == "windows":
                # Check Windows registry for dark mode
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                )
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return ThemeMode.LIGHT if value == 1 else ThemeMode.DARK
                
            elif system == "darwin":  # macOS
                # Use AppleScript to check macOS dark mode
                script = 'tell application "System Events" to tell appearance preferences to get dark mode'
                result = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return ThemeMode.DARK if result.stdout.strip() == "true" else ThemeMode.LIGHT
                    
            elif system == "linux":
                # Check GTK theme or environment variables
                import os
                gtk_theme = os.environ.get('GTK_THEME', '')
                if 'dark' in gtk_theme.lower():
                    return ThemeMode.DARK
                elif 'light' in gtk_theme.lower():
                    return ThemeMode.LIGHT
                    
        except Exception:
            # Fallback to time-based detection
            pass
        
        return None
    
    def get_time_based_theme(self) -> str:
        """Get theme based on current time"""
        now = dt.datetime.now().time()
        
        light_start = dt.time.fromisoformat(self.config['auto_schedule']['light_start'])
        dark_start = dt.time.fromisoformat(self.config['auto_schedule']['dark_start'])
        
        if light_start <= now < dark_start:
            return ThemeMode.LIGHT
        else:
            return ThemeMode.DARK
    
    def determine_theme(self) -> str:
        """Determine which theme should be active"""
        # Manual override takes precedence
        if self.config['manual_override']:
            return self.config['last_manual_theme']
        
        mode = self.config['mode']
        
        if mode == ThemeMode.SYSTEM:
            system_theme = self.get_system_theme()
            if system_theme:
                return system_theme
            # Fallback to auto if system detection fails
            mode = ThemeMode.AUTO
        
        if mode == ThemeMode.AUTO:
            return self.get_time_based_theme()
        
        # Explicit light or dark
        return mode
    
    def apply_theme(self, theme: Optional[str] = None, manual: bool = False):
        """Apply theme with optional manual override"""
        if theme is None:
            theme = self.determine_theme()
        
        if manual:
            self.config['manual_override'] = True
            self.config['last_manual_theme'] = theme
            self.save_config()
        
        if theme != self.current_theme:
            self.current_theme = theme
            
            if self.config['transition_enabled']:
                self.apply_with_transition(theme)
            else:
                self.apply_theme_callback(theme)
    
    def apply_with_transition(self, theme: str):
        """Apply theme with smooth transition effect"""
        # For now, just apply directly
        # In a more advanced implementation, you could fade between themes
        self.apply_theme_callback(theme)
    
    def start_auto_checking(self, root: tk.Tk, interval: int = 60000):
        """Start automatic theme checking (every minute by default)"""
        def check_theme():
            if not self.config['manual_override']:
                new_theme = self.determine_theme()
                if new_theme != self.current_theme:
                    self.apply_theme(new_theme)
            
            # Schedule next check
            self.auto_check_job = root.after(interval, check_theme)
        
        # Initial check
        check_theme()
    
    def stop_auto_checking(self, root: tk.Tk):
        """Stop automatic theme checking"""
        if self.auto_check_job:
            root.after_cancel(self.auto_check_job)
            self.auto_check_job = None
    
    def set_mode(self, mode: str):
        """Set theme mode"""
        self.config['mode'] = mode
        self.config['manual_override'] = False
        self.save_config()
        self.apply_theme()
    
    def toggle_theme(self):
        """Toggle between light and dark themes manually"""
        current = self.current_theme
        new_theme = ThemeMode.DARK if current == ThemeMode.LIGHT else ThemeMode.LIGHT
        self.apply_theme(new_theme, manual=True)
    
    def reset_manual_override(self):
        """Reset manual override and return to automatic mode"""
        self.config['manual_override'] = False
        self.save_config()
        self.apply_theme()
    
    def set_schedule(self, light_start: str, dark_start: str):
        """Set custom light/dark schedule (HH:MM format)"""
        try:
            # Validate time format
            dt.time.fromisoformat(light_start)
            dt.time.fromisoformat(dark_start)
            
            self.config['auto_schedule']['light_start'] = light_start
            self.config['auto_schedule']['dark_start'] = dark_start
            self.save_config()
            
            # Apply new schedule if in auto mode
            if self.config['mode'] == ThemeMode.AUTO and not self.config['manual_override']:
                self.apply_theme()
                
        except ValueError:
            raise ValueError("Invalid time format. Use HH:MM format (e.g., '06:00')")

class ThemeControlWidget:
    """Widget for theme controls and settings"""
    
    def __init__(self, parent, theme_manager: AdaptiveThemeManager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.setup_widget()
    
    def setup_widget(self):
        """Setup theme control widget"""
        # Main frame
        self.frame = ttk.LabelFrame(
            self.parent,
            text="🎨 Theme Settings",
            padding=10
        )
        self.frame.pack(fill="x", pady=10)
        
        # Current theme display
        current_frame = ttk.Frame(self.frame)
        current_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(
            current_frame,
            text="Current Theme:",
            style='PanelBody.TLabel'
        ).pack(side="left")
        
        self.current_theme_label = ttk.Label(
            current_frame,
            text=self.theme_manager.current_theme.title(),
            font=("TkDefaultFont", 10, "bold"),
            style='ThemeValue.TLabel'
        )
        self.current_theme_label.pack(side="left", padx=(10, 0))
        
        # Theme mode selection
        mode_frame = ttk.LabelFrame(self.frame, text="Theme Mode", padding=5)
        mode_frame.pack(fill="x", pady=(0, 10))
        
        self.mode_var = tk.StringVar(value=self.theme_manager.config['mode'])
        
        modes = [
            (ThemeMode.AUTO, "🕐 Auto (Time-based)"),
            (ThemeMode.SYSTEM, "💻 Follow System"),
            (ThemeMode.LIGHT, "☀️ Always Light"),
            (ThemeMode.DARK, "🌙 Always Dark")
        ]
        
        for i, (value, text) in enumerate(modes):
            ttk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.mode_var,
                value=value,
                command=self.on_mode_change
            ).grid(row=i//2, column=i%2, sticky="w", padx=5, pady=2)
        
        # Schedule settings (only shown when auto mode is selected)
        self.schedule_frame = ttk.LabelFrame(self.frame, text="Auto Schedule", padding=5)
        
        ttk.Label(self.schedule_frame, text="Light theme starts:").grid(row=0, column=0, sticky="w", pady=2)
        self.light_start_var = tk.StringVar(value=self.theme_manager.config['auto_schedule']['light_start'])
        light_entry = ttk.Entry(self.schedule_frame, textvariable=self.light_start_var, width=8)
        light_entry.grid(row=0, column=1, padx=(5, 0), pady=2)
        
        ttk.Label(self.schedule_frame, text="Dark theme starts:").grid(row=1, column=0, sticky="w", pady=2)
        self.dark_start_var = tk.StringVar(value=self.theme_manager.config['auto_schedule']['dark_start'])
        dark_entry = ttk.Entry(self.schedule_frame, textvariable=self.dark_start_var, width=8)
        dark_entry.grid(row=1, column=1, padx=(5, 0), pady=2)
        
        ttk.Button(
            self.schedule_frame,
            text="Apply Schedule",
            command=self.apply_schedule,
            style='Compact.TButton'
        ).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Control buttons
        controls_frame = ttk.Frame(self.frame)
        controls_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(
            controls_frame,
            text="Toggle Theme",
            command=self.toggle_theme,
            style='Accent.TButton'
        ).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            controls_frame,
            text="Reset Override",
            command=self.reset_override
        ).pack(side="left", padx=5)
        
        # Override indicator
        self.override_label = ttk.Label(
            controls_frame,
            text="",
            style='Override.TLabel'
        )
        self.override_label.pack(side="right")
        
        self.update_display()
    
    def on_mode_change(self):
        """Handle theme mode change"""
        new_mode = self.mode_var.get()
        self.theme_manager.set_mode(new_mode)
        self.update_display()
    
    def apply_schedule(self):
        """Apply custom schedule"""
        try:
            light_start = self.light_start_var.get()
            dark_start = self.dark_start_var.get()
            self.theme_manager.set_schedule(light_start, dark_start)
            self.update_display()
        except ValueError as e:
            tk.messagebox.showerror("Invalid Schedule", str(e))
    
    def toggle_theme(self):
        """Toggle theme manually"""
        self.theme_manager.toggle_theme()
        self.update_display()
    
    def reset_override(self):
        """Reset manual override"""
        self.theme_manager.reset_manual_override()
        self.mode_var.set(self.theme_manager.config['mode'])
        self.update_display()
    
    def update_display(self):
        """Update the display with current settings"""
        # Update current theme
        theme_icon = "🌙" if self.theme_manager.current_theme == ThemeMode.DARK else "☀️"
        self.current_theme_label.config(
            text=f"{theme_icon} {self.theme_manager.current_theme.title()}"
        )
        
        # Show/hide schedule frame
        if self.mode_var.get() == ThemeMode.AUTO:
            self.schedule_frame.pack(fill="x", pady=(0, 10))
        else:
            self.schedule_frame.pack_forget()
        
        # Show override status
        if self.theme_manager.config['manual_override']:
            self.override_label.config(text="🔒 Manual Override Active")
        else:
            self.override_label.config(text="")

def setup_adaptive_theme_styles(style: ttk.Style):
    """Setup styles for adaptive theme widgets"""
    style.configure(
        'ThemeValue.TLabel',
        background='#ffffff',
        foreground='#3b82f6'
    )
    
    style.configure(
        'Override.TLabel',
        background='#ffffff',
        foreground='#ef4444',
        font=('TkDefaultFont', 9)
    )
    
    style.configure(
        'Compact.TButton',
        padding=(5, 2)
    )