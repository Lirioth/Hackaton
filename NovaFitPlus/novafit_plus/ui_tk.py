import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from typing import Optional, List
import datetime as _dt
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .utils import load_config, today_iso
from .ui_enhancements import (
    ToolTip, NotificationToast, SmartEntry, DatePicker, 
    KeyboardShortcuts, setup_error_style, show_toast, add_tooltip,
    # Advanced components
    AutoRefreshManager, TrendCard, SmartNotificationCenter, SmartNotificationToast,
    BreadcrumbNavigation, ProgressRing, StatusBar, InteractiveChart,
    # Utility functions
    show_smart_toast, create_trend_card, create_progress_ring, 
    setup_auto_refresh, create_modern_button, create_info_panel
)
from .db import get_user, daily_water_total, add_water_intake, weather_on_date, insert_weather, upsert_activity, upsert_user, tail
from .db import migrate_schema, sleep_on_date, get_conn, reset_to_default, get_data_summary, steps_on_date, get_all_users
from .profile import bmi, bmr_mifflin, maintenance_calories
from .hydration import daily_water_goal_ml
from . import weather as wz
from .analysis import kpis, best_running_days, hydration_adherence, sleep_stats, health_score
from .export import export_json, export_excel, export_csv
from .reports import chart_hydration, chart_steps_vs_sleep, chart_sleep_vs_goal, save_report_figures
from .demo_data import DemoDataGenerator, populate_demo_data
from .modular_dashboard import ModularDashboard, setup_dashboard_styles
from .gamification import GamificationEngine, GamificationWidget, setup_gamification_styles
from .adaptive_theme import AdaptiveThemeManager, ThemeControlWidget, setup_adaptive_theme_styles


def steps_on_date(db_path: str, user_name: str, date_str: str) -> Optional[int]:
    """Get steps for a specific user and date"""
    try:
        with get_conn(db_path) as c:
            cur = c.cursor()
            cur.execute(
                '''SELECT steps FROM activities a JOIN users u ON a.user_id=u.id
                   WHERE u.name=? AND a.date=?''', (user_name, date_str)
            )
            result = cur.fetchone()
            return result[0] if result and result[0] else None
    except:
        return None


def _default_profile(name: str):
    return (None, name, 30, "M", 166, 66, "light", "", "")

def _ensure(db):
    migrate_schema(db)

def dashboard_text(db, user):
    u = get_user(db, user) or _default_profile(user)
    _, name, age, sex, h, w, al, city, country = u
    b, cat = bmi(w, h)
    bmr = bmr_mifflin(age, sex, h, w)
    maint = maintenance_calories(bmr, al)
    total = daily_water_total(db, user, today_iso())
    goal = daily_water_goal_ml(w, today_iso(), db, user)
    wrow = weather_on_date(db, today_iso(), user)
    sleep = sleep_on_date(db, user, today_iso())
    w7 = sleep_stats(db, user, days=7)
    w30 = sleep_stats(db, user, days=30)
    hs = health_score(db, user, w, h, days=7)

    lines = [
        f"👤 User: {name} | 🎂 Age: {age} | ⚧ Sex: {sex} | 🏃 Activity: {al}",
        (f"📍 Location: {', '.join([part for part in (city, country) if part])}" if (city or country) else "📍 Location: not set"),
        f"📏 Height: {h} cm | ⚖️ Weight: {w} kg | 📊 BMI: {b} ({cat})",
        f"🔥 BMR: {bmr} kcal | 🍽️ Maintenance: {maint} kcal",
        f"💧 Hydration: {total}/{goal} ml",
        f"😴 Sleep today: {sleep} h",
        f"📊 Weekly sleep vs 8h: {w7['percent_vs_8h']}% | Monthly: {w30['percent_vs_8h']}%",
        f"❤️ Health Score (7d): {hs['score']} / 100",
    ]
    if wrow:
        tmax, tmin, hum, wind, cond_code, city = wrow
        # Use weather display with emoji - with error handling
        try:
            weather_display = wz.get_weather_display(cond_code) if hasattr(wz, 'get_weather_display') else f"🌡️ {wz.code_to_text(cond_code)}"
        except Exception:
            weather_display = f"🌡️ {cond_code}"  # Fallback to just showing the code/text
        lines.append(f"🌤️ Today's weather [{city}]: 🌡️ max {tmax}°C, min {tmin}°C, 💧 humidity {hum}%, 💨 wind {wind} km/h, {weather_display}")
    else:
        lines.append("🌤️ Today's weather: not found.")
    return "\n".join(lines), total, goal

def main(config_path: Optional[str] = None):
    cfg = load_config(config_path)
    db = cfg["db_path"]
    _ensure(db)
    default_user = "Kevin"
    profile_defaults = get_user(db, default_user) or _default_profile(default_user)
    (
        _,
        init_name,
        init_age,
        init_sex,
        init_h,
        init_w,
        init_al,
        init_city,
        init_country,
    ) = profile_defaults

    root = tk.Tk()
    root.title("NovaFit Plus — GUI")
    root.geometry("1100x760")
    root.minsize(980, 660)
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass
    
    # Setup error styling for enhanced widgets
    setup_error_style(style)
    base_font = tkfont.nametofont('TkDefaultFont')
    base_font.configure(size=10)
    title_font = tkfont.Font(family=base_font.actual('family'), size=12, weight='bold')
    subtitle_font = tkfont.Font(family=base_font.actual('family'), size=11)
    metric_font = tkfont.Font(family=base_font.actual('family'), size=18, weight='bold')

    theme_colors = {
        'light': {
            'bg': '#f4f6fb',
            'fg': '#1f2933',
            'muted': '#52606d',
            'accent': '#3b82f6',
            'panel_bg': '#ffffff',
            'card_bg': '#ffffff',
            'health': '#10b981',
            'sleep': '#8b5cf6',
            'status_bg': '#e5e7eb',
            'cards': {
                'hydration': {
                    'bg': '#ffffff',
                    'accent': '#3b82f6',
                    'title_fg': '#52606d',
                    'value_fg': '#1d4ed8',
                    'icon_fg': '#1d4ed8'
                },
                'sleep': {
                    'bg': '#ffffff',
                    'accent': '#8b5cf6',
                    'title_fg': '#52606d',
                    'value_fg': '#6d28d9',
                    'icon_fg': '#6d28d9'
                },
                'health': {
                    'bg': '#ffffff',
                    'accent': '#10b981',
                    'title_fg': '#52606d',
                    'value_fg': '#047857',
                    'icon_fg': '#047857'
                },
                'steps': {
                    'bg': '#ffffff',
                    'accent': '#f59e0b',
                    'title_fg': '#52606d',
                    'value_fg': '#b45309',
                    'icon_fg': '#b45309'
                },
                'calories': {
                    'bg': '#ffffff',
                    'accent': '#ef4444',
                    'title_fg': '#52606d',
                    'value_fg': '#b91c1c',
                    'icon_fg': '#b91c1c'
                }
            }
        },
        'dark': {
            'bg': '#0d1117',           # GitHub dark bg
            'fg': '#f0f6fc',           # GitHub dark text
            'muted': '#7d8590',        # GitHub muted text
            'accent': '#58a6ff',       # GitHub blue
            'panel_bg': '#161b22',     # GitHub panel bg
            'card_bg': '#21262d',      # GitHub card bg
            'health': '#3fb950',       # GitHub green
            'sleep': '#a5a5f8',        # Soft purple
            'status_bg': '#21262d',    # GitHub status bg
            'cards': {
                'hydration': {
                    'bg': '#1c2128',
                    'accent': '#58a6ff',
                    'title_fg': '#8b949e',
                    'value_fg': '#58a6ff',
                    'icon_fg': '#79c0ff'
                },
                'sleep': {
                    'bg': '#1c2128', 
                    'accent': '#a5a5f8',
                    'title_fg': '#8b949e',
                    'value_fg': '#a5a5f8',
                    'icon_fg': '#d2a8ff'
                },
                'health': {
                    'bg': '#1c2128',
                    'accent': '#3fb950', 
                    'title_fg': '#8b949e',
                    'value_fg': '#3fb950',
                    'icon_fg': '#56d364'
                },
                'steps': {
                    'bg': '#1c2128',
                    'accent': '#f2cc60',
                    'title_fg': '#8b949e', 
                    'value_fg': '#f2cc60',
                    'icon_fg': '#ffeb3b'
                },
                'calories': {
                    'bg': '#1c2128',
                    'accent': '#ff7b72',
                    'title_fg': '#8b949e',
                    'value_fg': '#ff7b72', 
                    'icon_fg': '#ff9492'
                }
            }
        }
    }
    text_widgets = []
    status_widgets = []
    gauge_widgets = {}
    theme_state = {'mode': 'light'}
    card_elements = []

    def apply_theme(mode: str = 'light'):
        theme_state['mode'] = mode if mode in theme_colors else 'light'
        palette = theme_colors.get(theme_state['mode'], theme_colors['light'])
        root.configure(bg=palette['bg'])
        style.configure('.', background=palette['bg'], foreground=palette['fg'])
        style.configure('TFrame', background=palette['bg'])
        style.configure('Header.TFrame', background=palette['bg'])
        style.configure('Panel.TFrame', background=palette['panel_bg'])
        style.configure('Header.TLabel', background=palette['bg'], foreground=palette['fg'], font=tkfont.Font(family=base_font.actual('family'), size=16, weight='bold'))
        style.configure('Subtitle.TLabel', background=palette['bg'], foreground=palette['muted'], font=subtitle_font)
        style.configure('Card.TFrame', background=palette['card_bg'])
        style.configure('CardTitle.TLabel', background=palette['card_bg'], foreground=palette['muted'], font=subtitle_font)
        style.configure('CardValue.TLabel', background=palette['card_bg'], foreground=palette['accent'], font=metric_font)
        card_palettes = palette.get('cards', {})
        for card_key, card_palette in card_palettes.items():
            style_prefix = card_key.capitalize()
            card_bg = card_palette.get('bg', palette['card_bg'])
            title_fg = card_palette.get('title_fg', palette['muted'])
            value_fg = card_palette.get('value_fg', palette['accent'])
            icon_fg = card_palette.get('icon_fg', value_fg)
            style.configure(f'{style_prefix}Card.TFrame', background=card_bg)
            style.configure(f'{style_prefix}CardBody.TFrame', background=card_bg)
            style.configure(f'{style_prefix}Title.TLabel', background=card_bg, foreground=title_fg, font=subtitle_font)
            style.configure(f'{style_prefix}Value.TLabel', background=card_bg, foreground=value_fg, font=metric_font)
            style.configure(f'{style_prefix}Icon.TLabel', background=card_bg, foreground=icon_fg, font=title_font)
        for card in card_elements:
            card_palette = card_palettes.get(card['key'], {})
            accent_color = card_palette.get('accent', palette['accent'])
            card['accent'].configure(bg=accent_color)
        style.configure('PanelHeading.TLabel', background=palette['panel_bg'], foreground=palette['fg'], font=title_font)
        style.configure('PanelBody.TLabel', background=palette['panel_bg'], foreground=palette['muted'])
        style.configure('Accent.TButton', background=palette['accent'], foreground='#ffffff')
        style.map('Accent.TButton', background=[('active', palette['accent'])], foreground=[('disabled', palette['muted'])])
        style.configure('Accent.Horizontal.TProgressbar', troughcolor=palette['panel_bg'], background=palette['accent'])
        style.configure('Health.Horizontal.TProgressbar', troughcolor=palette['panel_bg'], background=palette['health'])
        style.configure('Sleep.Horizontal.TProgressbar', troughcolor=palette['panel_bg'], background=palette['sleep'])
        style.configure('TNotebook', background=palette['panel_bg'])
        style.configure('TNotebook.Tab', background=palette['bg'], foreground=palette['muted'])
        style.map('TNotebook.Tab', background=[('selected', palette['panel_bg'])], foreground=[('selected', palette['fg'])])
        
        # Card styles for advanced components
        style.configure('Card.TLabelFrame', 
                       background=palette['card_bg'], 
                       foreground=palette['fg'],
                       relief='raised',
                       borderwidth=1)
        
        # Enhanced dark mode specific styles
        if mode == 'dark':
            style.configure('TEntry', fieldbackground=palette['card_bg'], foreground=palette['fg'], 
                          bordercolor=palette['muted'], insertcolor=palette['fg'])
            style.configure('TCombobox', fieldbackground=palette['card_bg'], foreground=palette['fg'])
            style.configure('TFrame', background=palette['panel_bg'])
            style.configure('TLabelFrame', background=palette['panel_bg'], foreground=palette['fg'])
            style.configure('TCheckbutton', background=palette['panel_bg'], foreground=palette['fg'])
            style.configure('TRadiobutton', background=palette['panel_bg'], foreground=palette['fg'])
        else:
            # Light mode defaults
            style.configure('TEntry', fieldbackground='#ffffff', foreground='#000000')
            style.configure('TCombobox', fieldbackground='#ffffff', foreground='#000000')
            style.configure('TFrame', background=palette['panel_bg'])
            style.configure('TLabelFrame', background=palette['panel_bg'], foreground=palette['fg'])
        
        for txt in text_widgets:
            txt.configure(bg=palette['panel_bg'], fg=palette['fg'], insertbackground=palette['fg'])
        # StatusBar widgets use ttk styling, so we skip the direct bg/fg configuration
        # They should respond to the theme changes through ttk styles
        for gauge_key, gauge in gauge_widgets.items():
            canvas = gauge['canvas']
            canvas.configure(bg=palette['panel_bg'], highlightbackground=palette['panel_bg'])
            canvas.itemconfig(gauge['bg'], outline=palette['status_bg'])
            canvas.itemconfig(
                gauge['arc'],
                outline=palette.get(gauge['palette_key'], palette['accent'])
            )
            canvas.itemconfig(gauge['text'], fill=palette['fg'])

    def switch_theme():
        apply_theme('dark' if theme_state['mode'] == 'light' else 'light')

    def resolve_date_value(raw: Optional[str]) -> str:
        candidate = (raw or "").strip() or today_iso()
        try:
            return _dt.date.fromisoformat(candidate).isoformat()
        except ValueError as exc:
            raise ValueError("Invalid date. Please use YYYY-MM-DD.") from exc

    subtitle_var = tk.StringVar(value="Personal wellness snapshot at a glance.")
    hydration_summary_var = tk.StringVar(value="--")
    sleep_summary_var = tk.StringVar(value="--")
    score_summary_var = tk.StringVar(value="--")
    steps_summary_var = tk.StringVar(value="--")
    calories_summary_var = tk.StringVar(value="--")
    today_summary_var = tk.StringVar(value="Stay consistent with your habits today.")
    hydration_tip_var = tk.StringVar(value="Log your first glass of water.")
    sleep_tip_var = tk.StringVar(value="Aim for restful sleep tonight.")
    weather_tip_var = tk.StringVar(value="Save today's weather for tailored tips.")
    score_breakdown_var = tk.StringVar(value="Health score insights appear here once data is available.")
    status_var = tk.StringVar(value="Ready.")
    user_var = tk.StringVar(value=init_name or default_user)

    # Setup keyboard shortcuts
    shortcuts = KeyboardShortcuts(root)
    
    # Setup auto-refresh system
    auto_refresh = AutoRefreshManager(root)
    
    # Setup smart notifications
    notification_center = SmartNotificationCenter(root)

    main_container = ttk.Frame(root, padding=(16, 14), style='Header.TFrame')
    main_container.pack(fill="both", expand=True)

    # Add breadcrumb navigation
    breadcrumb = BreadcrumbNavigation(main_container)
    breadcrumb.pack(fill="x", pady=(0, 8))
    breadcrumb.update_path(["NovaFit Plus", "Dashboard"])

    header_frame = ttk.Frame(main_container, style='Header.TFrame')
    header_frame.pack(fill="x")
    header_frame.columnconfigure(0, weight=1)
    header_title = ttk.Label(header_frame, text="NovaFit Plus Wellness Hub", style='Header.TLabel')
    header_title.grid(row=0, column=0, sticky="w")
    subtitle_label = ttk.Label(header_frame, textvariable=subtitle_var, style='Subtitle.TLabel')
    subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))
    header_buttons = ttk.Frame(header_frame, style='Header.TFrame')
    header_buttons.grid(row=0, column=1, rowspan=2, sticky="e", padx=(12, 0))

    cards_frame = ttk.Frame(main_container, style='Header.TFrame')
    cards_frame.pack(fill="x", pady=(12, 8))
    cards_frame.rowconfigure(0, weight=1)
    for idx in range(5):
        cards_frame.columnconfigure(idx, weight=1)

    def create_enhanced_stat_card(column: int, card_key: str, title_text: str, var: tk.StringVar, icon_text: str):
        """Create an enhanced stat card with trend visualization"""
        color_mapping = {
            "hydration": "#3b82f6",
            "sleep": "#8b5cf6", 
            "health": "#10b981",
            "steps": "#f59e0b",
            "calories": "#ef4444"
        }
        
        card = TrendCard(
            cards_frame, 
            title_text, 
            icon_text, 
            color_mapping.get(card_key, "#3b82f6"),
            padding=(12, 10)
        )
        card.grid(row=0, column=column, sticky="nsew", padx=6, pady=4)
        
        # Store reference for updates
        card.value_var = var
        card.card_key = card_key
        
        return card

    cards_config = [
        ("hydration", "Hydration Today", hydration_summary_var, "💧"),
        ("sleep", "Sleep vs Target", sleep_summary_var, "🌙"),
        ("health", "Health Score", score_summary_var, "💚"),
        ("steps", "7-day Steps", steps_summary_var, "👟"),
        ("calories", "Avg Calories", calories_summary_var, "🔥"),
    ]
    
    # Tooltip messages for each card
    card_tooltips = {
        "hydration": "Track your daily water intake vs. personalized goal based on weight, activity and weather",
        "sleep": "Compare your sleep duration against the recommended 8 hours target",
        "health": "Composite score combining steps, hydration, sleep quality and mood over 7 days",
        "steps": "7-day rolling average of your daily step count",
        "calories": "Average daily calorie burn from logged activities"
    }
    
    # Store enhanced cards for updates
    enhanced_cards = {}
    
    for idx, (key, title, var, icon) in enumerate(cards_config):
        card = create_enhanced_stat_card(idx, key, title, var, icon)
        enhanced_cards[key] = card
        # Add tooltip to the card
        if key in card_tooltips:
            add_tooltip(card, card_tooltips[key])

    ttk.Separator(main_container, orient='horizontal').pack(fill="x", pady=(4, 12))

    nb = ttk.Notebook(main_container)
    nb.pack(fill="both", expand=True)

    tab_dash = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_dash, text="Dashboard")
    top_dash = ttk.Frame(tab_dash, style='Panel.TFrame')
    top_dash.pack(fill="x")
    ttk.Label(top_dash, text="User:", style='PanelHeading.TLabel').pack(side="left")
    
    # User selector with dropdown
    def update_user_list():
        """Update the user selector with available users"""
        try:
            users = get_all_users(db)
            current_value = user_var.get()
            user_selector['values'] = users
            
            # If current value is not in the list, add it
            if current_value and current_value not in users:
                user_selector['values'] = [current_value] + users
        except Exception:
            user_selector['values'] = [user_var.get() or default_user]
    
    def on_user_change(event=None):
        """Handle user selection change"""
        new_user = user_selector.get().strip()
        if new_user:
            user_var.set(new_user)
            refresh_dashboard()
            generate_insights()
            # Update gamification if available
            try:
                if 'gamification_engine' in locals():
                    gamification_engine.user_name = new_user
                    if hasattr(gamification_widget, 'update_display'):
                        gamification_widget.update_display()
            except:
                pass
    
    user_selector = ttk.Combobox(top_dash, textvariable=user_var, width=18)
    user_selector.pack(side="left", padx=6)
    user_selector.bind('<<ComboboxSelected>>', on_user_change)
    user_selector.bind('<Return>', on_user_change)
    
    # Refresh button for user list
    ttk.Button(top_dash, text="🔄", width=3, 
              command=update_user_list).pack(side="left", padx=2)
    add_tooltip(top_dash.winfo_children()[-1], "Refresh user list")
    
    # Initial user list update
    update_user_list()

    dash_split = ttk.Panedwindow(tab_dash, orient='horizontal')
    dash_split.pack(fill="both", expand=True, pady=10)

    dash_text_frame = ttk.Frame(dash_split, style='Panel.TFrame')
    dash_text = tk.Text(dash_text_frame, width=80, height=16, wrap="word", relief='flat', bd=0)
    dash_text.pack(fill="both", expand=True)
    text_widgets.append(dash_text)
    dash_split.add(dash_text_frame, weight=3)

    insight_panel = ttk.Frame(dash_split, style='Panel.TFrame', padding=(12, 10))
    ttk.Label(insight_panel, text="Daily Focus", style='PanelHeading.TLabel').pack(anchor='w')
    ttk.Label(insight_panel, textvariable=today_summary_var, style='PanelBody.TLabel', wraplength=240, justify='left').pack(anchor='w', pady=(4, 6))
    ttk.Separator(insight_panel, orient='horizontal').pack(fill='x', pady=6)
    ttk.Label(insight_panel, text="Hydration", style='PanelHeading.TLabel').pack(anchor='w')
    ttk.Label(insight_panel, textvariable=hydration_tip_var, style='PanelBody.TLabel', wraplength=240, justify='left').pack(anchor='w', pady=(2, 6))
    ttk.Label(insight_panel, text="Sleep", style='PanelHeading.TLabel').pack(anchor='w')
    ttk.Label(insight_panel, textvariable=sleep_tip_var, style='PanelBody.TLabel', wraplength=240, justify='left').pack(anchor='w', pady=(2, 6))
    ttk.Label(insight_panel, text="Weather", style='PanelHeading.TLabel').pack(anchor='w')
    ttk.Label(insight_panel, textvariable=weather_tip_var, style='PanelBody.TLabel', wraplength=240, justify='left').pack(anchor='w', pady=(2, 6))
    ttk.Label(insight_panel, text="Health Score Components", style='PanelHeading.TLabel').pack(anchor='w')
    ttk.Label(insight_panel, textvariable=score_breakdown_var, style='PanelBody.TLabel', wraplength=240, justify='left').pack(anchor='w', pady=(2, 0))
    dash_split.add(insight_panel, weight=2)

    metrics_frame = ttk.Frame(tab_dash, style='Panel.TFrame')
    metrics_frame.pack(fill="x", pady=4)
    def _create_gauge_row(frame: ttk.Frame, title: str, key: str, palette_key: str, maximum: int, initial: str):
        row = ttk.Frame(frame, style='Panel.TFrame')
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=title, style='PanelHeading.TLabel').pack(side="left", padx=6)
        canvas = tk.Canvas(row, width=96, height=96, highlightthickness=0, bd=0)
        canvas.pack(side="left", padx=6, pady=4)
        bbox = (8, 8, 88, 88)
        bg_ring = canvas.create_oval(*bbox, width=10, outline="#d1d5db")
        arc = canvas.create_arc(*bbox, start=90, extent=0, width=10, style='arc', outline="#3b82f6")
        text_item = canvas.create_text(48, 48, text=initial, font=metric_font, fill="#1f2933")
        value_label = ttk.Label(row, text=initial, style='PanelBody.TLabel')
        value_label.pack(side="left", padx=6)
        gauge_widgets[key] = {
            'canvas': canvas,
            'arc': arc,
            'text': text_item,
            'bg': bg_ring,
            'label': value_label,
            'max': maximum,
            'palette_key': palette_key,
        }

    _create_gauge_row(metrics_frame, "Hydration % (today)", 'hydration', 'accent', 100, "0%")
    _create_gauge_row(metrics_frame, "Weekly Sleep % (vs 8h)", 'sleep', 'sleep', 120, "0%")
    _create_gauge_row(metrics_frame, "Health Score (7d)", 'health', 'health', 100, "--")

    def update_gauge(key: str, value: float, display_text: str, label_text: Optional[str] = None):
        gauge = gauge_widgets.get(key)
        if not gauge:
            return
        max_value = gauge.get('max', 100) or 100
        clamped = max(0, min(value, max_value))
        extent = -360 * (clamped / max_value)
        gauge['canvas'].itemconfig(gauge['arc'], extent=extent)
        gauge['canvas'].itemconfig(gauge['text'], text=display_text)
        gauge['label'].config(text=label_text or display_text)

    btns = ttk.Frame(tab_dash, style='Panel.TFrame')
    btns.pack(fill="x", pady=6)
    
    # Quick water buttons with tooltips
    water_btn_250 = ttk.Button(btns, text="Water +250 ml", style='Accent.TButton', 
                              command=lambda: quick_add_enhanced(250))
    water_btn_250.pack(side="left", padx=4)
    add_tooltip(water_btn_250, "Add a standard glass of water (250ml)")
    
    water_btn_500 = ttk.Button(btns, text="Water +500 ml", style='Accent.TButton', 
                              command=lambda: quick_add_enhanced(500))
    water_btn_500.pack(side="left", padx=4)
    add_tooltip(water_btn_500, "Add a standard water bottle (500ml)")
    
    weather_btn = ttk.Button(
        btns,
        text="Fetch Today's Weather",
        command=lambda: fetch_today_weather(
            db,
            cfg,
            user_var.get().strip() or default_user,
            refresh_dashboard,
        ),
    )
    weather_btn.pack(side="right", padx=4)
    add_tooltip(weather_btn, "Get current weather data for personalized hydration goals")

    def get_hydration_trend(db_path: str, user_name: str, days: int = 7) -> List[float]:
        """Get hydration percentage trend for the last N days"""
        try:
            u = get_user(db_path, user_name) or _default_profile(user_name)
            weight_kg = u[5] if u[5] else 70  # Default weight
            
            trend_data = []
            for i in range(days):
                date_str = (_dt.date.today() - _dt.timedelta(days=days-1-i)).isoformat()
                goal = daily_water_goal_ml(weight_kg, date_str, db_path, user_name)
                actual = daily_water_total(db_path, user_name, date_str)
                pct = (actual / goal * 100) if goal > 0 else 0
                trend_data.append(min(100, pct))
            
            return trend_data
        except:
            return [0] * days
    
    def get_sleep_trend(db_path: str, user_name: str, days: int = 7) -> List[float]:
        """Get sleep hours trend for the last N days"""
        try:
            trend_data = []
            for i in range(days):
                date_str = (_dt.date.today() - _dt.timedelta(days=days-1-i)).isoformat()
                sleep_hours = sleep_on_date(db_path, user_name, date_str) or 0
                trend_data.append(sleep_hours)
            
            return trend_data
        except:
            return [0] * days
    
    def get_health_trend(db_path: str, user_name: str, weight_kg: float, height_cm: float, days: int = 7) -> List[float]:
        """Get health score trend for the last N days"""
        try:
            trend_data = []
            for i in range(days):
                # Calculate health score for each day looking back 7 days from that point
                end_date = _dt.date.today() - _dt.timedelta(days=days-1-i)
                hs = health_score(db_path, user_name, weight_kg, height_cm, days=7)
                score = hs.get('score', 0) if isinstance(hs, dict) else 0
                trend_data.append(score)
            
            return trend_data
        except:
            return [0] * days
    
    def get_steps_trend(db_path: str, user_name: str, days: int = 7) -> List[float]:
        """Get daily steps trend for the last N days"""
        try:
            trend_data = []
            for i in range(days):
                date_str = (_dt.date.today() - _dt.timedelta(days=days-1-i)).isoformat()
                steps = steps_on_date(db_path, user_name, date_str) or 0
                trend_data.append(float(steps))
            
            return trend_data
        except:
            return [0] * days
    
    def get_calories_trend(db_path: str, user_name: str, days: int = 7) -> List[float]:
        """Get daily calories trend for the last N days"""
        try:
            with get_conn(db_path) as c:
                cur = c.cursor()
                trend_data = []
                for i in range(days):
                    date_str = (_dt.date.today() - _dt.timedelta(days=days-1-i)).isoformat()
                    cur.execute(
                        '''SELECT calories FROM activities a JOIN users u ON a.user_id=u.id
                           WHERE u.name=? AND a.date=?''', (user_name, date_str)
                    )
                    result = cur.fetchone()
                    calories = result[0] if result and result[0] else 0
                    trend_data.append(float(calories))
                
                return trend_data
        except:
            return [0] * days

    def refresh_dashboard():
        user_name = user_var.get().strip() or default_user
        text, total, goal = dashboard_text(db, user_name)
        dash_text.delete("1.0", tk.END)
        dash_text.insert(tk.END, text)
        
        # Update hydration card with trend
        pct = 0 if goal <= 0 else int(total * 100 / goal)
        update_gauge('hydration', pct, f"{pct}%")
        hydration_summary_var.set(
            f"💧 {pct}% • {total} ml / {goal} ml" if goal > 0 else f"💧 {total} ml logged"
        )
        
        # Get historical hydration data for trend
        hydration_trend = get_hydration_trend(db, user_name, days=7)
        if 'hydration' in enhanced_cards:
            enhanced_cards['hydration'].update_data(
                hydration_trend, 
                f"{pct}%",
                "↗ +5%" if len(hydration_trend) > 1 and hydration_trend[-1] > hydration_trend[-2] else "→ Stable",
                f"{total}/{goal} ml today"
            )
        
        if goal > 0 and total < goal:
            hydration_tip_var.set(f"💧 Drink {goal - total} ml more to meet today's goal!")
        elif goal > 0:
            hydration_tip_var.set("🎉 Hydration goal achieved — amazing!")
        else:
            hydration_tip_var.set("🎯 Set a water goal in your profile to unlock guidance.")

        # Update sleep card with trend
        w7 = sleep_stats(db, user_name, days=7)
        sleep_pct = int(w7["percent_vs_8h"]) if w7 else 0
        update_gauge('sleep', sleep_pct, f"{sleep_pct}%")
        avg_sleep = w7.get("avg_hours", 0) if w7 else 0
        sleep_summary_var.set(f"😴 {sleep_pct}% • avg {avg_sleep}h vs 8h")
        
        # Get sleep trend data
        sleep_trend = get_sleep_trend(db, user_name, days=7)
        if 'sleep' in enhanced_cards:
            trend_indicator = "↗ Improving" if len(sleep_trend) > 1 and sleep_trend[-1] > sleep_trend[-2] else "→ Stable"
            enhanced_cards['sleep'].update_data(
                sleep_trend,
                f"{sleep_pct}%",
                trend_indicator,
                f"avg {avg_sleep}h vs 8h target"
            )
        
        if sleep_pct >= 100:
            sleep_tip_var.set("✨ Great rest pattern — keep it consistent tonight!")
        elif avg_sleep:
            sleep_tip_var.set(f"😴 Add {round(max(0, 8 - avg_sleep), 1)}h nightly to reach target.")
        else:
            sleep_tip_var.set("📊 Log sleep to unlock tailored tips.")

        # Update health score card with trend
        u = get_user(db, user_name) or _default_profile(user_name)
        _, name, _, _, h, w, _, city, _ = u
        hs = health_score(db, user_name, w, h, days=7)
        score_val = int(hs.get('score', 0))
        update_gauge('health', score_val, f"{score_val}", f"{score_val} pts")
        score_summary_var.set(f"❤️ {score_val} pts / 100")
        
        # Get health score trend
        health_trend = get_health_trend(db, user_name, w, h, days=7)
        if 'health' in enhanced_cards:
            trend_indicator = "↗ Improving" if len(health_trend) > 1 and health_trend[-1] > health_trend[-2] else "→ Stable"
            enhanced_cards['health'].update_data(
                health_trend,
                f"{score_val}",
                trend_indicator,
                "7-day composite score"
            )
        
        components = hs.get('components', {})
        score_breakdown_var.set(
            " • ".join([
                f"🚶 Steps {components.get('steps_score', 0)}",
                f"💧 Hydration {components.get('hydration_score', 0)}",
                f"😴 Sleep {components.get('sleep_score', 0)}",
                f"😊 Mood {components.get('mood_score', 0)}"
            ])
        )

        # Update steps and calories cards
        kpi_data = kpis(db, user_name, 7)
        if isinstance(kpi_data, dict) and 'message' not in kpi_data:
            steps_mov = kpi_data.get('steps_movavg_7d_last') or 0
            steps_summary_var.set(f"🚶 {int(round(steps_mov)):,} avg steps")
            
            # Get steps trend
            steps_trend = get_steps_trend(db, user_name, days=7)
            if 'steps' in enhanced_cards:
                trend_indicator = "↗ Increasing" if len(steps_trend) > 1 and steps_trend[-1] > steps_trend[-2] else "→ Stable"
                enhanced_cards['steps'].update_data(
                    steps_trend,
                    f"{int(round(steps_mov)):,}",
                    trend_indicator,
                    "7-day average"
                )
            
            cal_avg = kpi_data.get('calories_avg') or 0
            calories_summary_var.set(f"🔥 {int(round(cal_avg))} kcal / day")
            
            # Get calories trend
            calories_trend = get_calories_trend(db, user_name, days=7)
            if 'calories' in enhanced_cards:
                trend_indicator = "↗ Increasing" if len(calories_trend) > 1 and calories_trend[-1] > calories_trend[-2] else "→ Stable"
                enhanced_cards['calories'].update_data(
                    calories_trend,
                    f"{int(round(cal_avg))}",
                    trend_indicator,
                    "daily average"
                )
        else:
            steps_summary_var.set("📊 Log steps to see trends")
            calories_summary_var.set("📈 Calories data pending")

        # Update weather and general info with auto-fetch if needed
        wrow = weather_on_date(db, today_iso(), user_name)
        
        # Get current user's city for weather fetching
        current_user = get_user(db, user_name) or _default_profile(user_name)
        user_city = current_user[7] if current_user and len(current_user) > 7 else ""
        
        # Auto-fetch weather if not available and city is set
        if not wrow and user_city:
            try:
                # Check if we haven't fetched weather in the last hour
                current_hour = _dt.datetime.now().hour
                last_fetch_key = f"last_weather_fetch_{user_name}"
                
                # Simple time-based check for auto-fetch
                should_fetch = True
                try:
                    with open("weather_cache.json", "r") as f:
                        cache = json.load(f)
                        last_fetch = cache.get(last_fetch_key, 0)
                        if abs(current_hour - last_fetch) < 1:  # Less than 1 hour ago
                            should_fetch = False
                except:
                    should_fetch = True
                
                if should_fetch:
                    # Auto-fetch weather silently
                    def weather_callback():
                        try:
                            with open("weather_cache.json", "w") as f:
                                cache = {}
                                try:
                                    with open("weather_cache.json", "r") as rf:
                                        cache = json.load(rf)
                                except:
                                    pass
                                cache[last_fetch_key] = current_hour
                                json.dump(cache, f)
                        except:
                            pass
                        # Refresh to show new weather data
                        root.after(1000, refresh_dashboard)
                    
                    # Fetch weather in background
                    import threading
                    weather_thread = threading.Thread(
                        target=lambda: fetch_today_weather(db, cfg, user_name, weather_callback)
                    )
                    weather_thread.daemon = True
                    weather_thread.start()
            except:
                pass  # Silent fail for auto-fetch
        
        # Update weather display with emojis
        wrow = weather_on_date(db, today_iso(), user_name)
        if wrow:
            tmax, tmin, hum, wind, cond_code, city_name = wrow
            # Convert condition code to emoji + text - with error handling
            try:
                weather_display = wz.get_weather_display(cond_code) if hasattr(wz, 'get_weather_display') else f"🌡️ {wz.code_to_text(cond_code)}"
            except Exception:
                weather_display = f"🌡️ {cond_code}"  # Fallback
            weather_tip_var.set(
                f"🏙️ {city_name}: 🌡️ {tmax}°C / {tmin}°C, 💧 {hum}%, 💨 {wind} km/h — {weather_display}"
            )
        elif user_city:
            weather_tip_var.set(f"🔄 Fetching weather for {user_city}...")
        else:
            weather_tip_var.set("📍 Add your city to profile for weather updates.")

        today_summary_var.set(f"{name}, you're {pct}% to your hydration goal today.")
        subtitle_var.set(f"{name}'s dashboard refreshed.")
        current_time = _dt.datetime.now().strftime('%H:%M:%S')
        
        # Update status bar
        status_bar.update_status("Dashboard refreshed", "success")
        status_bar.set_info(f"Last updated: {current_time}")
        
        # Update breadcrumb
        breadcrumb.update_path(["NovaFit Plus", "Dashboard"])
        
        # Analyze data for smart notifications
        dashboard_data = {
            'hydration_pct': pct,
            'steps': int(round(kpi_data.get('steps_movavg_7d_last', 0))) if isinstance(kpi_data, dict) else 0,
            'health_score': score_val,
            'sleep_hours': avg_sleep,
            'mood': 3  # Default, would need to get from recent activity
        }
        notification_center.analyze_and_notify(dashboard_data)
        
        # Update gamification if available
        if 'update_gamification' in locals():
            try:
                update_gamification()
            except:
                pass  # Gamification not yet initialized
        
        # Update modular dashboard widgets if available
        try:
            # Prepare weather data
            weather_data = {
                'condition_code': 0,
                'temp_max': '--',
                'temp_min': '--',
                'humidity': '--',
                'wind': '--',
                'city': '--'
            }
            
            if wrow:
                tmax, tmin, hum, wind, cond_code, city_name = wrow
                weather_data.update({
                    'condition_code': cond_code,
                    'temp_max': tmax,
                    'temp_min': tmin,
                    'humidity': hum,
                    'wind': wind,
                    'city': city_name
                })
            
            # Update modular dashboard widgets with sample data
            widget_data = {
                'hydration_stats': {
                    'value': pct,
                    'unit': f"{total}/{goal} ml",
                    'trend': f"↗ +5%" if pct > 50 else "→ Stable"
                },
                'health_stats': {
                    'value': score_val,
                    'unit': "pts / 100",
                    'trend': "↗ Improving" if score_val > 70 else "→ Stable"
                },
                'weather_data': weather_data
            }
            
            # This would be used by modular dashboard if it was integrated
            # For now, just store it globally for later use
            globals()['dashboard_widget_data'] = widget_data
            
        except Exception as e:
            pass  # Silent fail for widget updates
        
        # Show success toast (less frequent than before)
        if _dt.datetime.now().minute % 5 == 0:  # Only every 5 minutes
            show_toast(root, "Dashboard updated successfully!", "success", 2000)

    # 🏃 Activity tab
    tab_act = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_act, text="Activity")
    ttk.Label(tab_act, text="Daily Activity Log", style='PanelHeading.TLabel').pack(anchor='w')
    
    # Enhanced date picker
    date_picker = DatePicker(tab_act, "Activity Date")
    date_picker.pack(fill="x", pady=(8, 4))
    
    # Enhanced form fields
    act_grid = ttk.Frame(tab_act, style='Panel.TFrame')
    act_grid.pack(fill="x", pady=(8, 4))
    act_grid.columnconfigure((0, 1), weight=1)
    
    # Smart entry fields with validation and tooltips
    steps_entry = SmartEntry(
        act_grid, 
        "Steps", 
        value_type="number", 
        min_value=0, 
        max_value=100000,
        tooltip="Daily step count (0-100,000)",
        width=12
    )
    steps_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=4)
    
    cals_entry = SmartEntry(
        act_grid,
        "Calories Burned",
        value_type="number",
        min_value=0,
        max_value=10000,
        tooltip="Calories burned from activities (0-10,000)",
        width=12
    )
    cals_entry.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)
    
    mood_entry = SmartEntry(
        act_grid,
        "Mood (1-5)",
        value_type="number",
        min_value=1,
        max_value=5,
        tooltip="Rate your mood: 1=Poor, 2=Below Average, 3=Average, 4=Good, 5=Excellent",
        width=12
    )
    mood_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=4)
    mood_entry.set("3")  # Default value
    
    sleep_entry = SmartEntry(
        act_grid,
        "Sleep Hours",
        value_type="number",
        min_value=0,
        max_value=24,
        tooltip="Hours of sleep (0-24, decimals allowed: e.g., 7.5)",
        width=12
    )
    sleep_entry.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)
    
    # Notes field
    ttk.Label(tab_act, text="Notes", style='PanelHeading.TLabel').pack(anchor="w", pady=(8, 4))
    notes_var = tk.StringVar()
    notes_entry = ttk.Entry(tab_act, textvariable=notes_var, width=90)
    notes_entry.pack(fill="x")
    add_tooltip(notes_entry, "Optional notes about your day, activities, or how you felt")

    def save_activity():
        try:
            # Validate all fields first
            if not all([
                date_picker.date_entry.validate(),
                steps_entry.validate(),
                cals_entry.validate(),
                mood_entry.validate(),
                sleep_entry.validate()
            ]):
                show_toast(root, "Please fix the validation errors before saving", "error")
                return
            
            chosen_date = resolve_date_value(date_picker.get())
            steps = int(float(steps_entry.get() or 0))
            cals = int(float(cals_entry.get() or 0))
            mood = int(float(mood_entry.get() or 3))
            mood = max(1, min(5, mood))  # Ensure mood is in valid range
            sleep = float(sleep_entry.get() or 0.0)
            
            upsert_activity(db, user_var.get().strip() or default_user, chosen_date, steps, cals, mood, notes_var.get().strip(), sleep)
            show_toast(root, f"Activity saved for {chosen_date}", "success")
            refresh_dashboard()
        except ValueError as err:
            show_toast(root, f"Invalid date: {str(err)}", "error")
        except Exception as e:
            show_toast(root, f"Error saving activity: {str(e)}", "error")
    ttk.Button(tab_act, text="Save Activity", style='Accent.TButton', command=save_activity).pack(pady=10, anchor='e')

    # 💧 Water tab
    tab_water = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_water, text="Water")
    ttk.Label(tab_water, text="Daily Hydration Helper", style='PanelHeading.TLabel').pack(anchor='w')
    
    # Enhanced date picker for water
    water_date_picker = DatePicker(tab_water, "Water Intake Date")
    water_date_picker.pack(fill="x", pady=(8, 12))
    
    # Quick add section with tooltips
    quick_frame = ttk.LabelFrame(tab_water, text="Quick Add", padding=10)
    quick_frame.pack(fill="x", pady=(0, 12))
    
    ttk.Label(quick_frame, text="Common serving sizes:", style='PanelBody.TLabel').pack(anchor="w", pady=(0, 4))
    wbtns = ttk.Frame(quick_frame, style='Panel.TFrame')
    wbtns.pack(anchor="w", pady=4)
    
    water_amounts = [
        (250, "Glass", "Standard water glass"),
        (500, "Bottle", "Standard water bottle"),
        (750, "Large", "Large water bottle")
    ]
    
    for ml, label, tooltip in water_amounts:
        btn = ttk.Button(
            wbtns, 
            text=f"{label}\n+{ml} ml", 
            style='Accent.TButton',
            command=lambda m=ml: quick_add_enhanced(m, water_date_picker.get(), f"water-tab-{m}")
        )
        btn.pack(side="left", padx=4)
        add_tooltip(btn, tooltip)
    
    # Custom amount section
    custom_frame = ttk.LabelFrame(tab_water, text="Custom Amount", padding=10)
    custom_frame.pack(fill="x")
    
    custom_entry = SmartEntry(
        custom_frame,
        "Custom Amount (ml)",
        value_type="number",
        min_value=1,
        max_value=2000,
        tooltip="Enter any amount between 1-2000ml",
        width=15
    )
    custom_entry.pack(side="left", padx=(0, 8))

    def add_custom_water():
        if not custom_entry.validate():
            show_toast(root, "Please enter a valid amount in ml", "error")
            return
        try:
            ml = int(float(custom_entry.get() or 0))
            quick_add_enhanced(ml, water_date_picker.get(), "water-tab-custom")
            custom_entry.set("")  # Clear after adding
        except ValueError:
            show_toast(root, "Please enter a valid number", "error")
    
    ttk.Button(custom_frame, text="Add Custom Amount", command=add_custom_water).pack(side="left", padx=4)
    
    def quick_add_enhanced(ml: int, date_input: Optional[str] = None, source: str = "gui"):
        try:
            chosen_date = resolve_date_value(date_input if date_input is not None else today_iso())
        except ValueError as err:
            show_toast(root, f"Invalid date: {str(err)}", "error")
            return
        add_water_intake(db, user_var.get().strip() or default_user, chosen_date, ml, source)
        show_toast(root, f"Added {ml}ml of water for {chosen_date}", "success")
        refresh_dashboard()

    # 🌦️ Weather tab
    tab_w = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_w, text="Weather")
    city_var = tk.StringVar(value=init_city or cfg.get("default_city", ""))
    country_var = tk.StringVar(value=init_country or cfg.get("default_country", ""))
    days_var = tk.StringVar(value="3")
    tab_w.columnconfigure((1, 3, 5), weight=1)
    ttk.Label(tab_w, text="Forecast Sync", style='PanelHeading.TLabel').grid(row=0, column=0, columnspan=6, sticky='w', pady=(0, 6))
    for i, (label, var) in enumerate([("City", city_var), ("Country", country_var), ("Days (1-7)", days_var)]):
        ttk.Label(tab_w, text=label, style='PanelBody.TLabel').grid(row=1, column=2*i, sticky="e", padx=4, pady=4)
        ttk.Entry(tab_w, textvariable=var, width=16).grid(row=1, column=2*i+1, sticky="we", padx=4, pady=4)
    ttk.Button(
        tab_w,
        text="Fetch Forecast",
        command=lambda: fetch_forecast(
            db,
            cfg,
            user_var.get().strip() or default_user,
            city_var.get(),
            country_var.get(),
            days_var.get(),
            on_refresh=refresh_dashboard,
            on_insights=generate_insights,
        ),
    ).grid(row=2, column=0, columnspan=6, pady=6, sticky='w')

    # 💡 Insights tab
    tab_ins = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_ins, text='Insights')
    tf_var = tk.StringVar(value='7')
    rb_frame = ttk.Frame(tab_ins, style='Panel.TFrame'); rb_frame.pack(fill='x')
    ttk.Label(rb_frame, text='Health Score period:', style='PanelBody.TLabel').pack(side='left', padx=6)
    ttk.Radiobutton(rb_frame, text='7 days', variable=tf_var, value='7').pack(side='left', padx=4)
    ttk.Radiobutton(rb_frame, text='30 days', variable=tf_var, value='30').pack(side='left', padx=4)

    txt_ins = tk.Text(tab_ins, width=100, height=14, wrap='word', relief='flat', bd=0)
    txt_ins.pack(fill='both', expand=True, pady=8)
    text_widgets.append(txt_ins)

    qa = ttk.Frame(tab_ins, style='Panel.TFrame'); qa.pack(fill='x')
    ttk.Label(qa, text='Quick actions:', style='PanelBody.TLabel').pack(side='left', padx=6)
    btn_250 = ttk.Button(qa, text='+250 ml', style='Accent.TButton', 
                        command=lambda: (add_water_intake(db, user_var.get().strip() or default_user, today_iso(), 250, 'insight'), 
                                       refresh_dashboard(), generate_insights(), 
                                       show_toast(root, "Added 250ml water", "success")))
    btn_250.pack(side='left', padx=2)
    add_tooltip(btn_250, "Quick add 250ml water")
    
    btn_500 = ttk.Button(qa, text='+500 ml', style='Accent.TButton', 
                        command=lambda: (add_water_intake(db, user_var.get().strip() or default_user, today_iso(), 500, 'insight'), 
                                       refresh_dashboard(), generate_insights(),
                                       show_toast(root, "Added 500ml water", "success")))
    btn_500.pack(side='left', padx=2)
    add_tooltip(btn_500, "Quick add 500ml water")
    
    btn_walk = ttk.Button(qa, text='Prefill 30-min walk', command=lambda: prefill_walk())
    btn_walk.pack(side='left', padx=2)
    add_tooltip(btn_walk, "Prefill activity form with typical 30-minute walk data")

    def prefill_walk():
        try:
            steps_entry.set('3000')
            cals_entry.set('150')
            mood_entry.set('4')
            notes_var.set('30-min walk')
            show_toast(root, 'Activity fields prefilled for a 30-min walk. Go to the Activity tab to save.', "info")
        except Exception:
            pass

    def generate_insights():
        period = int(tf_var.get() or '7')
        u = get_user(db, user_var.get().strip() or default_user) or _default_profile(default_user)
        _, _, _, _, h, w, _, _, _ = u
        # 🧮 Health score
        hs = health_score(db, user_var.get().strip() or default_user, w, h, days=period)
        score = hs.get('score', 0)
        if score >= 85: band = 'Excellent'
        elif score >= 70: band = 'Good'
        elif score >= 50: band = 'Fair'
        else: band = 'Needs attention'
        # 💦 Hydration insight
        from .hydration import hydration_progress
        prog = hydration_progress(db, user_var.get().strip() or default_user, today_iso(), w)
        hyd_pct = 0 if prog['goal_ml'] <= 0 else int(prog['total_ml']*100/prog['goal_ml'])
        hyd_ins = 'On track for hydration today.' if hyd_pct >= 100 else f"Drink {prog['remaining_ml']} ml more to reach today's goal."
        # 😴 Sleep insight (weekly)
        ss7 = sleep_stats(db, user_var.get().strip() or default_user, days=7)
        sleep_ins = 'Sleep average meets target.' if ss7['percent_vs_8h'] >= 100 else f"Avg {ss7['avg_hours']}h (vs 8h). Aim +{round(max(0,8-ss7['avg_hours'])*60)} min/night."
        # 🚶 Steps trend insight
        kp = kpis(db, user_var.get().strip() or default_user, 7)
        st = int(kp.get('steps_movavg_7d_last') or 0)
        steps_ins = 'Great step trend.' if st >= 10000 else f"7d avg {st} steps. Consider a 3k–5k walk to boost."
        # 🌤️ Weather-based tip
        wrow = weather_on_date(db, today_iso(), user_var.get().strip() or default_user)
        wx_ins = 'Weather not saved for today.' if not wrow else ( 'Hot day — prioritize water.' if (wrow[0] and wrow[0] > 30) else 'Weather is mild — good for outdoor activity.' )
        # 📝 Compose text
        lines = [
            f"Health Score ({period}d): {score} ({band})",
            f"Hydration: {hyd_ins}",
            f"Sleep: {sleep_ins}",
            f"Steps: {steps_ins}",
            f"Weather: {wx_ins}",
        ]
        txt_ins.delete('1.0', tk.END); txt_ins.insert(tk.END, '\n'.join(lines))

    ttk.Button(tab_ins, text='Generate insights', style='Accent.TButton', command=generate_insights).pack(anchor='w', pady=6)

    header_buttons.columnconfigure((0, 1, 2, 3, 4), weight=0)
    
    def navigate_to_tab(tab, tab_name):
        """Navigate to tab and update breadcrumb"""
        nb.select(tab)
        breadcrumb.update_path(["NovaFit Plus", tab_name])
        status_bar.set_info(f"Viewing {tab_name}")
    
    def quick_demo_header():
        """Quick demo generation from header"""
        try:
            generator = DemoDataGenerator(db)
            demo_user = generator.quick_demo_setup()
            user_var.set(demo_user)
            refresh_dashboard()
            generate_insights()
            show_smart_toast(
                root,
                "Quick Demo Ready! 🎯",
                f"Generated 14 days of demo data for '{demo_user}'. Explore the features!",
                "success",
                duration=4000
            )
        except Exception as e:
            show_toast(root, f"Demo generation failed: {str(e)}", "error")
    
    refresh_btn = ttk.Button(header_buttons, text='Refresh View', style='Accent.TButton', 
              command=lambda: (refresh_dashboard(), generate_insights()))
    refresh_btn.grid(row=0, column=0, padx=4)
    add_tooltip(refresh_btn, "Refresh dashboard data and regenerate insights (Ctrl+R)")
    
    theme_btn = ttk.Button(header_buttons, text='Toggle Theme', command=switch_theme)
    theme_btn.grid(row=0, column=1, padx=4)
    add_tooltip(theme_btn, "Switch between light and dark themes (Ctrl+T)")
    
    demo_btn = ttk.Button(header_buttons, text='Quick Demo', command=quick_demo_header)
    demo_btn.grid(row=0, column=2, padx=4)
    add_tooltip(demo_btn, "Generate 14 days of realistic demo data instantly (Ctrl+D)")
    
    activity_btn = ttk.Button(header_buttons, text='Activity', 
              command=lambda: navigate_to_tab(tab_act, "Activity"))
    activity_btn.grid(row=0, column=3, padx=4)
    add_tooltip(activity_btn, "Go to Activity tracking tab (Ctrl+N)")
    
    reports_btn = ttk.Button(header_buttons, text='Reports', 
              command=lambda: navigate_to_tab(tab_rep, "Reports"))
    reports_btn.grid(row=0, column=4, padx=4)
    add_tooltip(reports_btn, "View charts and analytical reports")

    # 📊 Analytics tab
    tab_an = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_an, text="Analytics")
    days_an_var = tk.StringVar(value="14")
    ttk.Label(tab_an, text="Analyze last N days:", style='PanelBody.TLabel').pack(anchor="w")
    ttk.Entry(tab_an, textvariable=days_an_var, width=10).pack(anchor="w")
    txt_an = tk.Text(tab_an, width=100, height=16, wrap="word", relief='flat', bd=0)
    txt_an.pack(fill="both", expand=True, pady=8)
    text_widgets.append(txt_an)

    def run_analytics():
        try:
            days = int(days_an_var.get() or 14)
            res = kpis(db, user_var.get().strip() or default_user, days)
            lines = [f"KPIs: {res}"]
            lines.append("Best running days:")
            for d, cond, score in best_running_days(db, days):
                lines.append(f"  {d} — {cond} — Score {score}")
            lines.append("Hydration adherence (7 days):")
            u = get_user(db, user_var.get().strip() or default_user) or _default_profile(default_user)
            _, _, _, _, h, w, _, _, _ = u
            rep = hydration_adherence(db, user_var.get().strip() or default_user, w, days=7)
            for row in rep:
                lines.append(f"  {row}")
            hs = health_score(db, user_var.get().strip() or default_user, w, h, days=7)
            lines.append(f"Health Score (7d): {hs}")
            txt_an.delete('1.0', tk.END); txt_an.insert(tk.END, "\n".join(lines))
            show_toast(root, f"Analytics generated for last {days} days", "success")
        except Exception as e:
            show_toast(root, f"Error generating analytics: {str(e)}", "error")
    ttk.Button(tab_an, text="Run Analytics", style='Accent.TButton', command=run_analytics).pack(anchor="w")

    # 🖼️ Reports tab
    tab_rep = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_rep, text="Reports")
    rep_timeframe_var = tk.StringVar(value="14")
    report_status_var = tk.StringVar(value="Charts render inline. Use Export to save PNGs.")
    report_figures = {}
    report_canvases = {}

    controls_rep = ttk.Frame(tab_rep, style='Panel.TFrame')
    controls_rep.pack(fill='x')
    controls_rep.columnconfigure(4, weight=1)
    ttk.Label(controls_rep, text="Timeframe (days):", style='PanelBody.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 8))
    rep_timeframe_cb = ttk.Combobox(
        controls_rep,
        textvariable=rep_timeframe_var,
        values=("7", "14", "30"),
        state='readonly',
        width=6,
    )
    rep_timeframe_cb.grid(row=0, column=1, sticky='w')

    def parse_report_days() -> int:
        """Parse timeframe selection to an integer. 🔢"""

        try:
            return max(1, int(rep_timeframe_var.get() or 14))
        except ValueError as exc:
            raise ValueError("Please choose a valid number of days.") from exc

    def render_canvas(slot: str, figure):
        """Render or update a canvas slot with a Matplotlib figure. 🖼️"""

        container = report_containers[slot]
        if slot in report_canvases:
            report_canvases[slot].get_tk_widget().destroy()
        canvas = FigureCanvasTkAgg(figure, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        report_canvases[slot] = canvas

    def gen_charts(*_args):
        """Refresh report figures using the chosen timeframe. 🔄"""

        try:
            days = parse_report_days()
            user_profile = get_user(db, user_var.get().strip() or default_user) or _default_profile(default_user)
            _, _, _, _, _, weight_kg, _, _, _ = user_profile
            report_figures.clear()
            report_figures.update(
                {
                    'hydration_trend': chart_hydration(db, user_var.get().strip() or default_user, weight_kg, days),
                    'steps_vs_sleep': chart_steps_vs_sleep(db, user_var.get().strip() or default_user, days),
                    'sleep_vs_goal': chart_sleep_vs_goal(db, user_var.get().strip() or default_user, days),
                }
            )
            for key, figure in report_figures.items():
                render_canvas(key, figure)
            report_status_var.set(f"Charts updated for last {days} day(s).")
        except Exception as exc:
            messagebox.showerror('Error', str(exc))

    ttk.Button(controls_rep, text="Refresh Charts", style='Accent.TButton', command=gen_charts).grid(row=0, column=2, padx=8)

    def export_charts():
        """Save the current report figures to PNG files. 💾"""

        if not report_figures:
            messagebox.showinfo('Reports', 'Generate charts before exporting.')
            return
        try:
            saved = save_report_figures(report_figures, outdir="exports/charts")
            joined = "\n".join(f"{name}: {path}" for name, path in saved.items())
            report_status_var.set(f"Charts exported to disk. ({len(saved)} files)")
            messagebox.showinfo('Reports', f'PNG files saved:\n{joined}')
        except Exception as exc:
            messagebox.showerror('Error', str(exc))

    ttk.Button(controls_rep, text="Export PNGs", command=export_charts).grid(row=0, column=3)

    ttk.Label(tab_rep, textvariable=report_status_var, style='PanelBody.TLabel').pack(anchor='w', pady=(8, 4))

    charts_frame = ttk.Frame(tab_rep, style='Panel.TFrame')
    charts_frame.pack(fill='both', expand=True)
    charts_frame.columnconfigure(0, weight=1)
    charts_frame.columnconfigure(1, weight=1)
    charts_frame.rowconfigure(0, weight=1)
    charts_frame.rowconfigure(1, weight=1)

    report_containers = {
        'hydration_trend': ttk.Frame(charts_frame, style='Panel.TFrame', padding=6),
        'steps_vs_sleep': ttk.Frame(charts_frame, style='Panel.TFrame', padding=6),
        'sleep_vs_goal': ttk.Frame(charts_frame, style='Panel.TFrame', padding=6),
    }

    ttk.Label(report_containers['hydration_trend'], text='Hydration Trend', style='PanelHeading.TLabel').pack(anchor='w')
    ttk.Label(report_containers['steps_vs_sleep'], text='Steps vs Sleep', style='PanelHeading.TLabel').pack(anchor='w')
    ttk.Label(report_containers['sleep_vs_goal'], text='Sleep vs Goal', style='PanelHeading.TLabel').pack(anchor='w')

    report_containers['hydration_trend'].grid(row=0, column=0, sticky='nsew', padx=4, pady=4)
    report_containers['steps_vs_sleep'].grid(row=0, column=1, sticky='nsew', padx=4, pady=4)
    report_containers['sleep_vs_goal'].grid(row=1, column=0, columnspan=2, sticky='nsew', padx=4, pady=4)

    rep_timeframe_cb.bind('<<ComboboxSelected>>', gen_charts)

    # 📤 Export tab
    tab_ex = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_ex, text="Export")
    ttk.Label(tab_ex, text="Share your data in seconds", style='PanelBody.TLabel').pack(anchor='w')
    def do_export_json():
        try:
            out = export_json(db, cfg["export_dir"], user_var.get().strip() or default_user, days=14)
            show_toast(root, f"JSON exported successfully to: {out}", "success")
        except Exception as e:
            show_toast(root, f"Export failed: {str(e)}", "error")
    
    def do_export_xlsx():
        try:
            out = export_excel(db, cfg["export_dir"], user_var.get().strip() or default_user, days=14)
            show_toast(root, f"Excel exported successfully to: {out}", "success")
        except Exception as e:
            show_toast(root, f"Export failed: {str(e)}", "error")
    
    def do_export_csv():
        try:
            outs = export_csv(db, cfg["export_dir"], user_var.get().strip() or default_user, days=14)
            show_toast(root, f"CSV exported successfully: {outs}", "success")
        except Exception as e:
            show_toast(root, f"Export failed: {str(e)}", "error")
    
    export_json_btn = ttk.Button(tab_ex, text="Export JSON", style='Accent.TButton', command=do_export_json)
    export_json_btn.pack(anchor="w", pady=4)
    add_tooltip(export_json_btn, "Export all your data to a JSON file for backup or analysis")
    
    export_excel_btn = ttk.Button(tab_ex, text="Export Excel", style='Accent.TButton', command=do_export_xlsx)
    export_excel_btn.pack(anchor="w", pady=4)
    add_tooltip(export_excel_btn, "Export to Excel spreadsheet with multiple sheets for different data types")
    
    export_csv_btn = ttk.Button(tab_ex, text="Export CSV", style='Accent.TButton', command=do_export_csv)
    export_csv_btn.pack(anchor="w", pady=4)
    add_tooltip(export_csv_btn, "Export to CSV files - compatible with most data analysis tools")

    # 👤 Profile tab
    tab_prof = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_prof, text="Profile")
    ttk.Label(tab_prof, text="Personal details", style='PanelHeading.TLabel').pack(anchor='w')
    name_var = tk.StringVar(value=init_name or default_user)
    age_var = tk.StringVar(value=str(init_age if init_age is not None else 30))
    sex_var = tk.StringVar(value=init_sex or "M")
    ht_var = tk.StringVar(value=str(init_h if init_h is not None else 166))
    wt_var = tk.StringVar(value=str(init_w if init_w is not None else 66))
    actl_var = tk.StringVar(value=init_al or "light")
    city_prof_var = tk.StringVar(value=init_city or "")
    country_prof_var = tk.StringVar(value=init_country or "")
    grid = ttk.Frame(tab_prof, style='Panel.TFrame'); grid.pack(fill="x", pady=6)
    for i, (lab, var) in enumerate([
        ("Name", name_var),
        ("Age", age_var),
        ("Sex", sex_var),
        ("Height cm", ht_var),
        ("Weight kg", wt_var),
        ("Activity level", actl_var),
        ("City", city_prof_var),
        ("Country", country_prof_var),
    ]):
        ttk.Label(grid, text=lab, style='PanelBody.TLabel').grid(row=i, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(grid, textvariable=var, width=20).grid(row=i, column=1, sticky="w", padx=4, pady=4)
    def save_profile():
        try:
            name = name_var.get().strip() or default_user
            age = int(age_var.get().strip() or init_age)
            sex = sex_var.get().strip() or "M"
            height = float(ht_var.get().strip() or init_h)
            weight = float(wt_var.get().strip() or init_w)
            activity = (actl_var.get().strip() or "light").lower()
            city_val = city_prof_var.get().strip()
            country_val = country_prof_var.get().strip()
            
            # Get current user city before updating to detect changes
            current_user = get_user(db, name) or _default_profile(name)
            current_city = current_user[7] if current_user and len(current_user) > 7 else ""
            
            upsert_user(db, name, age, sex, height, weight, activity, city_val, country_val)
            user_var.set(name)
            actl_var.set(activity)
            city_prof_var.set(city_val)
            country_prof_var.set(country_val)
            city_var.set(city_val or cfg.get("default_city", ""))
            country_var.set(country_val or cfg.get("default_country", ""))
            
            # Clear weather cache when city changes to force fresh data
            try:
                import os
                if os.path.exists("weather_cache.json"):
                    os.remove("weather_cache.json")
            except:
                pass
            
            show_toast(root, "Profile updated successfully!", "success")
            refresh_dashboard()
            
            # Force immediate weather fetch for new city if different
            if city_val and city_val != current_city:
                show_toast(root, f"Updating weather for {city_val}...", "info", 3000)
                # Trigger weather fetch in background
                def delayed_weather_fetch():
                    try:
                        fetch_today_weather(db, cfg, name, lambda: root.after(500, refresh_dashboard))
                    except:
                        pass
                import threading
                weather_thread = threading.Thread(target=delayed_weather_fetch)
                weather_thread.daemon = True
                weather_thread.start()
        except Exception as e:
            show_toast(root, f"Error saving profile: {str(e)}", "error")
    ttk.Button(tab_prof, text="Save Profile", style='Accent.TButton', command=save_profile).pack(anchor="w", pady=6)

    # 🎭 Demo Data Section
    ttk.Separator(tab_prof, orient='horizontal').pack(fill='x', pady=(16, 8))
    ttk.Label(tab_prof, text="Demo Data Generator", style='PanelHeading.TLabel').pack(anchor='w')
    ttk.Label(tab_prof, text="Generate realistic demo data for testing and presentation", style='PanelBody.TLabel').pack(anchor='w', pady=(0, 8))
    
    demo_frame = ttk.Frame(tab_prof, style='Panel.TFrame')
    demo_frame.pack(fill="x", pady=4)
    
    demo_days_var = tk.StringVar(value="14")
    demo_user_var = tk.StringVar(value="Demo User")
    
    demo_controls = ttk.Frame(demo_frame, style='Panel.TFrame')
    demo_controls.pack(fill="x", pady=4)
    
    ttk.Label(demo_controls, text="Demo User Name:", style='PanelBody.TLabel').grid(row=0, column=0, sticky="e", padx=4, pady=2)
    ttk.Entry(demo_controls, textvariable=demo_user_var, width=20).grid(row=0, column=1, sticky="w", padx=4, pady=2)
    
    ttk.Label(demo_controls, text="Days of Data:", style='PanelBody.TLabel').grid(row=1, column=0, sticky="e", padx=4, pady=2)
    demo_days_combo = ttk.Combobox(
        demo_controls,
        textvariable=demo_days_var,
        values=("7", "14", "30", "60"),
        state='readonly',
        width=18
    )
    demo_days_combo.grid(row=1, column=1, sticky="w", padx=4, pady=2)
    
    def generate_quick_demo():
        try:
            days = int(demo_days_var.get() or 14)
            user_name = demo_user_var.get().strip() or "Demo User"
            
            generator = DemoDataGenerator(db)
            created_user = generator.populate_demo_user(user_name, days)
            
            # Switch to the demo user
            user_var.set(created_user)
            refresh_dashboard()
            generate_insights()
            
            show_smart_toast(
                root,
                f"Demo data generated! 🎉",
                f"Created {days} days of realistic data for '{created_user}'. Check your dashboard!",
                "success",
                duration=5000
            )
        except Exception as e:
            show_toast(root, f"Error generating demo data: {str(e)}", "error")
    
    def generate_full_demo():
        try:
            generator = DemoDataGenerator(db)
            demo_users = generator.create_demo_dataset(num_users=3, days_back=30)
            
            # Switch to first demo user
            if demo_users:
                user_var.set(demo_users[0])
                refresh_dashboard()
                generate_insights()
            
            show_smart_toast(
                root,
                "Full demo dataset created! 🚀",
                f"Generated 3 demo users with 30 days of data each: {', '.join(demo_users)}",
                "success",
                duration=6000
            )
        except Exception as e:
            show_toast(root, f"Error generating full demo: {str(e)}", "error")
    
    demo_buttons = ttk.Frame(demo_frame, style='Panel.TFrame')
    demo_buttons.pack(fill="x", pady=8)
    
    quick_demo_btn = ttk.Button(
        demo_buttons, 
        text="Generate Quick Demo", 
        style='Accent.TButton',
        command=generate_quick_demo
    )
    quick_demo_btn.pack(side="left", padx=(0, 8))
    add_tooltip(quick_demo_btn, "Generate demo data for one user with customizable settings")
    
    full_demo_btn = ttk.Button(
        demo_buttons,
        text="Generate Full Demo Dataset",
        command=generate_full_demo
    )
    full_demo_btn.pack(side="left", padx=4)
    add_tooltip(full_demo_btn, "Generate comprehensive demo dataset with 3 users and 30 days of data")
    
    auto_demo_btn = ttk.Button(
        demo_buttons,
        text="Auto-populate Current User",
        command=lambda: (
            populate_demo_data(db, user_var.get().strip() or default_user, 7),
            refresh_dashboard(),
            generate_insights(),
            show_toast(root, f"Added 7 days of demo data for {user_var.get()}", "success")
        )
    )
    auto_demo_btn.pack(side="left", padx=4)
    add_tooltip(auto_demo_btn, "Add realistic demo data to the current user profile")

    # 🚀 Advanced Settings tab
    tab_advanced = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_advanced, text="Advanced")
    
    # Create scrollable frame for advanced settings
    advanced_canvas = tk.Canvas(tab_advanced, highlightthickness=0)
    advanced_scrollbar = ttk.Scrollbar(tab_advanced, orient="vertical", command=advanced_canvas.yview)
    advanced_scrollable_frame = ttk.Frame(advanced_canvas, style='Panel.TFrame')
    
    advanced_scrollable_frame.bind(
        "<Configure>",
        lambda e: advanced_canvas.configure(scrollregion=advanced_canvas.bbox("all"))
    )
    
    advanced_canvas.create_window((0, 0), window=advanced_scrollable_frame, anchor="nw")
    advanced_canvas.configure(yscrollcommand=advanced_scrollbar.set)
    
    advanced_canvas.pack(side="left", fill="both", expand=True)
    advanced_scrollbar.pack(side="right", fill="y")
    
    # Initialize gamification engine
    gamification_engine = GamificationEngine(db, user_var.get().strip() or default_user)
    
    # Initialize adaptive theme manager  
    def on_theme_change(theme_mode):
        theme_state['mode'] = theme_mode
        apply_theme(theme_mode)
    
    adaptive_theme_manager = AdaptiveThemeManager(on_theme_change)
    
    # Setup all advanced styles
    setup_dashboard_styles(style)
    setup_gamification_styles(style)
    setup_adaptive_theme_styles(style)
    
    # Gamification widget
    gamification_widget = GamificationWidget(advanced_scrollable_frame, gamification_engine)
    
    # Theme control widget
    theme_control_widget = ThemeControlWidget(advanced_scrollable_frame, adaptive_theme_manager)
    
    # Modular dashboard section
    dashboard_section = ttk.LabelFrame(
        advanced_scrollable_frame,
        text="🎛️ Dashboard Customization",
        padding=10
    )
    dashboard_section.pack(fill="x", pady=10)
    
    ttk.Label(
        dashboard_section,
        text="Customize your dashboard layout with drag & drop widgets",
        style='PanelBody.TLabel'
    ).pack(anchor="w", pady=(0, 10))
    
    def open_dashboard_designer():
        """Open dashboard designer window"""
        designer_window = tk.Toplevel(root)
        designer_window.title("Dashboard Designer")
        designer_window.geometry("800x600")
        designer_window.resizable(True, True)
        
        # Create modular dashboard in new window
        modular_dashboard = ModularDashboard(designer_window)
        
        # Sample data for widgets
        sample_data = {
            'hydration': {
                'value': daily_water_total(db, user_var.get().strip() or default_user, today_iso()),
                'unit': 'ml',
                'trend': '↗ +15% this week'
            },
            'steps': {
                'value': steps_on_date(db, user_var.get().strip() or default_user, today_iso()) or 0,
                'unit': 'steps',
                'trend': '→ Steady pace'
            },
            'sleep': {
                'value': sleep_on_date(db, user_var.get().strip() or default_user, today_iso()) or 0,
                'unit': 'hours',
                'trend': '↗ Improving'
            },
            'trend': {
                'values': [20, 35, 25, 40, 30, 45, 35]
            },
            'goals': {
                'current': 75,
                'goal': 100
            }
        }
        
        # Update widgets with sample data
        modular_dashboard.update_all_widgets(sample_data)
    
    ttk.Button(
        dashboard_section,
        text="Open Dashboard Designer",
        command=open_dashboard_designer,
        style='Accent.TButton'
    ).pack(anchor="w")
    
    # Goals and Achievements section
    goals_section = ttk.LabelFrame(
        advanced_scrollable_frame,
        text="🎯 Goals & Achievements",
        padding=10
    )
    goals_section.pack(fill="x", pady=10)
    
    def open_goals_manager():
        """Open goals and achievements manager"""
        goals_window = tk.Toplevel(root)
        goals_window.title("Goals & Achievements")
        goals_window.geometry("600x500")
        goals_window.resizable(True, True)
        
        # Goals notebook
        goals_notebook = ttk.Notebook(goals_window)
        goals_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Active Goals tab
        goals_tab = ttk.Frame(goals_notebook, padding=10)
        goals_notebook.add(goals_tab, text="Active Goals")
        
        ttk.Label(goals_tab, text="Active Goals", style='PanelHeading.TLabel').pack(anchor="w")
        
        goals_list = ttk.Treeview(
            goals_tab,
            columns=('title', 'progress', 'deadline'),
            show='headings',
            height=8
        )
        goals_list.heading('title', text='Goal')
        goals_list.heading('progress', text='Progress')
        goals_list.heading('deadline', text='Deadline')
        goals_list.pack(fill="both", expand=True, pady=10)
        
        # Populate goals
        for goal_id, goal in gamification_engine.goals.items():
            if not goal.is_completed:
                progress = f"{goal.current_value}/{goal.target_value}"
                goals_list.insert('', 'end', values=(goal.title, progress, goal.deadline or "No deadline"))
        
        # Achievements tab
        achievements_tab = ttk.Frame(goals_notebook, padding=10)
        goals_notebook.add(achievements_tab, text="Achievements")
        
        ttk.Label(achievements_tab, text="Achievements", style='PanelHeading.TLabel').pack(anchor="w")
        
        # Achievement grid
        ach_frame = ttk.Frame(achievements_tab)
        ach_frame.pack(fill="both", expand=True, pady=10)
        
        row, col = 0, 0
        for ach_id, achievement in gamification_engine.achievements.items():
            ach_card = ttk.LabelFrame(
                ach_frame,
                text=achievement.title,
                padding=5
            )
            ach_card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            # Achievement icon and status
            icon_color = "gold" if achievement.is_unlocked else "gray"
            ttk.Label(
                ach_card,
                text=achievement.icon,
                font=("TkDefaultFont", 16),
                foreground=icon_color
            ).pack()
            
            ttk.Label(
                ach_card,
                text=achievement.description,
                style='PanelBody.TLabel',
                wraplength=120
            ).pack()
            
            if achievement.is_unlocked:
                ttk.Label(
                    ach_card,
                    text=f"✅ {achievement.points} XP",
                    foreground="green",
                    font=("TkDefaultFont", 8, "bold")
                ).pack()
            else:
                ttk.Label(
                    ach_card,
                    text="🔒 Locked",
                    foreground="gray",
                    font=("TkDefaultFont", 8)
                ).pack()
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
    
    ttk.Button(
        goals_section,
        text="Manage Goals & Achievements",
        command=open_goals_manager,
        style='Accent.TButton'
    ).pack(anchor="w", pady=(0, 5))
    
    # 🔴 Reset Application section
    reset_section = ttk.LabelFrame(
        advanced_scrollable_frame,
        text="🔴 Reset Application",
        padding=10
    )
    reset_section.pack(fill="x", pady=10)
    
    ttk.Label(
        reset_section,
        text="⚠️ Danger Zone: Reset all application data",
        style='PanelHeading.TLabel',
        foreground='red'
    ).pack(anchor="w", pady=(0, 5))
    
    ttk.Label(
        reset_section,
        text="This will permanently delete ALL data and reset the application to its initial state.",
        style='PanelBody.TLabel'
    ).pack(anchor="w", pady=(0, 10))
    
    # Data summary frame
    data_summary_frame = ttk.Frame(reset_section, style='Panel.TFrame')
    data_summary_frame.pack(fill="x", pady=(0, 10))
    
    data_summary_labels = {}
    
    def update_data_summary():
        """Update the data summary display"""
        try:
            summary = get_data_summary(db)
            for key, value in summary.items():
                if key in data_summary_labels:
                    data_summary_labels[key].config(text=f"{value}")
        except Exception:
            pass
    
    # Create data summary display
    summary_info = [
        ("Users", "users"),
        ("Activities", "activities"),
        ("Weather Records", "weather"),
        ("Water Intake Records", "water_intake")
    ]
    
    for i, (label, key) in enumerate(summary_info):
        row_frame = ttk.Frame(data_summary_frame, style='Panel.TFrame')
        row_frame.pack(fill="x", pady=2)
        
        ttk.Label(row_frame, text=f"{label}:", style='PanelBody.TLabel').pack(side="left")
        data_summary_labels[key] = ttk.Label(row_frame, text="0", style='PanelBody.TLabel')
        data_summary_labels[key].pack(side="right")
    
    # Update data summary initially
    update_data_summary()
    
    def confirm_reset():
        """Show simple Yes/No confirmation dialog and reset if confirmed"""
        update_data_summary()
        
        # Check if there's any data
        summary = get_data_summary(db)
        total_records = sum(summary.values())
        
        if total_records == 0:
            show_toast(root, "Database is already empty.", "info")
            return
        
        # Create data summary message
        data_info = []
        for label, key in summary_info:
            count = summary[key]
            if count > 0:
                data_info.append(f"• {count} {label}")
        
        data_text = "\n".join(data_info)
        
        # Use standard messagebox for reliable Yes/No confirmation
        import tkinter.messagebox as msgbox
        
        message = f"""⚠️ RESET APPLICATION DATA

This will PERMANENTLY DELETE all data:

{data_text}

⚠️ This action cannot be undone!

Are you absolutely sure you want to reset the application?"""
        
        # Show Yes/No dialog
        result = msgbox.askyesno(
            "⚠️ Confirm Reset", 
            message,
            icon='warning',
            default='no'
        )
        
        if result:  # User clicked YES
            # Show progress
            show_toast(root, "Resetting application...", "info", 2000)
            
            try:
                # Reset database
                reset_to_default(db)
                
                # Clear cache files
                import os
                cache_files = ["weather_cache.json", "gamification_Kevin.json"]
                for cache_file in cache_files:
                    if os.path.exists(cache_file):
                        try:
                            os.remove(cache_file)
                        except:
                            pass
                
                # Update data summary
                update_data_summary()
                
                # Reset user variable to default
                user_var.set("Kevin")
                
                # Update user list if function is available
                try:
                    update_user_list()
                except NameError:
                    # Function not in scope, update combobox directly
                    try:
                        user_selector['values'] = ["Kevin"]
                    except:
                        pass
                
                # Refresh dashboard
                refresh_dashboard()
                
                # Show success
                show_smart_toast(
                    root,
                    "Application Reset Complete! 🎉",
                    "All data has been cleared. You can now start fresh with a new profile.",
                    "success",
                    duration=5000
                )
                
                # Switch to profile tab to encourage user to set up
                nb.select(tab_prof)
                
            except Exception as e:
                show_toast(root, f"Reset failed: {str(e)}", "error")
        else:  # User clicked NO or cancelled
            show_toast(root, "Reset cancelled.", "info")
    
    # Reset buttons
    button_frame = ttk.Frame(reset_section, style='Panel.TFrame')
    button_frame.pack(fill="x", pady=(0, 5))
    
    ttk.Button(
        button_frame,
        text="🔄 Refresh Data Summary",
        command=update_data_summary
    ).pack(side="left")
    
    ttk.Button(
        button_frame,
        text="🗑️ Reset Application",
        command=confirm_reset,
        style='Accent.TButton'
    ).pack(side="right")
    
    add_tooltip(button_frame.winfo_children()[0], "Update the data summary counts")
    add_tooltip(button_frame.winfo_children()[1], "⚠️ Permanently delete ALL application data")
    
    # Auto-update gamification data
    def update_gamification():
        """Update gamification with current activity data"""
        try:
            today = today_iso()
            
            activity_data = {
                'daily_water_ml': daily_water_total(db, user_var.get().strip() or default_user, today),
                'daily_steps': steps_on_date(db, user_var.get().strip() or default_user, today) or 0,
                'sleep_hours': sleep_on_date(db, user_var.get().strip() or default_user, today) or 0,
                'health_score': 0  # Will be calculated based on other metrics
            }
            
            # Calculate health score
            user_profile = get_user(db, user_var.get().strip() or default_user) or _default_profile(default_user)
            _, _, _, _, h, w, _, _, _ = user_profile
            hs = health_score(db, user_var.get().strip() or default_user, w, h, days=7)
            activity_data['health_score'] = hs.get('score', 0)
            
            # Check for new achievements
            new_achievements = gamification_engine.check_achievements(activity_data)
            
            # Show achievement popups
            for achievement in new_achievements:
                if hasattr(gamification_widget, 'show_achievement_popup'):
                    gamification_widget.show_achievement_popup(achievement)
            
            # Update widget display
            gamification_widget.update_display()
            
        except Exception as e:
            print(f"Error updating gamification: {e}")
    
    # Start adaptive theme checking
    adaptive_theme_manager.start_auto_checking(root)
    
    # Apply initial theme
    adaptive_theme_manager.apply_theme()

    # Enhanced status bar
    status_bar = StatusBar(root)
    status_bar.pack(fill="x", side="bottom")
    status_widgets.append(status_bar)

    # Setup breadcrumb navigation callbacks after all tabs are defined
    breadcrumb.add_navigation_callback("NovaFit Plus", lambda: navigate_to_tab(tab_dash, "Dashboard"))
    breadcrumb.add_navigation_callback("Dashboard", lambda: navigate_to_tab(tab_dash, "Dashboard"))
    breadcrumb.add_navigation_callback("Activity", lambda: navigate_to_tab(tab_act, "Activity"))
    breadcrumb.add_navigation_callback("Water", lambda: navigate_to_tab(tab_water, "Water"))
    breadcrumb.add_navigation_callback("Weather", lambda: navigate_to_tab(tab_w, "Weather"))
    breadcrumb.add_navigation_callback("Insights", lambda: navigate_to_tab(tab_ins, "Insights"))
    breadcrumb.add_navigation_callback("Analytics", lambda: navigate_to_tab(tab_an, "Analytics"))
    breadcrumb.add_navigation_callback("Reports", lambda: navigate_to_tab(tab_rep, "Reports"))
    breadcrumb.add_navigation_callback("Export", lambda: navigate_to_tab(tab_ex, "Export"))
    breadcrumb.add_navigation_callback("Profile", lambda: navigate_to_tab(tab_prof, "Profile"))
    breadcrumb.add_navigation_callback("Advanced", lambda: navigate_to_tab(tab_advanced, "Advanced"))

    # 🔄 Helpers
    def fetch_today_weather(db, cfg, user_name, cb):
        try:
            profile = get_user(db, user_name) or _default_profile(user_name)
            city = (profile[7] or "").strip() or cfg.get("default_city", "")
            country = (profile[8] or "").strip() or cfg.get("default_country", "")
            lat, lon, cname = wz.geocode_city(city, country)
            data = wz.fetch_daily_forecast(lat, lon, days=1)
            daily = data.get("daily", {})
            for i, d in enumerate(daily.get("time", [])):
                tmax = daily.get("temperature_2m_max", [None]*len(daily["time"]))[i]
                tmin = daily.get("temperature_2m_min", [None]*len(daily["time"]))[i]
                hum = daily.get("relative_humidity_2m_mean", [None]*len(daily["time"]))[i]
                wind = daily.get("windspeed_10m_max", [None]*len(daily["time"]))[i]
                code = daily.get("weathercode", [None]*len(daily["time"]))[i]
                cond = wz.code_to_text(code) if code is not None else None
                insert_weather(db, d, cname, lat, lon, tmax, tmin, int(hum) if hum is not None else None, wind, cond)
            show_toast(root, f"Weather data fetched for {cname}", "success")
            cb()
        except Exception as e:
            show_toast(root, f"Weather fetch failed: {str(e)}", "error")

    def fetch_forecast(db, cfg, user_name, city, country, days, on_refresh=None, on_insights=None):
        try:
            days = max(1, min(int(days or 1), 7))
            profile = get_user(db, user_name) or _default_profile(user_name)
            resolved_city = city.strip() or (profile[7] or "").strip() or cfg.get("default_city", "")
            resolved_country = country.strip() or (profile[8] or "").strip() or cfg.get("default_country", "")
            lat, lon, cname = wz.geocode_city(resolved_city, resolved_country)
            data = wz.fetch_daily_forecast(lat, lon, days=days)
            daily = data.get("daily", {})
            for i, d in enumerate(daily.get("time", [])):
                tmax = daily.get("temperature_2m_max", [None]*len(daily["time"]))[i]
                tmin = daily.get("temperature_2m_min", [None]*len(daily["time"]))[i]
                hum = daily.get("relative_humidity_2m_mean", [None]*len(daily["time"]))[i]
                wind = daily.get("windspeed_10m_max", [None]*len(daily["time"]))[i]
                code = daily.get("weathercode", [None]*len(daily["time"]))[i]
                cond = wz.code_to_text(code) if code is not None else None
                insert_weather(db, d, cname, lat, lon, tmax, tmin, int(hum) if hum is not None else None, wind, cond)
            show_toast(root, f"Weather forecast saved for {cname} ({days} day(s))", "success")
            if callable(on_refresh):
                on_refresh()
            if callable(on_insights):
                on_insights()
            status_var.set("Forecast synced — dashboard and insights auto-refreshed.")
        except Exception as e:
            show_toast(root, f"Weather fetch failed: {str(e)}", "error")

    apply_theme(theme_state['mode'])
    refresh_dashboard()
    generate_insights()
    gen_charts()
    
    # Setup keyboard shortcuts after all components are ready
    shortcuts.add_shortcut("Control-r", refresh_dashboard, "Refresh dashboard")
    shortcuts.add_shortcut("F5", refresh_dashboard, "Refresh dashboard")
    shortcuts.add_shortcut("Control-n", lambda: nb.select(tab_act), "Go to Activity tab")
    shortcuts.add_shortcut("Control-w", lambda: nb.select(tab_water), "Go to Water tab")
    shortcuts.add_shortcut("Control-e", lambda: nb.select(tab_ex), "Go to Export tab")
    shortcuts.add_shortcut("Control-a", lambda: nb.select(tab_advanced), "Go to Advanced tab")
    shortcuts.add_shortcut("Control-t", switch_theme, "Toggle light/dark theme")
    shortcuts.add_shortcut("Control-d", quick_demo_header, "Generate quick demo data")
    shortcuts.add_shortcut("Control-1", lambda: quick_add_enhanced(250), "Add 250ml water")
    shortcuts.add_shortcut("Control-2", lambda: quick_add_enhanced(500), "Add 500ml water")
    
    # Setup auto-refresh system
    auto_refresh_callbacks = {
        'dashboard': {
            'callback': refresh_dashboard,
            'interval': 60,  # Refresh every minute
            'priority': 'normal'
        },
        'insights': {
            'callback': generate_insights,
            'interval': 300,  # Refresh every 5 minutes
            'priority': 'low'
        }
    }
    
    # Configure auto-refresh
    for name, config in auto_refresh_callbacks.items():
        auto_refresh.add_callback(
            name,
            config['callback'],
            config['interval'],
            config['priority']
        )
    
    # Start auto-refresh
    auto_refresh.start()
    
    # Show welcome notification
    root.after(1000, lambda: show_smart_toast(
        root, 
        "Welcome to NovaFit Plus!", 
        "Your enhanced health dashboard is ready. Try the new features!",
        "info",
        duration=4000
    ))
    
    root.mainloop()
    
    # Cleanup on exit
    auto_refresh.stop()

if __name__ == "__main__":
    main()
