"""
UI Enhancements for NovaFit Plus GUI
====================================

This module contains enhanced UI components and utilities to improve
user experience, accessibility, and visual feedback.

Advanced Features:
- Auto-refresh system with smart intervals
- Enhanced metric cards with trend visualization  
- Interactive charts and data visualization
- Smart notifications based on data patterns
- Customizable dashboard components
"""

import tkinter as tk
from tkinter import ttk
import datetime as _dt
from typing import Optional, Callable, Dict, Any, List, Tuple
import threading
import time
import math


class ToolTip:
    """
    Enhanced tooltip system for providing contextual help.
    
    Usage:
        ToolTip(widget, "This is a helpful tooltip message")
    """
    
    def __init__(self, widget: tk.Widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self.timer = None
        
        # Bind events
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)
    
    def on_enter(self, event=None):
        """Start timer for showing tooltip"""
        self.timer = self.widget.after(self.delay, self.show_tooltip)
    
    def on_leave(self, event=None):
        """Hide tooltip and cancel timer"""
        if self.timer:
            self.widget.after_cancel(self.timer)
            self.timer = None
        self.hide_tooltip()
    
    def show_tooltip(self):
        """Display the tooltip"""
        if self.tooltip:
            return
            
        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Style the tooltip
        frame = tk.Frame(
            self.tooltip,
            background="#fffbf0",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=4
        )
        frame.pack()
        
        label = tk.Label(
            frame,
            text=self.text,
            background="#fffbf0",
            foreground="#333333",
            font=("TkDefaultFont", 9),
            wraplength=300,
            justify="left"
        )
        label.pack()
    
    def hide_tooltip(self):
        """Hide the tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class NotificationToast:
    """
    Non-intrusive notification system for user feedback.
    
    Usage:
        NotificationToast(parent, "Operation completed successfully!", "success")
    """
    
    def __init__(self, parent: tk.Widget, message: str, toast_type: str = "info", duration: int = 3000):
        self.parent = parent
        self.duration = duration
        self.toast = None
        
        # Color schemes for different notification types
        self.colors = {
            "info": {"bg": "#e3f2fd", "fg": "#1976d2", "border": "#2196f3"},
            "success": {"bg": "#e8f5e8", "fg": "#2e7d32", "border": "#4caf50"},
            "warning": {"bg": "#fff3e0", "fg": "#f57c00", "border": "#ff9800"},
            "error": {"bg": "#ffebee", "fg": "#d32f2f", "border": "#f44336"}
        }
        
        self.create_toast(message, toast_type)
    
    def create_toast(self, message: str, toast_type: str):
        """Create and display the toast notification"""
        # Get color scheme
        colors = self.colors.get(toast_type, self.colors["info"])
        
        # Create toplevel window
        self.toast = tk.Toplevel(self.parent)
        self.toast.wm_overrideredirect(True)
        
        # Position in top-right corner
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        
        toast_width = 320
        toast_height = 80
        
        x = parent_x + parent_width - toast_width - 20
        y = parent_y + 60
        
        self.toast.wm_geometry(f"{toast_width}x{toast_height}+{x}+{y}")
        
        # Create main frame
        main_frame = tk.Frame(
            self.toast,
            bg=colors["bg"],
            relief="raised",
            bd=1,
            highlightbackground=colors["border"],
            highlightthickness=2
        )
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Add icon based on type
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        icon_frame = tk.Frame(main_frame, bg=colors["bg"])
        icon_frame.pack(side="left", padx=(10, 5), pady=10)
        
        tk.Label(
            icon_frame,
            text=icons.get(toast_type, "ℹ️"),
            bg=colors["bg"],
            font=("TkDefaultFont", 14)
        ).pack()
        
        # Add message
        message_frame = tk.Frame(main_frame, bg=colors["bg"])
        message_frame.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)
        
        tk.Label(
            message_frame,
            text=message,
            bg=colors["bg"],
            fg=colors["fg"],
            font=("TkDefaultFont", 9),
            wraplength=220,
            justify="left"
        ).pack(anchor="w")
        
        # Add close button
        close_frame = tk.Frame(main_frame, bg=colors["bg"])
        close_frame.pack(side="right", padx=(0, 8), pady=8)
        
        close_btn = tk.Button(
            close_frame,
            text="×",
            bg=colors["bg"],
            fg=colors["fg"],
            font=("TkDefaultFont", 12, "bold"),
            relief="flat",
            bd=0,
            command=self.destroy,
            cursor="hand2"
        )
        close_btn.pack()
        
        # Hover effects for close button
        def on_enter(e):
            close_btn.config(bg=colors["border"])
        def on_leave(e):
            close_btn.config(bg=colors["bg"])
            
        close_btn.bind("<Enter>", on_enter)
        close_btn.bind("<Leave>", on_leave)
        
        # Auto-destroy after duration
        self.toast.after(self.duration, self.destroy)
        
        # Bring to front
        self.toast.lift()
        self.toast.attributes('-topmost', True)
    
    def destroy(self):
        """Destroy the toast notification"""
        if self.toast:
            self.toast.destroy()
            self.toast = None


class SmartEntry(ttk.Frame):
    """
    Enhanced entry widget with real-time validation and helpful feedback.
    
    Usage:
        entry = SmartEntry(parent, "Weight (kg)", value_type="number", min_value=0, max_value=500)
    """
    
    def __init__(self, parent, label: str, value_type: str = "text", **kwargs):
        super().__init__(parent, style='Panel.TFrame')
        
        self.value_type = value_type
        self.min_value = kwargs.pop('min_value', None)
        self.max_value = kwargs.pop('max_value', None)
        self.required = kwargs.pop('required', False)
        self.tooltip_text = kwargs.pop('tooltip', None)
        
        self.error_var = tk.StringVar()
        self.value_var = tk.StringVar()
        
        self.setup_ui(label, **kwargs)
        self.setup_validation()
    
    def setup_ui(self, label: str, **kwargs):
        """Setup the UI components"""
        # Label with required indicator
        label_frame = ttk.Frame(self, style='Panel.TFrame')
        label_frame.pack(fill="x", pady=(0, 2))
        
        label_text = f"{label} *" if self.required else label
        self.label = ttk.Label(label_frame, text=label_text, style='PanelBody.TLabel')
        self.label.pack(side="left")
        
        # Add tooltip if provided
        if self.tooltip_text:
            ToolTip(self.label, self.tooltip_text)
        
        # Entry widget
        self.entry = ttk.Entry(self, textvariable=self.value_var, **kwargs)
        self.entry.pack(fill="x", pady=(0, 2))
        
        # Error message label
        self.error_label = ttk.Label(
            self,
            textvariable=self.error_var,
            foreground="red",
            font=("TkDefaultFont", 8),
            style='Panel.TLabel'
        )
        self.error_label.pack(fill="x")
    
    def setup_validation(self):
        """Setup real-time validation"""
        self.entry.bind('<KeyRelease>', self.validate)
        self.entry.bind('<FocusOut>', self.validate)
    
    def validate(self, event=None) -> bool:
        """Validate the current value"""
        value = self.value_var.get().strip()
        
        # Check if required and empty
        if self.required and not value:
            self.set_error("This field is required")
            return False
        
        # Skip validation if empty and not required
        if not value:
            self.clear_error()
            return True
        
        # Type-specific validation
        if self.value_type == "number":
            return self.validate_number(value)
        elif self.value_type == "date":
            return self.validate_date(value)
        elif self.value_type == "email":
            return self.validate_email(value)
        
        self.clear_error()
        return True
    
    def validate_number(self, value: str) -> bool:
        """Validate numeric input"""
        try:
            num = float(value)
            
            if self.min_value is not None and num < self.min_value:
                self.set_error(f"Value must be at least {self.min_value}")
                return False
                
            if self.max_value is not None and num > self.max_value:
                self.set_error(f"Value must be at most {self.max_value}")
                return False
                
            self.clear_error()
            return True
            
        except ValueError:
            self.set_error("Please enter a valid number")
            return False
    
    def validate_date(self, value: str) -> bool:
        """Validate date input"""
        try:
            _dt.date.fromisoformat(value)
            self.clear_error()
            return True
        except ValueError:
            self.set_error("Please use YYYY-MM-DD format")
            return False
    
    def validate_email(self, value: str) -> bool:
        """Basic email validation"""
        if "@" in value and "." in value.split("@")[-1]:
            self.clear_error()
            return True
        else:
            self.set_error("Please enter a valid email address")
            return False
    
    def set_error(self, message: str):
        """Set error message and styling"""
        self.error_var.set(message)
        self.entry.configure(style='Error.TEntry')
    
    def clear_error(self):
        """Clear error message and styling"""
        self.error_var.set("")
        self.entry.configure(style='TEntry')
    
    def get(self) -> str:
        """Get the current value"""
        return self.value_var.get().strip()
    
    def set(self, value: str):
        """Set the value"""
        self.value_var.set(value)
        self.validate()


class DatePicker(ttk.Frame):
    """
    Enhanced date picker with quick selection buttons and validation.
    
    Usage:
        picker = DatePicker(parent, "Select Date")
        date_str = picker.get()  # Returns ISO format date string
    """
    
    def __init__(self, parent, label: str = "Date", **kwargs):
        super().__init__(parent, style='Panel.TFrame')
        
        self.date_var = tk.StringVar()
        self.setup_ui(label, **kwargs)
        self.set_today()
    
    def setup_ui(self, label: str, **kwargs):
        """Setup the UI components"""
        # Label
        ttk.Label(self, text=label, style='PanelBody.TLabel').pack(anchor="w", pady=(0, 4))
        
        # Main frame for date controls
        main_frame = ttk.Frame(self, style='Panel.TFrame')
        main_frame.pack(fill="x")
        
        # Date entry
        self.date_entry = SmartEntry(
            main_frame,
            "",
            value_type="date",
            tooltip="Enter date in YYYY-MM-DD format",
            width=12
        )
        self.date_entry.pack(side="left", padx=(0, 8))
        
        # Sync our variable with the entry's variable
        self.date_entry.value_var = self.date_var
        self.date_entry.entry.configure(textvariable=self.date_var)
        
        # Quick selection buttons
        buttons_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        buttons_frame.pack(side="left")
        
        quick_buttons = [
            ("Today", self.set_today),
            ("Yesterday", self.set_yesterday),
            ("Week ago", self.set_week_ago)
        ]
        
        for text, command in quick_buttons:
            btn = ttk.Button(buttons_frame, text=text, command=command, width=8)
            btn.pack(side="left", padx=1)
            ToolTip(btn, f"Set date to {text.lower()}")
    
    def set_today(self):
        """Set date to today"""
        self.date_var.set(_dt.date.today().isoformat())
    
    def set_yesterday(self):
        """Set date to yesterday"""
        yesterday = _dt.date.today() - _dt.timedelta(days=1)
        self.date_var.set(yesterday.isoformat())
    
    def set_week_ago(self):
        """Set date to one week ago"""
        week_ago = _dt.date.today() - _dt.timedelta(days=7)
        self.date_var.set(week_ago.isoformat())
    
    def get(self) -> str:
        """Get the current date value"""
        return self.date_var.get()
    
    def set(self, date_str: str):
        """Set the date value"""
        self.date_var.set(date_str)


class KeyboardShortcuts:
    """
    Centralized keyboard shortcuts management for the application.
    
    Usage:
        shortcuts = KeyboardShortcuts(root)
        shortcuts.add_shortcut("Control-r", refresh_function, "Refresh dashboard")
    """
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.shortcuts = {}
        self.setup_default_shortcuts()
    
    def setup_default_shortcuts(self):
        """Setup commonly used shortcuts"""
        # Help shortcut is always available
        self.root.bind("<F1>", lambda e: self.show_help())
    
    def add_shortcut(self, key_combination: str, callback: Callable, description: str = ""):
        """Add a keyboard shortcut"""
        self.shortcuts[key_combination] = {
            'callback': callback,
            'description': description
        }
        self.root.bind(f"<{key_combination}>", lambda e: callback())
    
    def show_help(self):
        """Show keyboard shortcuts help dialog"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Keyboard Shortcuts")
        help_window.geometry("400x300")
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Center the window
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (help_window.winfo_screenheight() // 2) - (300 // 2)
        help_window.geometry(f"400x300+{x}+{y}")
        
        # Header
        header_frame = ttk.Frame(help_window, padding=16)
        header_frame.pack(fill="x")
        
        ttk.Label(
            header_frame,
            text="Keyboard Shortcuts",
            font=("TkDefaultFont", 14, "bold")
        ).pack()
        
        # Shortcuts list
        list_frame = ttk.Frame(help_window, padding=(16, 0, 16, 16))
        list_frame.pack(fill="both", expand=True)
        
        # Create scrollable text widget
        text_widget = tk.Text(
            list_frame,
            wrap="word",
            font=("TkDefaultFont", 10),
            relief="flat",
            bg="#f8f9fa",
            fg="#212529"
        )
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add shortcuts to text
        shortcuts_text = "Available Keyboard Shortcuts:\n\n"
        shortcuts_text += "F1                    Show this help\n"
        
        for key, info in self.shortcuts.items():
            if info['description']:
                # Format key combination for display
                display_key = key.replace("Control", "Ctrl").replace("-", "+")
                shortcuts_text += f"{display_key:<20} {info['description']}\n"
        
        if not self.shortcuts:
            shortcuts_text += "\nNo additional shortcuts configured."
        
        text_widget.insert("1.0", shortcuts_text)
        text_widget.configure(state="disabled")
        
        # Close button
        button_frame = ttk.Frame(help_window, padding=16)
        button_frame.pack(fill="x")
        
        ttk.Button(
            button_frame,
            text="Close",
            command=help_window.destroy
        ).pack(anchor="center")


class AutoRefreshManager:
    """
    Intelligent auto-refresh system that updates UI components based on user activity
    and data importance. Implements smart intervals and pause/resume functionality.
    
    Usage:
        refresh_manager = AutoRefreshManager(root)
        refresh_manager.add_callback("dashboard", refresh_dashboard, interval=30)
        refresh_manager.start()
    """
    
    def __init__(self, root: tk.Widget):
        self.root = root
        self.callbacks: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        self.is_paused = False
        self.thread = None
        self.last_user_activity = time.time()
        self.activity_threshold = 300  # 5 minutes of inactivity before slowing refresh
        
        # Track user activity
        self.setup_activity_tracking()
    
    def setup_activity_tracking(self):
        """Setup event bindings to track user activity"""
        def on_activity(event=None):
            self.last_user_activity = time.time()
        
        # Bind to common activity events
        self.root.bind_all("<Button-1>", on_activity)
        self.root.bind_all("<Key>", on_activity)
        self.root.bind_all("<Motion>", on_activity)
    
    def add_callback(self, name: str, callback: Callable, interval: int = 60, 
                    priority: str = "normal", condition: Optional[Callable] = None):
        """
        Add a callback to the refresh system
        
        Args:
            name: Unique identifier for the callback
            callback: Function to call
            interval: Refresh interval in seconds
            priority: 'high', 'normal', or 'low' - affects refresh frequency during inactivity
            condition: Optional function that returns True if refresh should happen
        """
        self.callbacks[name] = {
            'callback': callback,
            'interval': interval,
            'priority': priority,
            'condition': condition,
            'last_run': 0,
            'error_count': 0
        }
    
    def remove_callback(self, name: str):
        """Remove a callback from the refresh system"""
        if name in self.callbacks:
            del self.callbacks[name]
    
    def start(self):
        """Start the auto-refresh system"""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the auto-refresh system"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def pause(self):
        """Pause auto-refresh (useful during user input)"""
        self.is_paused = True
    
    def resume(self):
        """Resume auto-refresh"""
        self.is_paused = False
    
    def _refresh_loop(self):
        """Main refresh loop running in background thread"""
        while self.is_running:
            try:
                if not self.is_paused:
                    current_time = time.time()
                    inactive_time = current_time - self.last_user_activity
                    is_user_inactive = inactive_time > self.activity_threshold
                    
                    for name, info in self.callbacks.items():
                        # Skip if condition function returns False
                        if info['condition'] and not info['condition']():
                            continue
                        
                        # Calculate effective interval based on priority and user activity
                        base_interval = info['interval']
                        if is_user_inactive:
                            if info['priority'] == 'low':
                                effective_interval = base_interval * 3
                            elif info['priority'] == 'normal':
                                effective_interval = base_interval * 2
                            else:  # high priority
                                effective_interval = base_interval
                        else:
                            effective_interval = base_interval
                        
                        # Check if it's time to refresh this callback
                        if current_time - info['last_run'] >= effective_interval:
                            try:
                                # Schedule callback on main thread
                                self.root.after_idle(info['callback'])
                                info['last_run'] = current_time
                                info['error_count'] = 0
                            except Exception as e:
                                info['error_count'] += 1
                                # Stop calling if too many errors
                                if info['error_count'] > 5:
                                    print(f"Auto-refresh: Disabling {name} due to repeated errors: {e}")
                                    del self.callbacks[name]
                                    break
                
                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Auto-refresh error: {e}")
                time.sleep(5)  # Wait longer on error
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the refresh system"""
        inactive_time = time.time() - self.last_user_activity
        return {
            'running': self.is_running,
            'paused': self.is_paused,
            'callbacks_count': len(self.callbacks),
            'user_inactive': inactive_time > self.activity_threshold,
            'inactive_time': inactive_time
        }


class TrendCard(ttk.Frame):
    """
    Enhanced metric card with trend visualization and sparkline charts.
    Shows current value, trend direction, and mini chart of recent history.
    
    Usage:
        card = TrendCard(parent, "Steps", icon="👟", color="#3b82f6")
        card.update_data([1000, 1200, 900, 1500, 1800], "1,800", "↗ +300")
    """
    
    def __init__(self, parent, title: str, icon: str = "", color: str = "#3b82f6", **kwargs):
        super().__init__(parent, style='Card.TFrame', **kwargs)
        
        self.title = title
        self.icon = icon
        self.color = color
        self.trend_data: List[float] = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the card UI components"""
        self.configure(padding=(16, 14))
        
        # Main container
        main_frame = ttk.Frame(self, style='Card.TFrame')
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(1, weight=1)
        
        # Accent strip
        self.accent_canvas = tk.Canvas(main_frame, width=4, highlightthickness=0, bd=0)
        self.accent_canvas.grid(row=0, column=0, sticky="ns", padx=(0, 12))
        
        # Content area
        content_frame = ttk.Frame(main_frame, style='Card.TFrame')
        content_frame.grid(row=0, column=1, sticky="nsew")
        content_frame.columnconfigure(1, weight=1)
        
        # Header row: icon + title + trend indicator
        header_frame = ttk.Frame(content_frame, style='Card.TFrame')
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        header_frame.columnconfigure(1, weight=1)
        
        # Icon
        self.icon_label = ttk.Label(header_frame, text=self.icon, font=("TkDefaultFont", 14))
        self.icon_label.grid(row=0, column=0, sticky="w")
        
        # Title
        self.title_label = ttk.Label(header_frame, text=self.title, font=("TkDefaultFont", 10, "bold"))
        self.title_label.grid(row=0, column=1, sticky="w", padx=(8, 0))
        
        # Trend indicator
        self.trend_label = ttk.Label(header_frame, text="", font=("TkDefaultFont", 9))
        self.trend_label.grid(row=0, column=2, sticky="e")
        
        # Value row
        self.value_label = ttk.Label(
            content_frame, 
            text="--", 
            font=("TkDefaultFont", 18, "bold"),
            foreground=self.color
        )
        self.value_label.grid(row=1, column=0, sticky="w", pady=(0, 8))
        
        # Sparkline canvas
        self.chart_canvas = tk.Canvas(
            content_frame, 
            width=80, 
            height=30, 
            highlightthickness=0, 
            bd=0,
            bg="white"
        )
        self.chart_canvas.grid(row=1, column=1, sticky="e", padx=(8, 0))
        
        # Subtitle/description
        self.subtitle_label = ttk.Label(
            content_frame, 
            text="", 
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        self.subtitle_label.grid(row=2, column=0, columnspan=2, sticky="w")
    
    def update_data(self, trend_data: List[float], current_value: str, 
                   trend_text: str = "", subtitle: str = ""):
        """Update the card with new data"""
        self.trend_data = trend_data[-10:]  # Keep last 10 points
        
        # Update text elements
        self.value_label.configure(text=current_value)
        self.trend_label.configure(text=trend_text)
        self.subtitle_label.configure(text=subtitle)
        
        # Update sparkline
        self.draw_sparkline()
        
        # Update accent strip
        self.update_accent_color()
    
    def draw_sparkline(self):
        """Draw a sparkline chart showing trend"""
        if len(self.trend_data) < 2:
            return
        
        canvas = self.chart_canvas
        canvas.delete("all")
        
        width = 80
        height = 30
        padding = 4
        
        # Calculate dimensions
        chart_width = width - (2 * padding)
        chart_height = height - (2 * padding)
        
        # Scale data to fit canvas
        min_val = min(self.trend_data)
        max_val = max(self.trend_data)
        val_range = max_val - min_val if max_val != min_val else 1
        
        # Create points for line
        points = []
        for i, value in enumerate(self.trend_data):
            x = padding + (i / (len(self.trend_data) - 1)) * chart_width
            y = padding + chart_height - ((value - min_val) / val_range) * chart_height
            points.extend([x, y])
        
        # Draw line
        if len(points) >= 4:
            canvas.create_line(points, fill=self.color, width=2, smooth=True)
        
        # Draw points
        for i in range(0, len(points), 2):
            x, y = points[i], points[i + 1]
            canvas.create_oval(x-1, y-1, x+1, y+1, fill=self.color, outline=self.color)
        
        # Highlight last point
        if len(points) >= 2:
            last_x, last_y = points[-2], points[-1]
            canvas.create_oval(last_x-2, last_y-2, last_x+2, last_y+2, 
                             fill=self.color, outline="white", width=1)
    
    def update_accent_color(self):
        """Update accent strip color based on trend"""
        if len(self.trend_data) < 2:
            return
        
        # Determine trend direction
        recent_trend = self.trend_data[-1] - self.trend_data[-2] if len(self.trend_data) >= 2 else 0
        
        if recent_trend > 0:
            color = "#10b981"  # Green for upward trend
        elif recent_trend < 0:
            color = "#ef4444"  # Red for downward trend
        else:
            color = self.color  # Default color for no change
        
        # Update accent strip
        self.accent_canvas.delete("all")
        self.accent_canvas.create_rectangle(0, 0, 4, 100, fill=color, outline=color)


class SmartNotificationCenter:
    """
    Intelligent notification system that analyzes user data patterns
    and provides contextual insights and recommendations.
    
    Usage:
        notif_center = SmartNotificationCenter(root)
        notif_center.analyze_and_notify(user_data)
    """
    
    def __init__(self, root: tk.Widget):
        self.root = root
        self.notification_history: List[Dict] = []
        self.user_preferences = {
            'hydration_reminders': True,
            'achievement_celebrations': True,
            'health_insights': True,
            'streak_notifications': True
        }
    
    def analyze_and_notify(self, data: Dict[str, Any]):
        """Analyze user data and trigger relevant notifications"""
        notifications = []
        
        # Hydration analysis
        if data.get('hydration_pct', 0) < 50 and self.user_preferences['hydration_reminders']:
            notifications.append({
                'type': 'warning',
                'title': 'Hydration Reminder',
                'message': f"You're at {data.get('hydration_pct', 0)}% of your daily water goal. Consider drinking more water!",
                'action': 'add_water',
                'priority': 'high'
            })
        
        # Achievement detection
        if data.get('steps', 0) >= 10000 and self.user_preferences['achievement_celebrations']:
            if not self._notification_sent_today('steps_achievement'):
                notifications.append({
                    'type': 'success',
                    'title': '🎉 Achievement Unlocked!',
                    'message': f"Fantastic! You've reached {data.get('steps', 0):,} steps today!",
                    'action': None,
                    'priority': 'normal'
                })
                self._mark_notification_sent('steps_achievement')
        
        # Health score insights
        health_score = data.get('health_score', 0)
        if health_score < 60 and self.user_preferences['health_insights']:
            recommendations = self._generate_health_recommendations(data)
            notifications.append({
                'type': 'info',
                'title': 'Health Insight',
                'message': f"Your health score is {health_score}. {recommendations}",
                'action': 'view_insights',
                'priority': 'normal'
            })
        
        # Streak notifications
        if data.get('hydration_streak', 0) >= 7 and self.user_preferences['streak_notifications']:
            if not self._notification_sent_today('hydration_streak'):
                notifications.append({
                    'type': 'success',
                    'title': '🔥 Streak Alert!',
                    'message': f"Amazing! {data.get('hydration_streak', 0)} days of hydration goals met!",
                    'action': None,
                    'priority': 'normal'
                })
                self._mark_notification_sent('hydration_streak')
        
        # Show notifications
        for notification in notifications:
            self._show_smart_notification(notification)
    
    def _generate_health_recommendations(self, data: Dict[str, Any]) -> str:
        """Generate personalized health recommendations"""
        recommendations = []
        
        if data.get('hydration_pct', 0) < 80:
            recommendations.append("increase water intake")
        if data.get('steps', 0) < 8000:
            recommendations.append("add more daily movement")
        if data.get('sleep_hours', 0) < 7:
            recommendations.append("prioritize better sleep")
        if data.get('mood', 3) < 3:
            recommendations.append("focus on stress management")
        
        if recommendations:
            return f"Try to: {', '.join(recommendations[:2])}."
        return "Keep up the great work!"
    
    def _show_smart_notification(self, notification: Dict[str, Any]):
        """Show a smart notification with contextual actions"""
        # Create enhanced toast with action buttons if applicable
        toast = SmartNotificationToast(
            self.root,
            notification['title'],
            notification['message'],
            notification['type'],
            notification.get('action'),
            duration=5000 if notification['priority'] == 'high' else 3000
        )
        
        # Log notification
        self.notification_history.append({
            **notification,
            'timestamp': _dt.datetime.now(),
            'shown': True
        })
    
    def _notification_sent_today(self, notification_type: str) -> bool:
        """Check if a notification type was already sent today"""
        today = _dt.date.today()
        return any(
            n.get('type') == notification_type and 
            n.get('timestamp', _dt.datetime.min).date() == today
            for n in self.notification_history
        )
    
    def _mark_notification_sent(self, notification_type: str):
        """Mark a notification type as sent for today"""
        self.notification_history.append({
            'type': notification_type,
            'timestamp': _dt.datetime.now(),
            'shown': True
        })


class SmartNotificationToast(NotificationToast):
    """
    Enhanced notification toast with action buttons and smart behavior.
    Extends the basic NotificationToast with interactive capabilities.
    """
    
    def __init__(self, parent: tk.Widget, title: str, message: str, 
                 toast_type: str = "info", action: Optional[str] = None, duration: int = 3000):
        self.title = title
        self.action = action
        
        # Don't call parent __init__ yet, we'll override create_toast
        self.parent = parent
        self.duration = duration
        self.toast = None
        
        # Color schemes for different notification types
        self.colors = {
            "info": {"bg": "#e3f2fd", "fg": "#1976d2", "border": "#2196f3"},
            "success": {"bg": "#e8f5e8", "fg": "#2e7d32", "border": "#4caf50"},
            "warning": {"bg": "#fff3e0", "fg": "#f57c00", "border": "#ff9800"},
            "error": {"bg": "#ffebee", "fg": "#d32f2f", "border": "#f44336"}
        }
        
        self.create_smart_toast(title, message, toast_type)
    
    def create_smart_toast(self, title: str, message: str, toast_type: str):
        """Create an enhanced toast with title and optional action buttons"""
        colors = self.colors.get(toast_type, self.colors["info"])
        
        # Create toplevel window
        self.toast = tk.Toplevel(self.parent)
        self.toast.wm_overrideredirect(True)
        
        # Position in top-right corner
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        
        toast_width = 350
        toast_height = 100 if self.action else 80
        
        x = parent_x + parent_width - toast_width - 20
        y = parent_y + 60
        
        self.toast.wm_geometry(f"{toast_width}x{toast_height}+{x}+{y}")
        
        # Create main frame with rounded appearance
        main_frame = tk.Frame(
            self.toast,
            bg=colors["bg"],
            relief="raised",
            bd=1,
            highlightbackground=colors["border"],
            highlightthickness=2
        )
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Header with title
        header_frame = tk.Frame(main_frame, bg=colors["bg"])
        header_frame.pack(fill="x", padx=12, pady=(8, 4))
        
        # Icon
        icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
        tk.Label(
            header_frame,
            text=icons.get(toast_type, "ℹ️"),
            bg=colors["bg"],
            font=("TkDefaultFont", 12)
        ).pack(side="left")
        
        # Title
        tk.Label(
            header_frame,
            text=title,
            bg=colors["bg"],
            fg=colors["fg"],
            font=("TkDefaultFont", 10, "bold")
        ).pack(side="left", padx=(8, 0))
        
        # Close button
        close_btn = tk.Button(
            header_frame,
            text="×",
            bg=colors["bg"],
            fg=colors["fg"],
            font=("TkDefaultFont", 12, "bold"),
            relief="flat",
            bd=0,
            command=self.destroy,
            cursor="hand2"
        )
        close_btn.pack(side="right")
        
        # Message
        message_frame = tk.Frame(main_frame, bg=colors["bg"])
        message_frame.pack(fill="x", padx=12, pady=(0, 8))
        
        tk.Label(
            message_frame,
            text=message,
            bg=colors["bg"],
            fg=colors["fg"],
            font=("TkDefaultFont", 9),
            wraplength=280,
            justify="left"
        ).pack(anchor="w")
        
        # Action buttons if applicable
        if self.action:
            action_frame = tk.Frame(main_frame, bg=colors["bg"])
            action_frame.pack(fill="x", padx=12, pady=(0, 8))
            
            action_text = {
                'add_water': 'Add Water',
                'view_insights': 'View Insights',
                'log_activity': 'Log Activity'
            }.get(self.action, 'Take Action')
            
            tk.Button(
                action_frame,
                text=action_text,
                bg=colors["border"],
                fg="white",
                font=("TkDefaultFont", 8, "bold"),
                relief="flat",
                bd=0,
                padx=8,
                pady=2,
                cursor="hand2",
                command=self._handle_action
            ).pack(side="right")
        
        # Auto-destroy after duration
        self.toast.after(self.duration, self.destroy)
        
        # Bring to front
        self.toast.lift()
        self.toast.attributes('-topmost', True)
    
    def _handle_action(self):
        """Handle action button clicks"""
        # This would integrate with the main application's functions
        # For now, just close the notification
        print(f"Action triggered: {self.action}")
        self.destroy()


class BreadcrumbNavigation(ttk.Frame):
    """
    Breadcrumb navigation component for better user orientation.
    Shows current location and provides quick navigation to parent sections.
    
    Usage:
        breadcrumb = BreadcrumbNavigation(parent)
        breadcrumb.update_path(["Dashboard", "Activity", "Today's Log"])
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, style='Header.TFrame', **kwargs)
        self.path_elements: List[str] = []
        self.navigation_callbacks: Dict[str, Callable] = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the breadcrumb UI"""
        self.configure(padding=(8, 4))
        
        # Home icon
        self.home_label = ttk.Label(
            self,
            text="🏠",
            font=("TkDefaultFont", 10),
            cursor="hand2"
        )
        self.home_label.pack(side="left", padx=(0, 4))
        
        # Dynamic content frame
        self.content_frame = ttk.Frame(self, style='Header.TFrame')
        self.content_frame.pack(side="left", fill="x", expand=True)
    
    def update_path(self, path_elements: List[str]):
        """Update the breadcrumb path"""
        self.path_elements = path_elements
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the breadcrumb display"""
        # Clear existing content
        for child in self.content_frame.winfo_children():
            child.destroy()
        
        # Add path elements
        for i, element in enumerate(self.path_elements):
            # Add separator
            if i > 0:
                separator = ttk.Label(
                    self.content_frame,
                    text="›",
                    font=("TkDefaultFont", 10),
                    foreground="gray"
                )
                separator.pack(side="left", padx=4)
            
            # Add path element
            is_last = i == len(self.path_elements) - 1
            
            if is_last:
                # Current page - not clickable
                label = ttk.Label(
                    self.content_frame,
                    text=element,
                    font=("TkDefaultFont", 10, "bold"),
                    foreground="#2563eb"
                )
            else:
                # Clickable parent path
                label = ttk.Label(
                    self.content_frame,
                    text=element,
                    font=("TkDefaultFont", 10),
                    foreground="#1976d2",
                    cursor="hand2"
                )
                # Bind click event
                label.bind("<Button-1>", lambda e, elem=element: self._navigate_to(elem))
                
                # Hover effects
                def on_enter(e, lbl=label):
                    lbl.configure(foreground="#0d47a1")
                def on_leave(e, lbl=label):
                    lbl.configure(foreground="#1976d2")
                
                label.bind("<Enter>", on_enter)
                label.bind("<Leave>", on_leave)
            
            label.pack(side="left", padx=2)
    
    def add_navigation_callback(self, element: str, callback: Callable):
        """Add a callback for navigating to a specific element"""
        self.navigation_callbacks[element] = callback
    
    def _navigate_to(self, element: str):
        """Handle navigation to a breadcrumb element"""
        if element in self.navigation_callbacks:
            self.navigation_callbacks[element]()


class ProgressRing(tk.Canvas):
    """
    Circular progress indicator with customizable colors and animation.
    Perfect for showing completion percentages and health scores.
    
    Usage:
        ring = ProgressRing(parent, size=100, thickness=8)
        ring.set_progress(75, "75%", color="#10b981")
    """
    
    def __init__(self, parent, size: int = 80, thickness: int = 6, **kwargs):
        self.size = size
        self.thickness = thickness
        self.progress = 0
        self.color = "#3b82f6"
        
        super().__init__(
            parent,
            width=size,
            height=size,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        
        self.setup_ring()
    
    def setup_ring(self):
        """Setup the ring graphics"""
        center = self.size // 2
        radius = (self.size - self.thickness) // 2
        
        # Background ring
        self.bg_ring = self.create_oval(
            center - radius, center - radius,
            center + radius, center + radius,
            outline="#e5e7eb",
            width=self.thickness,
            fill=""
        )
        
        # Progress arc (initially hidden)
        self.progress_arc = self.create_arc(
            center - radius, center - radius,
            center + radius, center + radius,
            start=90,
            extent=0,
            outline=self.color,
            width=self.thickness,
            style="arc"
        )
        
        # Center text
        self.center_text = self.create_text(
            center, center,
            text="0%",
            font=("TkDefaultFont", min(12, self.size // 6), "bold"),
            fill="#374151"
        )
    
    def set_progress(self, percentage: float, text: str = "", color: str = None, animate: bool = True):
        """Update the progress ring"""
        if color:
            self.color = color
            self.itemconfig(self.progress_arc, outline=color)
        
        target_progress = max(0, min(100, percentage))
        display_text = text or f"{int(target_progress)}%"
        
        if animate and abs(target_progress - self.progress) > 1:
            self._animate_to_progress(target_progress, display_text)
        else:
            self._update_progress(target_progress, display_text)
    
    def _animate_to_progress(self, target: float, text: str):
        """Animate progress change"""
        steps = 20
        step_size = (target - self.progress) / steps
        
        def animate_step(current_step: int):
            if current_step <= steps:
                new_progress = self.progress + (step_size * current_step)
                self._update_progress(new_progress, text if current_step == steps else f"{int(new_progress)}%")
                
                if current_step < steps:
                    self.after(20, lambda: animate_step(current_step + 1))
                else:
                    self.progress = target
        
        animate_step(1)
    
    def _update_progress(self, percentage: float, text: str):
        """Update the visual progress"""
        # Calculate arc extent (negative for clockwise)
        extent = -(percentage / 100) * 360
        
        # Update arc
        self.itemconfig(self.progress_arc, extent=extent)
        
        # Update center text
        self.itemconfig(self.center_text, text=text)


class StatusBar(ttk.Frame):
    """
    Enhanced status bar with multiple information zones and real-time updates.
    Shows connection status, last refresh time, and system information.
    
    Usage:
        status_bar = StatusBar(parent)
        status_bar.update_status("Connected", "success")
        status_bar.set_info("Last updated: 14:32")
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the status bar components"""
        # Status indicator
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(side="left", padx=(8, 16))
        
        self.status_indicator = tk.Canvas(
            self.status_frame,
            width=12,
            height=12,
            highlightthickness=0,
            bd=0
        )
        self.status_indicator.pack(side="left", padx=(0, 4))
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="Ready",
            font=("TkDefaultFont", 9)
        )
        self.status_label.pack(side="left")
        
        # Separator
        ttk.Separator(self, orient="vertical").pack(side="left", fill="y", padx=8)
        
        # Info area
        self.info_label = ttk.Label(
            self,
            text="",
            font=("TkDefaultFont", 9),
            foreground="gray"
        )
        self.info_label.pack(side="left", padx=(0, 8))
        
        # Right side - system info
        self.system_frame = ttk.Frame(self)
        self.system_frame.pack(side="right", padx=8)
        
        self.system_label = ttk.Label(
            self.system_frame,
            text="",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        self.system_label.pack()
        
        # Initialize with default status
        self.update_status("Ready", "info")
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update the status indicator and message"""
        colors = {
            "success": "#10b981",
            "warning": "#f59e0b", 
            "error": "#ef4444",
            "info": "#3b82f6"
        }
        
        color = colors.get(status_type, colors["info"])
        
        # Update indicator
        self.status_indicator.delete("all")
        self.status_indicator.create_oval(2, 2, 10, 10, fill=color, outline=color)
        
        # Update label
        self.status_label.configure(text=message)
    
    def set_info(self, info_text: str):
        """Set the info area text"""
        self.info_label.configure(text=info_text)
    
    def set_system_info(self, system_text: str):
        """Set the system info text"""
        self.system_label.configure(text=system_text)


class InteractiveChart(ttk.Frame):
    """
    Interactive chart widget with zoom, pan, and hover capabilities.
    Provides enhanced data visualization for health metrics.
    
    Usage:
        chart = InteractiveChart(parent, width=400, height=300)
        chart.plot_data(dates, values, "Daily Steps")
    """
    
    def __init__(self, parent, width: int = 400, height: int = 300, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.chart_width = width
        self.chart_height = height
        self.data_points: List[Tuple[float, float]] = []
        self.labels: List[str] = []
        self.title = ""
        
        # Interaction state
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.is_panning = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the chart UI"""
        # Create canvas
        self.canvas = tk.Canvas(
            self,
            width=self.chart_width,
            height=self.chart_height,
            bg="white",
            highlightthickness=1,
            highlightbackground="#e5e7eb"
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Bind interaction events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.canvas.bind("<Motion>", self.on_hover)
        
        # Tooltip for hover
        self.tooltip = None
    
    def plot_data(self, x_values: List[float], y_values: List[float], 
                  title: str = "", labels: List[str] = None):
        """Plot data on the chart"""
        if len(x_values) != len(y_values):
            raise ValueError("x_values and y_values must have the same length")
        
        self.data_points = list(zip(x_values, y_values))
        self.labels = labels or [f"Point {i+1}" for i in range(len(x_values))]
        self.title = title
        
        self.redraw()
    
    def redraw(self):
        """Redraw the entire chart"""
        self.canvas.delete("all")
        
        if not self.data_points:
            return
        
        # Calculate bounds
        padding = 40
        chart_area_width = self.chart_width - (2 * padding)
        chart_area_height = self.chart_height - (2 * padding)
        
        # Data bounds
        x_values = [p[0] for p in self.data_points]
        y_values = [p[1] for p in self.data_points]
        
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        
        x_range = x_max - x_min if x_max != x_min else 1
        y_range = y_max - y_min if y_max != y_min else 1
        
        # Apply zoom and pan
        effective_width = chart_area_width * self.zoom_factor
        effective_height = chart_area_height * self.zoom_factor
        
        # Convert data points to canvas coordinates
        canvas_points = []
        for x, y in self.data_points:
            canvas_x = padding + ((x - x_min) / x_range) * effective_width + self.pan_x
            canvas_y = self.chart_height - padding - ((y - y_min) / y_range) * effective_height + self.pan_y
            canvas_points.append((canvas_x, canvas_y))
        
        # Draw grid
        self.draw_grid(padding, chart_area_width, chart_area_height)
        
        # Draw axes
        self.draw_axes(padding, chart_area_width, chart_area_height, x_min, x_max, y_min, y_max)
        
        # Draw data line
        if len(canvas_points) > 1:
            line_points = []
            for x, y in canvas_points:
                line_points.extend([x, y])
            
            self.canvas.create_line(
                line_points,
                fill="#3b82f6",
                width=2,
                smooth=True,
                tags="data_line"
            )
        
        # Draw data points
        for i, (x, y) in enumerate(canvas_points):
            self.canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill="#3b82f6",
                outline="white",
                width=1,
                tags=f"data_point_{i}"
            )
        
        # Draw title
        if self.title:
            self.canvas.create_text(
                self.chart_width // 2, 20,
                text=self.title,
                font=("TkDefaultFont", 12, "bold"),
                fill="#374151"
            )
    
    def draw_grid(self, padding: int, width: int, height: int):
        """Draw chart grid"""
        grid_color = "#f3f4f6"
        
        # Vertical grid lines
        for i in range(1, 10):
            x = padding + (i * width // 10)
            self.canvas.create_line(
                x, padding, x, padding + height,
                fill=grid_color,
                width=1
            )
        
        # Horizontal grid lines
        for i in range(1, 8):
            y = padding + (i * height // 8)
            self.canvas.create_line(
                padding, y, padding + width, y,
                fill=grid_color,
                width=1
            )
    
    def draw_axes(self, padding: int, width: int, height: int, 
                  x_min: float, x_max: float, y_min: float, y_max: float):
        """Draw chart axes with labels"""
        # X-axis
        self.canvas.create_line(
            padding, padding + height,
            padding + width, padding + height,
            fill="#6b7280",
            width=2
        )
        
        # Y-axis
        self.canvas.create_line(
            padding, padding,
            padding, padding + height,
            fill="#6b7280",
            width=2
        )
        
        # X-axis labels
        for i in range(0, 6):
            x = padding + (i * width // 5)
            value = x_min + (i * (x_max - x_min) / 5)
            self.canvas.create_text(
                x, padding + height + 15,
                text=f"{value:.1f}",
                font=("TkDefaultFont", 8),
                fill="#6b7280"
            )
        
        # Y-axis labels
        for i in range(0, 6):
            y = padding + height - (i * height // 5)
            value = y_min + (i * (y_max - y_min) / 5)
            self.canvas.create_text(
                padding - 15, y,
                text=f"{value:.0f}",
                font=("TkDefaultFont", 8),
                fill="#6b7280"
            )
    
    def on_click(self, event):
        """Handle mouse click"""
        self.is_panning = True
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
    
    def on_drag(self, event):
        """Handle mouse drag (panning)"""
        if self.is_panning:
            dx = event.x - self.last_mouse_x
            dy = event.y - self.last_mouse_y
            
            self.pan_x += dx
            self.pan_y += dy
            
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            
            self.redraw()
    
    def on_release(self, event):
        """Handle mouse release"""
        self.is_panning = False
    
    def on_scroll(self, event):
        """Handle mouse scroll (zooming)"""
        # Zoom in/out
        zoom_delta = 0.1 if event.delta > 0 else -0.1
        new_zoom = max(0.5, min(3.0, self.zoom_factor + zoom_delta))
        
        if new_zoom != self.zoom_factor:
            self.zoom_factor = new_zoom
            self.redraw()
    
    def on_hover(self, event):
        """Handle mouse hover for tooltips"""
        # Find nearest data point
        closest_point = None
        min_distance = float('inf')
        
        for i, (x, y) in enumerate(self.get_canvas_points()):
            distance = math.sqrt((event.x - x)**2 + (event.y - y)**2)
            if distance < min_distance and distance < 20:  # 20px threshold
                min_distance = distance
                closest_point = i
        
        if closest_point is not None:
            self.show_tooltip(event.x, event.y, closest_point)
        else:
            self.hide_tooltip()
    
    def get_canvas_points(self) -> List[Tuple[float, float]]:
        """Get current canvas coordinates of data points"""
        if not self.data_points:
            return []
        
        padding = 40
        chart_area_width = self.chart_width - (2 * padding)
        chart_area_height = self.chart_height - (2 * padding)
        
        x_values = [p[0] for p in self.data_points]
        y_values = [p[1] for p in self.data_points]
        
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        
        x_range = x_max - x_min if x_max != x_min else 1
        y_range = y_max - y_min if y_max != y_min else 1
        
        effective_width = chart_area_width * self.zoom_factor
        effective_height = chart_area_height * self.zoom_factor
        
        canvas_points = []
        for x, y in self.data_points:
            canvas_x = padding + ((x - x_min) / x_range) * effective_width + self.pan_x
            canvas_y = self.chart_height - padding - ((y - y_min) / y_range) * effective_height + self.pan_y
            canvas_points.append((canvas_x, canvas_y))
        
        return canvas_points
    
    def show_tooltip(self, x: int, y: int, point_index: int):
        """Show tooltip for data point"""
        if self.tooltip:
            self.tooltip.destroy()
        
        data_x, data_y = self.data_points[point_index]
        label = self.labels[point_index] if point_index < len(self.labels) else f"Point {point_index + 1}"
        
        tooltip_text = f"{label}\nX: {data_x:.1f}\nY: {data_y:.1f}"
        
        self.tooltip = tk.Toplevel(self.canvas)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x + self.winfo_rootx() + 10}+{y + self.winfo_rooty() + 10}")
        
        tk.Label(
            self.tooltip,
            text=tooltip_text,
            background="lightyellow",
            relief="solid",
            borderwidth=1,
            font=("TkDefaultFont", 8),
            padx=4,
            pady=2
        ).pack()
    
    def hide_tooltip(self):
        """Hide tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    
    def reset_view(self):
        """Reset zoom and pan to default"""
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.redraw()


def setup_error_style(style: ttk.Style):
    """Setup error styling for enhanced widgets"""
    try:
        style.configure(
            'Error.TEntry',
            fieldbackground='#ffebee',
            bordercolor='#f44336',
            focuscolor='#f44336'
        )
    except tk.TclError:
        # Fallback if theme doesn't support these options
        pass


# Utility functions for easier integration
def show_toast(parent: tk.Widget, message: str, toast_type: str = "info", duration: int = 3000):
    """Convenience function to show a toast notification"""
    return NotificationToast(parent, message, toast_type, duration)


def show_smart_toast(parent: tk.Widget, title: str, message: str, 
                    toast_type: str = "info", action: str = None, duration: int = 3000):
    """Convenience function to show a smart toast notification with actions"""
    return SmartNotificationToast(parent, title, message, toast_type, action, duration)


def add_tooltip(widget: tk.Widget, text: str, delay: int = 500):
    """Convenience function to add a tooltip to a widget"""
    return ToolTip(widget, text, delay)


def validate_form(*smart_entries: SmartEntry) -> bool:
    """Validate multiple SmartEntry widgets"""
    all_valid = True
    for entry in smart_entries:
        if not entry.validate():
            all_valid = False
    return all_valid


def create_trend_card(parent: tk.Widget, title: str, icon: str = "", 
                     color: str = "#3b82f6", **kwargs) -> TrendCard:
    """Convenience function to create a trend card"""
    return TrendCard(parent, title, icon, color, **kwargs)


def create_progress_ring(parent: tk.Widget, size: int = 80, 
                        thickness: int = 6, **kwargs) -> ProgressRing:
    """Convenience function to create a progress ring"""
    return ProgressRing(parent, size, thickness, **kwargs)


def setup_auto_refresh(root: tk.Widget, callbacks: Dict[str, Dict[str, Any]]) -> AutoRefreshManager:
    """
    Setup auto-refresh system with multiple callbacks
    
    Args:
        root: Root widget
        callbacks: Dict with callback configs
            {
                'dashboard': {'callback': func, 'interval': 30, 'priority': 'high'},
                'charts': {'callback': func, 'interval': 60, 'priority': 'normal'}
            }
    """
    manager = AutoRefreshManager(root)
    
    for name, config in callbacks.items():
        manager.add_callback(
            name,
            config['callback'],
            config.get('interval', 60),
            config.get('priority', 'normal'),
            config.get('condition')
        )
    
    return manager


def create_interactive_chart(parent: tk.Widget, width: int = 400, 
                           height: int = 300, **kwargs) -> InteractiveChart:
    """Convenience function to create an interactive chart"""
    return InteractiveChart(parent, width, height, **kwargs)


# Enhanced styling utilities
def apply_gradient_effect(widget: tk.Widget, color1: str, color2: str):
    """Apply a gradient-like effect to a widget (simplified)"""
    # This is a simplified gradient effect
    # In a real implementation, you might use PIL or custom drawing
    pass


def animate_widget_entry(widget: tk.Widget, direction: str = "slide_in"):
    """Animate widget entrance with various effects"""
    if direction == "slide_in":
        # Slide in from right
        original_x = widget.winfo_x()
        widget.place(x=original_x + 200)
        
        def slide_step(current_x: int, step: int):
            if step < 10:
                new_x = current_x - 20
                widget.place(x=new_x)
                widget.after(20, lambda: slide_step(new_x, step + 1))
            else:
                widget.place(x=original_x)
        
        slide_step(original_x + 200, 0)
    
    elif direction == "fade_in":
        # Fade in effect (simplified)
        widget.configure(state="disabled")
        
        def fade_step(step: int):
            if step < 10:
                # Simplified fade - just enable at the end
                widget.after(50, lambda: fade_step(step + 1))
            else:
                widget.configure(state="normal")
        
        fade_step(0)


def create_modern_button(parent: tk.Widget, text: str, command: Callable = None,
                        style: str = "primary", size: str = "medium", **kwargs) -> tk.Button:
    """
    Create a modern-styled button with various presets
    
    Args:
        parent: Parent widget
        text: Button text
        command: Click callback
        style: 'primary', 'secondary', 'success', 'warning', 'danger'
        size: 'small', 'medium', 'large'
    """
    styles = {
        "primary": {"bg": "#3b82f6", "fg": "white", "active_bg": "#2563eb"},
        "secondary": {"bg": "#6b7280", "fg": "white", "active_bg": "#4b5563"},
        "success": {"bg": "#10b981", "fg": "white", "active_bg": "#059669"},
        "warning": {"bg": "#f59e0b", "fg": "white", "active_bg": "#d97706"},
        "danger": {"bg": "#ef4444", "fg": "white", "active_bg": "#dc2626"}
    }
    
    sizes = {
        "small": {"font": ("TkDefaultFont", 8), "padx": 8, "pady": 4},
        "medium": {"font": ("TkDefaultFont", 10), "padx": 12, "pady": 6},
        "large": {"font": ("TkDefaultFont", 12), "padx": 16, "pady": 8}
    }
    
    style_config = styles.get(style, styles["primary"])
    size_config = sizes.get(size, sizes["medium"])
    
    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=style_config["bg"],
        fg=style_config["fg"],
        font=size_config["font"],
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=size_config["padx"],
        pady=size_config["pady"],
        **kwargs
    )
    
    # Hover effects
    def on_enter(e):
        button.config(bg=style_config["active_bg"])
    
    def on_leave(e):
        button.config(bg=style_config["bg"])
    
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    
    return button


def create_info_panel(parent: tk.Widget, title: str, content: str, 
                     panel_type: str = "info", collapsible: bool = False) -> ttk.Frame:
    """
    Create an information panel with various styles
    
    Args:
        parent: Parent widget
        title: Panel title
        content: Panel content
        panel_type: 'info', 'success', 'warning', 'error'
        collapsible: Whether the panel can be collapsed
    """
    colors = {
        "info": {"bg": "#eff6ff", "border": "#3b82f6", "fg": "#1e40af"},
        "success": {"bg": "#f0fdf4", "border": "#10b981", "fg": "#065f46"},
        "warning": {"bg": "#fffbeb", "border": "#f59e0b", "fg": "#92400e"},
        "error": {"bg": "#fef2f2", "border": "#ef4444", "fg": "#991b1b"}
    }
    
    color_scheme = colors.get(panel_type, colors["info"])
    
    # Main frame
    panel_frame = tk.Frame(
        parent,
        bg=color_scheme["bg"],
        relief="solid",
        bd=1,
        highlightbackground=color_scheme["border"],
        highlightthickness=2
    )
    
    # Header
    header_frame = tk.Frame(panel_frame, bg=color_scheme["bg"])
    header_frame.pack(fill="x", padx=8, pady=(8, 4))
    
    # Icons for different panel types
    icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
    
    tk.Label(
        header_frame,
        text=icons.get(panel_type, "ℹ️"),
        bg=color_scheme["bg"],
        font=("TkDefaultFont", 12)
    ).pack(side="left")
    
    tk.Label(
        header_frame,
        text=title,
        bg=color_scheme["bg"],
        fg=color_scheme["fg"],
        font=("TkDefaultFont", 11, "bold")
    ).pack(side="left", padx=(8, 0))
    
    # Collapse button if collapsible
    if collapsible:
        collapse_btn = tk.Button(
            header_frame,
            text="−",
            bg=color_scheme["bg"],
            fg=color_scheme["fg"],
            font=("TkDefaultFont", 10, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        collapse_btn.pack(side="right")
    
    # Content
    content_frame = tk.Frame(panel_frame, bg=color_scheme["bg"])
    content_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
    
    content_label = tk.Label(
        content_frame,
        text=content,
        bg=color_scheme["bg"],
        fg=color_scheme["fg"],
        font=("TkDefaultFont", 9),
        wraplength=400,
        justify="left"
    )
    content_label.pack(anchor="w")
    
    # Collapse functionality
    if collapsible:
        is_collapsed = False
        
        def toggle_collapse():
            nonlocal is_collapsed
            if is_collapsed:
                content_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
                collapse_btn.config(text="−")
                is_collapsed = False
            else:
                content_frame.pack_forget()
                collapse_btn.config(text="+")
                is_collapsed = True
        
        collapse_btn.config(command=toggle_collapse)
    
    return panel_frame