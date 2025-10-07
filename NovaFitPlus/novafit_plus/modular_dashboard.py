"""
Modular Dashboard System for NovaFit Plus
========================================
Advanced drag & drop widget system for customizable dashboard layouts.
Users can rearrange, resize, and customize their dashboard widgets.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable, Tuple
import json
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

@dataclass
class WidgetConfig:
    """Configuration for dashboard widgets"""
    id: str
    title: str
    x: int
    y: int
    width: int
    height: int
    visible: bool = True
    widget_type: str = "default"
    custom_data: dict = None

    def __post_init__(self):
        if self.custom_data is None:
            self.custom_data = {}

class DashboardWidget(ABC):
    """Abstract base class for dashboard widgets"""
    
    def __init__(self, parent, config: WidgetConfig, **kwargs):
        self.parent = parent
        self.config = config
        self.frame = None
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.setup_widget()
        
    @abstractmethod
    def setup_widget(self):
        """Setup the widget UI - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def update_content(self, data: dict):
        """Update widget content with new data"""
        pass
    
    def make_draggable(self):
        """Make widget draggable"""
        self.frame.bind('<Button-1>', self.start_drag)
        self.frame.bind('<B1-Motion>', self.on_drag)
        self.frame.bind('<ButtonRelease-1>', self.stop_drag)
        
        # Make all child widgets draggable too
        for child in self.frame.winfo_children():
            child.bind('<Button-1>', self.start_drag)
            child.bind('<B1-Motion>', self.on_drag)
            child.bind('<ButtonRelease-1>', self.stop_drag)
    
    def start_drag(self, event):
        """Start dragging the widget"""
        self.is_dragging = True
        self.drag_start_x = event.x_root - self.frame.winfo_x()
        self.drag_start_y = event.y_root - self.frame.winfo_y()
        self.frame.configure(cursor="fleur")
    
    def on_drag(self, event):
        """Handle widget dragging"""
        if self.is_dragging:
            new_x = event.x_root - self.drag_start_x
            new_y = event.y_root - self.drag_start_y
            
            # Keep widget within parent bounds
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            widget_width = self.frame.winfo_width()
            widget_height = self.frame.winfo_height()
            
            new_x = max(0, min(new_x, parent_width - widget_width))
            new_y = max(0, min(new_y, parent_height - widget_height))
            
            self.frame.place(x=new_x, y=new_y)
            self.config.x = new_x
            self.config.y = new_y
    
    def stop_drag(self, event):
        """Stop dragging the widget"""
        self.is_dragging = False
        self.frame.configure(cursor="")

class StatsWidget(DashboardWidget):
    """Widget for displaying health statistics"""
    
    def setup_widget(self):
        self.frame = ttk.LabelFrame(
            self.parent,
            text=self.config.title,
            padding=10,
            
        )
        self.frame.place(
            x=self.config.x,
            y=self.config.y,
            width=self.config.width,
            height=self.config.height
        )
        
        # Main value display
        self.value_label = ttk.Label(
            self.frame,
            text="--",
            font=("TkDefaultFont", 24, "bold"),
            style='Value.TLabel'
        )
        self.value_label.pack(pady=(5, 0))
        
        # Subtitle/unit
        self.unit_label = ttk.Label(
            self.frame,
            text=self.config.custom_data.get('unit', ''),
            style='Unit.TLabel'
        )
        self.unit_label.pack()
        
        # Trend indicator
        self.trend_label = ttk.Label(
            self.frame,
            text="",
            style='Trend.TLabel'
        )
        self.trend_label.pack(pady=(5, 0))
        
        self.make_draggable()
    
    def update_content(self, data: dict):
        """Update stats widget with new data"""
        value = data.get('value', '--')
        unit = data.get('unit', '')
        trend = data.get('trend', '')
        
        self.value_label.config(text=str(value))
        self.unit_label.config(text=unit)
        self.trend_label.config(text=trend)

class ChartWidget(DashboardWidget):
    """Widget for displaying mini charts"""
    
    def setup_widget(self):
        self.frame = ttk.LabelFrame(
            self.parent,
            text=self.config.title,
            padding=8,
            
        )
        self.frame.place(
            x=self.config.x,
            y=self.config.y,
            width=self.config.width,
            height=self.config.height
        )
        
        # Mini chart canvas
        self.canvas = tk.Canvas(
            self.frame,
            width=self.config.width - 40,
            height=self.config.height - 60,
            highlightthickness=0,
            bg='white'
        )
        self.canvas.pack(pady=5)
        
        self.make_draggable()
    
    def update_content(self, data: dict):
        """Update chart widget with new data"""
        self.canvas.delete("all")
        values = data.get('values', [])
        
        if not values:
            self.canvas.create_text(
                self.canvas.winfo_reqwidth() // 2,
                self.canvas.winfo_reqheight() // 2,
                text="No data",
                fill="gray"
            )
            return
        
        # Draw simple line chart
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        
        if len(values) > 1:
            max_val = max(values) if max(values) > 0 else 1
            points = []
            
            for i, val in enumerate(values):
                x = i * (canvas_width / (len(values) - 1))
                y = canvas_height - (val / max_val * canvas_height * 0.8)
                points.extend([x, y])
            
            if len(points) >= 4:
                self.canvas.create_line(
                    points,
                    fill="#3b82f6",
                    width=2,
                    smooth=True
                )

class ProgressWidget(DashboardWidget):
    """Widget for displaying progress bars and goals"""
    
    def setup_widget(self):
        self.frame = ttk.LabelFrame(
            self.parent,
            text=self.config.title,
            padding=10,
            
        )
        self.frame.place(
            x=self.config.x,
            y=self.config.y,
            width=self.config.width,
            height=self.config.height
        )
        
        # Progress value
        self.progress_label = ttk.Label(
            self.frame,
            text="0%",
            font=("TkDefaultFont", 16, "bold")
        )
        self.progress_label.pack(pady=(0, 5))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame,
            variable=self.progress_var,
            maximum=100,
            length=self.config.width - 40,
            style='Accent.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(pady=5)
        
        # Goal text
        self.goal_label = ttk.Label(
            self.frame,
            text="",
            style='Goal.TLabel'
        )
        self.goal_label.pack()
        
        self.make_draggable()
    
    def update_content(self, data: dict):
        """Update progress widget with new data"""
        current = data.get('current', 0)
        goal = data.get('goal', 100)
        
        if goal > 0:
            percentage = (current / goal) * 100
            percentage = min(100, percentage)
        else:
            percentage = 0
        
        self.progress_var.set(percentage)
        self.progress_label.config(text=f"{percentage:.0f}%")
        self.goal_label.config(text=f"{current} / {goal}")

class QuickActionWidget(DashboardWidget):
    """Widget for quick actions and shortcuts"""
    
    def setup_widget(self):
        self.frame = ttk.LabelFrame(
            self.parent,
            text=self.config.title,
            padding=8,
            
        )
        self.frame.place(
            x=self.config.x,
            y=self.config.y,
            width=self.config.width,
            height=self.config.height
        )
        
        # Quick action buttons
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(fill="both", expand=True)
        
        self.make_draggable()
    
    def update_content(self, data: dict):
        """Update quick action widget with new data"""
        # Clear existing buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        actions = data.get('actions', [])
        for i, action in enumerate(actions):
            btn = ttk.Button(
                self.button_frame,
                text=action.get('text', 'Action'),
                command=action.get('command', lambda: None),
                style='Compact.TButton'
            )
            btn.pack(fill="x", pady=2)

class WeatherWidget(DashboardWidget):
    """Enhanced weather widget with emoji and detailed info"""
    
    def setup_widget(self):
        self.frame = ttk.LabelFrame(
            self.parent,
            text=self.config.title,
            padding=10,
            
        )
        self.frame.place(
            x=self.config.x,
            y=self.config.y,
            width=self.config.width,
            height=self.config.height
        )
        
        # Weather emoji and condition
        self.condition_label = ttk.Label(
            self.frame,
            text="🌡️",
            font=("TkDefaultFont", 32),
            justify="center"
        )
        self.condition_label.pack(pady=(5, 2))
        
        # Temperature display
        self.temp_label = ttk.Label(
            self.frame,
            text="--°C",
            font=("TkDefaultFont", 16, "bold"),
            style='Value.TLabel'
        )
        self.temp_label.pack()
        
        # Additional info frame
        self.info_frame = ttk.Frame(self.frame)
        self.info_frame.pack(fill="x", pady=(5, 0))
        
        # Humidity
        self.humidity_label = ttk.Label(
            self.info_frame,
            text="💧 --%",
            font=("TkDefaultFont", 10),
            style='Unit.TLabel'
        )
        self.humidity_label.pack()
        
        # Wind
        self.wind_label = ttk.Label(
            self.info_frame,
            text="💨 -- km/h",
            font=("TkDefaultFont", 10),
            style='Unit.TLabel'
        )
        self.wind_label.pack()
        
        # City
        self.city_label = ttk.Label(
            self.info_frame,
            text="📍 --",
            font=("TkDefaultFont", 9),
            style='Trend.TLabel'
        )
        self.city_label.pack(pady=(3, 0))
        
        self.make_draggable()
    
    def update_content(self, data: dict):
        """Update weather widget with new data"""
        # Import weather module for emoji functions
        try:
            from . import weather as wz
        except:
            import sys
            sys.path.append('.')
            try:
                import weather as wz
            except:
                wz = None
        
        condition_code = data.get('condition_code', 0)
        temp_max = data.get('temp_max', '--')
        temp_min = data.get('temp_min', '--')
        humidity = data.get('humidity', '--')
        wind = data.get('wind', '--')
        city = data.get('city', '--')
        
        # Update emoji and condition
        if wz and hasattr(wz, 'code_to_emoji'):
            try:
                emoji = wz.code_to_emoji(condition_code)
                self.condition_label.config(text=emoji)
            except Exception:
                self.condition_label.config(text="🌡️")
        else:
            self.condition_label.config(text="🌡️")
        
        # Update temperature
        if temp_max != '--' and temp_min != '--':
            self.temp_label.config(text=f"{temp_max}°C / {temp_min}°C")
        else:
            self.temp_label.config(text="--°C")
        
        # Update additional info
        self.humidity_label.config(text=f"💧 {humidity}%" if humidity != '--' else "💧 --%")
        self.wind_label.config(text=f"💨 {wind} km/h" if wind != '--' else "💨 -- km/h")
        self.city_label.config(text=f"📍 {city}" if city != '--' else "📍 --")

class ModularDashboard:
    """Main modular dashboard manager"""
    
    def __init__(self, parent, config_file: str = "dashboard_layout.json"):
        self.parent = parent
        self.config_file = config_file
        self.widgets: Dict[str, DashboardWidget] = {}
        self.widget_configs: Dict[str, WidgetConfig] = {}
        
        # Create main dashboard frame
        self.dashboard_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        self.dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control panel
        self.setup_control_panel()
        
        # Load saved layout or create default
        self.load_layout()
        
    def setup_control_panel(self):
        """Setup dashboard control panel"""
        self.control_frame = ttk.Frame(self.parent, style='Control.TFrame')
        self.control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Label(
            self.control_frame,
            text="Dashboard Layout:",
            style='PanelHeading.TLabel'
        ).pack(side="left", padx=(0, 10))
        
        ttk.Button(
            self.control_frame,
            text="Add Widget",
            command=self.show_add_widget_dialog,
            style='Accent.TButton'
        ).pack(side="left", padx=2)
        
        ttk.Button(
            self.control_frame,
            text="Reset Layout",
            command=self.reset_layout
        ).pack(side="left", padx=2)
        
        ttk.Button(
            self.control_frame,
            text="Save Layout",
            command=self.save_layout
        ).pack(side="left", padx=2)
        
        # Layout presets
        ttk.Label(
            self.control_frame,
            text="Presets:",
            style='PanelBody.TLabel'
        ).pack(side="left", padx=(20, 5))
        
        preset_combo = ttk.Combobox(
            self.control_frame,
            values=["Default", "Analytics Focus", "Goals Focus", "Minimal"],
            state="readonly",
            width=15
        )
        preset_combo.pack(side="left", padx=2)
        preset_combo.bind('<<ComboboxSelected>>', self.load_preset)
    
    def show_add_widget_dialog(self):
        """Show dialog to add new widget"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Widget")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Widget type selection
        ttk.Label(dialog, text="Widget Type:", style='PanelBody.TLabel').pack(pady=5)
        
        widget_type_var = tk.StringVar(value="stats")
        types_frame = ttk.Frame(dialog)
        types_frame.pack(pady=5)
        
        widget_types = [
            ("stats", "Statistics"),
            ("chart", "Chart"),
            ("progress", "Progress"),
            ("actions", "Quick Actions"),
            ("weather", "Weather")
        ]
        
        for value, text in widget_types:
            ttk.Radiobutton(
                types_frame,
                text=text,
                variable=widget_type_var,
                value=value
            ).pack(anchor="w")
        
        # Widget configuration
        config_frame = ttk.LabelFrame(dialog, text="Configuration", padding=10)
        config_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(config_frame, text="Title:").grid(row=0, column=0, sticky="w", pady=2)
        title_entry = ttk.Entry(config_frame, width=30)
        title_entry.grid(row=0, column=1, pady=2, padx=(5, 0))
        
        ttk.Label(config_frame, text="Width:").grid(row=1, column=0, sticky="w", pady=2)
        width_entry = ttk.Entry(config_frame, width=10)
        width_entry.insert(0, "200")
        width_entry.grid(row=1, column=1, pady=2, padx=(5, 0), sticky="w")
        
        ttk.Label(config_frame, text="Height:").grid(row=2, column=0, sticky="w", pady=2)
        height_entry = ttk.Entry(config_frame, width=10)
        height_entry.insert(0, "150")
        height_entry.grid(row=2, column=1, pady=2, padx=(5, 0), sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def add_widget():
            config = WidgetConfig(
                id=f"widget_{len(self.widgets)}",
                title=title_entry.get() or "New Widget",
                x=50,
                y=50,
                width=int(width_entry.get() or 200),
                height=int(height_entry.get() or 150),
                widget_type=widget_type_var.get()
            )
            self.create_widget(config)
            dialog.destroy()
        
        ttk.Button(button_frame, text="Add", command=add_widget, style='Accent.TButton').pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
    
    def create_widget(self, config: WidgetConfig):
        """Create a new dashboard widget"""
        widget_classes = {
            'stats': StatsWidget,
            'chart': ChartWidget,
            'progress': ProgressWidget,
            'actions': QuickActionWidget,
            'weather': WeatherWidget
        }
        
        widget_class = widget_classes.get(config.widget_type, StatsWidget)
        widget = widget_class(self.dashboard_frame, config)
        
        self.widgets[config.id] = widget
        self.widget_configs[config.id] = config
        
        # Add context menu for widget management
        self.add_widget_context_menu(widget)
        
        return widget
    
    def add_widget_context_menu(self, widget: DashboardWidget):
        """Add right-click context menu to widget"""
        def show_context_menu(event):
            context_menu = tk.Menu(self.parent, tearoff=0)
            context_menu.add_command(
                label="Configure",
                command=lambda: self.configure_widget(widget.config.id)
            )
            context_menu.add_command(
                label="Remove",
                command=lambda: self.remove_widget(widget.config.id)
            )
            context_menu.tk_popup(event.x_root, event.y_root)
        
        widget.frame.bind("<Button-3>", show_context_menu)
    
    def configure_widget(self, widget_id: str):
        """Configure widget properties"""
        # Implementation for widget configuration dialog
        pass
    
    def remove_widget(self, widget_id: str):
        """Remove widget from dashboard"""
        if widget_id in self.widgets:
            self.widgets[widget_id].frame.destroy()
            del self.widgets[widget_id]
            del self.widget_configs[widget_id]
    
    def load_layout(self):
        """Load dashboard layout from file"""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                
            for widget_data in data.get('widgets', []):
                config = WidgetConfig(**widget_data)
                self.create_widget(config)
                
        except (FileNotFoundError, json.JSONDecodeError):
            # Create default layout
            self.create_default_layout()
    
    def create_default_layout(self):
        """Create default dashboard layout"""
        default_widgets = [
            WidgetConfig("hydration", "Hydration", 20, 20, 200, 150, True, "stats", {"unit": "ml"}),
            WidgetConfig("steps", "Steps", 240, 20, 200, 150, True, "stats", {"unit": "steps"}),
            WidgetConfig("sleep", "Sleep", 460, 20, 200, 150, True, "stats", {"unit": "hours"}),
            WidgetConfig("trend", "Weekly Trend", 20, 190, 420, 120, True, "chart"),
            WidgetConfig("goals", "Daily Goals", 460, 190, 200, 120, True, "progress"),
        ]
        
        for config in default_widgets:
            self.create_widget(config)
    
    def save_layout(self):
        """Save current dashboard layout"""
        data = {
            'widgets': [asdict(config) for config in self.widget_configs.values()]
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save layout: {e}")
    
    def reset_layout(self):
        """Reset dashboard to default layout"""
        # Clear current widgets
        for widget in self.widgets.values():
            widget.frame.destroy()
        
        self.widgets.clear()
        self.widget_configs.clear()
        
        # Create default layout
        self.create_default_layout()
    
    def load_preset(self, event):
        """Load preset dashboard layout"""
        # Implementation for different layout presets
        pass
    
    def update_all_widgets(self, data: Dict[str, dict]):
        """Update all widgets with new data"""
        for widget_id, widget in self.widgets.items():
            if widget_id in data:
                widget.update_content(data[widget_id])


def setup_dashboard_styles(style: ttk.Style):
    """Setup styles for dashboard widgets"""
    style.configure(
        'Dashboard.TFrame',
        background='#f8f9fa',
        relief='sunken',
        borderwidth=1
    )
    
    style.configure(
        'Control.TFrame',
        background='#ffffff',
        relief='raised',
        borderwidth=1
    )
    
    style.configure(
        'Card.TLabelFrame',
        background='#ffffff',
        relief='raised',
        borderwidth=1
    )
    
    style.configure(
        'Value.TLabel',
        background='#ffffff',
        foreground='#1f2937',
        font=('TkDefaultFont', 20, 'bold')
    )
    
    style.configure(
        'Unit.TLabel',
        background='#ffffff',
        foreground='#6b7280',
        font=('TkDefaultFont', 10)
    )
    
    style.configure(
        'Trend.TLabel',
        background='#ffffff',
        foreground='#059669',
        font=('TkDefaultFont', 9)
    )
    
    style.configure(
        'Goal.TLabel',
        background='#ffffff',
        foreground='#6b7280',
        font=('TkDefaultFont', 9)
    )
    
    style.configure(
        'Compact.TButton',
        padding=(5, 2)
    )
