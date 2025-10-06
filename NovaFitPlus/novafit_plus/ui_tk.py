import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from typing import Optional
import datetime as _dt
from .utils import load_config, today_iso
from .db import get_user, daily_water_total, add_water_intake, weather_on_date, insert_weather, upsert_activity, upsert_user, tail
from .db import migrate_schema, sleep_on_date
from .profile import bmi, bmr_mifflin, maintenance_calories
from .hydration import daily_water_goal_ml
from . import weather as wz
from .analysis import kpis, best_running_days, hydration_adherence, sleep_stats, health_score
from .export import export_json, export_excel, export_csv
from .reports import chart_hydration, chart_steps_vs_sleep


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
    wrow = weather_on_date(db, today_iso())
    sleep = sleep_on_date(db, user, today_iso())
    w7 = sleep_stats(db, user, days=7)
    w30 = sleep_stats(db, user, days=30)
    hs = health_score(db, user, w, h, days=7)

    lines = [
        f"User: {name} | Age: {age} | Sex: {sex} | Activity: {al}",
        (f"Location: {', '.join([part for part in (city, country) if part])}" if (city or country) else "Location: not set"),
        f"Height: {h} cm | Weight: {w} kg | BMI: {b} ({cat})",
        f"BMR: {bmr} kcal | Maintenance: {maint} kcal",
        f"Hydration: {total}/{goal} ml",
        f"Sleep today: {sleep} h",
        f"Weekly sleep vs 8h: {w7['percent_vs_8h']}% | Monthly: {w30['percent_vs_8h']}%",
        f"Health Score (7d): {hs['score']} / 100",
    ]
    if wrow:
        tmax, tmin, hum, wind, cond, city = wrow
        lines.append(f"Today's weather [{city}]: max {tmax}°C, min {tmin}°C, humidity {hum}%, wind {wind} km/h, {cond}")
    else:
        lines.append("Today's weather: not found.")
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
            'status_bg': '#e5e7eb'
        },
        'dark': {
            'bg': '#121820',
            'fg': '#e5efff',
            'muted': '#9baec8',
            'accent': '#60a5fa',
            'panel_bg': '#19212b',
            'card_bg': '#1f2933',
            'health': '#34d399',
            'sleep': '#a78bfa',
            'status_bg': '#111827'
        }
    }
    text_widgets = []
    status_widgets = []
    theme_state = {'mode': 'light'}

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
        for txt in text_widgets:
            txt.configure(bg=palette['panel_bg'], fg=palette['fg'], insertbackground=palette['fg'])
        for status in status_widgets:
            status.configure(bg=palette['status_bg'], fg=palette['muted'])

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

    main_container = ttk.Frame(root, padding=(16, 14), style='Header.TFrame')
    main_container.pack(fill="both", expand=True)

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
    for idx in range(5):
        cards_frame.columnconfigure(idx, weight=1)

    def create_stat_card(column: int, title_text: str, var: tk.StringVar):
        frame = ttk.Frame(cards_frame, style='Card.TFrame', padding=(16, 14))
        frame.grid(row=0, column=column, sticky="nsew", padx=6)
        ttk.Label(frame, text=title_text, style='CardTitle.TLabel').pack(anchor="w")
        ttk.Label(frame, textvariable=var, style='CardValue.TLabel').pack(anchor="w", pady=(6, 0))

    create_stat_card(0, "Hydration Today", hydration_summary_var)
    create_stat_card(1, "Sleep vs Target", sleep_summary_var)
    create_stat_card(2, "Health Score", score_summary_var)
    create_stat_card(3, "7-day Steps", steps_summary_var)
    create_stat_card(4, "Avg Calories", calories_summary_var)

    ttk.Separator(main_container, orient='horizontal').pack(fill="x", pady=(4, 12))

    nb = ttk.Notebook(main_container)
    nb.pack(fill="both", expand=True)

    tab_dash = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_dash, text="Dashboard")
    top_dash = ttk.Frame(tab_dash, style='Panel.TFrame')
    top_dash.pack(fill="x")
    ttk.Label(top_dash, text="User:", style='PanelHeading.TLabel').pack(side="left")
    ttk.Entry(top_dash, textvariable=user_var, width=20).pack(side="left", padx=6)

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
    hyd_frame = ttk.Frame(metrics_frame, style='Panel.TFrame')
    hyd_frame.pack(fill="x")
    ttk.Label(hyd_frame, text="Hydration % (today)", style='PanelHeading.TLabel').pack(side="left", padx=6)
    pb = ttk.Progressbar(hyd_frame, maximum=100, length=300, style='Accent.Horizontal.TProgressbar')
    pb.pack(side="left", padx=6)
    lbl_pb = ttk.Label(hyd_frame, text="0%", style='PanelBody.TLabel')
    lbl_pb.pack(side="left", padx=6)

    sleep_frame = ttk.Frame(metrics_frame, style='Panel.TFrame')
    sleep_frame.pack(fill="x", pady=4)
    ttk.Label(sleep_frame, text="Weekly Sleep % (vs 8h)", style='PanelHeading.TLabel').pack(side="left", padx=6)
    sleep_pb = ttk.Progressbar(sleep_frame, maximum=120, length=300, style='Sleep.Horizontal.TProgressbar')
    sleep_pb.pack(side="left", padx=6)
    lbl_sleep = ttk.Label(sleep_frame, text="0%", style='PanelBody.TLabel')
    lbl_sleep.pack(side="left", padx=6)

    score_frame = ttk.Frame(metrics_frame, style='Panel.TFrame')
    score_frame.pack(fill="x", pady=4)
    ttk.Label(score_frame, text="Health Score (7d)", style='PanelHeading.TLabel').pack(side="left", padx=6)
    health_pb = ttk.Progressbar(score_frame, maximum=100, length=240, style='Health.Horizontal.TProgressbar')
    health_pb.pack(side="left", padx=6)
    lbl_score = ttk.Label(score_frame, text="--", style='PanelBody.TLabel')
    lbl_score.pack(side="left", padx=6)

    btns = ttk.Frame(tab_dash, style='Panel.TFrame')
    btns.pack(fill="x", pady=6)
    def quick_add(ml: int, date_input: Optional[str] = None, source: str = "gui"):
        try:
            chosen_date = resolve_date_value(date_input if date_input is not None else today_iso())
        except ValueError as err:
            messagebox.showerror("Invalid date", str(err))
            return
        add_water_intake(db, user_var.get().strip() or default_user, chosen_date, ml, source)
        refresh_dashboard()
    ttk.Button(btns, text="Water +250 ml", style='Accent.TButton', command=lambda: quick_add(250)).pack(side="left", padx=4)
    ttk.Button(btns, text="Water +500 ml", style='Accent.TButton', command=lambda: quick_add(500)).pack(side="left", padx=4)
    ttk.Button(
        btns,
        text="Fetch Today's Weather",
        command=lambda: fetch_today_weather(
            db,
            cfg,
            user_var.get().strip() or default_user,
            refresh_dashboard,
        ),
    ).pack(side="right", padx=4)

    def refresh_dashboard():
        user_name = user_var.get().strip() or default_user
        text, total, goal = dashboard_text(db, user_name)
        dash_text.delete("1.0", tk.END)
        dash_text.insert(tk.END, text)
        pct = 0 if goal <= 0 else int(total * 100 / goal)
        pb["value"] = min(pct, 100)
        lbl_pb.config(text=f"{pct}%")
        hydration_summary_var.set(
            f"{pct}% • {total} ml / {goal} ml" if goal > 0 else f"{total} ml logged"
        )
        if goal > 0 and total < goal:
            hydration_tip_var.set(f"Drink {goal - total} ml more to meet today's goal.")
        elif goal > 0:
            hydration_tip_var.set("Hydration goal achieved — amazing!")
        else:
            hydration_tip_var.set("Set a water goal in your profile to unlock guidance.")

        w7 = sleep_stats(db, user_name, days=7)
        sleep_pct = int(w7["percent_vs_8h"]) if w7 else 0
        sleep_pb["value"] = min(sleep_pct, 120)
        lbl_sleep.config(text=f"{sleep_pct}%")
        avg_sleep = w7.get("avg_hours", 0) if w7 else 0
        sleep_summary_var.set(f"{sleep_pct}% • avg {avg_sleep} h")
        if sleep_pct >= 100:
            sleep_tip_var.set("Great rest pattern — keep it consistent tonight.")
        elif avg_sleep:
            sleep_tip_var.set(f"Add {round(max(0, 8 - avg_sleep), 1)} h nightly to reach the target.")
        else:
            sleep_tip_var.set("Log sleep to unlock tailored tips.")

        u = get_user(db, user_name) or _default_profile(user_name)
        _, name, _, _, h, w, _, city, _ = u
        hs = health_score(db, user_name, w, h, days=7)
        score_val = int(hs.get('score', 0))
        health_pb['value'] = score_val
        lbl_score.config(text=f"{score_val}")
        score_summary_var.set(f"{score_val} pts / 100")
        components = hs.get('components', {})
        score_breakdown_var.set(
            " • ".join([
                f"Steps {components.get('steps_score', 0)}",
                f"Hydration {components.get('hydration_score', 0)}",
                f"Sleep {components.get('sleep_score', 0)}",
                f"Mood {components.get('mood_score', 0)}"
            ])
        )

        kpi_data = kpis(db, user_name, 7)
        if isinstance(kpi_data, dict) and 'message' not in kpi_data:
            steps_mov = kpi_data.get('steps_movavg_7d_last') or 0
            steps_summary_var.set(f"{int(round(steps_mov)):,} avg steps")
            cal_avg = kpi_data.get('calories_avg') or 0
            calories_summary_var.set(f"{int(round(cal_avg))} kcal / day")
        else:
            steps_summary_var.set("Log steps to see trends")
            calories_summary_var.set("Calories data pending")

        wrow = weather_on_date(db, today_iso())
        if wrow:
            tmax, tmin, hum, wind, cond, city_name = wrow
            weather_tip_var.set(
                f"{city_name}: {tmax}°C high / {tmin}°C low, humidity {hum}% — {cond}."
            )
        elif city:
            weather_tip_var.set(f"Fetch today's weather for {city} to personalize hydration.")
        else:
            weather_tip_var.set("Add your city to the profile for weather-aware advice.")

        today_summary_var.set(f"{name}, you're {pct}% to your hydration goal today.")
        subtitle_var.set(f"{name}'s dashboard refreshed.")
        status_var.set(f"Last refreshed at {_dt.datetime.now().strftime('%H:%M:%S')}")

    # 🏃 Activity tab
    tab_act = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_act, text="Activity")
    ttk.Label(tab_act, text="Daily Activity Log", style='PanelHeading.TLabel').pack(anchor='w')
    act_grid = ttk.Frame(tab_act, style='Panel.TFrame')
    act_grid.pack(fill="x", pady=(8, 4))
    act_grid.columnconfigure((1, 3, 5, 7), weight=1)
    act_date_var = tk.StringVar(value=today_iso())
    ttk.Label(act_grid, text="Date (YYYY-MM-DD)", style='PanelBody.TLabel').grid(row=0, column=0, sticky="e", padx=4, pady=4)
    ttk.Entry(act_grid, textvariable=act_date_var, width=14).grid(row=0, column=1, sticky="w", padx=4, pady=4)
    steps_var = tk.StringVar(); cals_var = tk.StringVar(); mood_var = tk.StringVar(value="3"); notes_var = tk.StringVar(); sleep_var = tk.StringVar()
    for idx, (label, var) in enumerate([("Steps", steps_var), ("Calories", cals_var), ("Mood (1-5)", mood_var), ("Sleep hours", sleep_var)]):
        ttk.Label(act_grid, text=label, style='PanelBody.TLabel').grid(row=1, column=2*idx, sticky="e", padx=4, pady=4)
        ttk.Entry(act_grid, textvariable=var, width=12).grid(row=1, column=2*idx+1, sticky="we", padx=4, pady=4)
    ttk.Label(tab_act, text="Notes", style='PanelHeading.TLabel').pack(anchor="w", pady=(4, 0))
    ent_notes = ttk.Entry(tab_act, textvariable=notes_var, width=90)
    ent_notes.pack(fill="x")

    def save_activity():
        try:
            chosen_date = resolve_date_value(act_date_var.get())
            steps = int(steps_var.get() or 0)
            cals = int(cals_var.get() or 0)
            mood = int(mood_var.get() or 3); mood = max(1, min(5, mood))
            sleep = float(sleep_var.get() or 0.0)
            upsert_activity(db, user_var.get().strip() or default_user, chosen_date, steps, cals, mood, notes_var.get().strip(), sleep)
            messagebox.showinfo("Saved", f"Activity saved for {chosen_date}.")
            refresh_dashboard()
        except ValueError as err:
            messagebox.showerror("Invalid date", str(err))
        except Exception as e:
            messagebox.showerror("Error", str(e))
    ttk.Button(tab_act, text="Save Activity", style='Accent.TButton', command=save_activity).pack(pady=10, anchor='e')

    # 💧 Water tab
    tab_water = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_water, text="Water")
    ttk.Label(tab_water, text="Daily Hydration Helper", style='PanelHeading.TLabel').pack(anchor='w')
    water_date_var = tk.StringVar(value=today_iso())
    date_frame = ttk.Frame(tab_water, style='Panel.TFrame'); date_frame.pack(anchor="w", pady=6)
    ttk.Label(date_frame, text="Date (YYYY-MM-DD):", style='PanelBody.TLabel').pack(side="left", padx=4)
    ttk.Entry(date_frame, textvariable=water_date_var, width=14).pack(side="left", padx=4)
    ttk.Label(tab_water, text="Quick add", style='PanelBody.TLabel').pack(anchor="w")
    wbtns = ttk.Frame(tab_water, style='Panel.TFrame'); wbtns.pack(anchor="w", pady=4)
    for ml in (250, 500, 750):
        ttk.Button(wbtns, text=f"+{ml} ml", style='Accent.TButton', command=lambda m=ml: quick_add(m, water_date_var.get(), f"water-tab-{m}")).pack(side="left", padx=4)
    cust_var = tk.StringVar()
    cust_frame = ttk.Frame(tab_water, style='Panel.TFrame'); cust_frame.pack(anchor="w", pady=6)
    ttk.Entry(cust_frame, textvariable=cust_var, width=10).pack(side="left", padx=4)

    def add_custom_water():
        try:
            ml = int(cust_var.get() or 0)
        except ValueError:
            messagebox.showerror("Invalid amount", "Please enter milliliters as a number.")
            return
        quick_add(ml, water_date_var.get(), "water-tab-custom")
    ttk.Button(cust_frame, text="Add custom ml", command=add_custom_water).pack(side="left", padx=4)

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
    ttk.Button(qa, text='+250 ml', style='Accent.TButton', command=lambda: (add_water_intake(db, user_var.get().strip() or default_user, today_iso(), 250, 'insight'), refresh_dashboard(), generate_insights())).pack(side='left', padx=2)
    ttk.Button(qa, text='+500 ml', style='Accent.TButton', command=lambda: (add_water_intake(db, user_var.get().strip() or default_user, today_iso(), 500, 'insight'), refresh_dashboard(), generate_insights())).pack(side='left', padx=2)
    ttk.Button(qa, text='Prefill 30-min walk', command=lambda: prefill_walk()).pack(side='left', padx=2)

    def prefill_walk():
        try:
            steps_var.set('3000')
            cals_var.set('150')
            mood_var.set('4')
            notes_var.set('30-min walk')
            messagebox.showinfo('Prefilled', 'Activity fields prefilled for a 30-min walk. Go to the Activity tab to save.')
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
        wrow = weather_on_date(db, today_iso())
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

    header_buttons.columnconfigure((0, 1, 2, 3), weight=0)
    ttk.Button(header_buttons, text='Refresh View', style='Accent.TButton', command=lambda: (refresh_dashboard(), generate_insights())).grid(row=0, column=0, padx=4)
    ttk.Button(header_buttons, text='Toggle Theme', command=switch_theme).grid(row=0, column=1, padx=4)
    ttk.Button(header_buttons, text='Activity', command=lambda: nb.select(tab_act)).grid(row=0, column=2, padx=4)
    ttk.Button(header_buttons, text='Reports', command=lambda: nb.select(tab_rep)).grid(row=0, column=3, padx=4)

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
        except Exception as e:
            messagebox.showerror("Error", str(e))
    ttk.Button(tab_an, text="Run Analytics", style='Accent.TButton', command=run_analytics).pack(anchor="w")

    # 🖼️ Reports tab
    tab_rep = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_rep, text="Reports")
    rep_days_var = tk.StringVar(value="14")
    ttk.Label(tab_rep, text="Days:", style='PanelBody.TLabel').pack(anchor='w')
    ttk.Entry(tab_rep, textvariable=rep_days_var, width=10).pack(anchor='w')
    txt_rep = tk.Text(tab_rep, width=100, height=16, wrap='word', relief='flat', bd=0)
    txt_rep.pack(fill='both', expand=True, pady=8)
    text_widgets.append(txt_rep)
    img_label = ttk.Label(tab_rep, style='PanelBody.TLabel')
    img_label.pack()
    def gen_charts():
        try:
            days = int(rep_days_var.get() or 14)
            u = get_user(db, user_var.get().strip() or default_user) or _default_profile(default_user)
            _, _, _, _, h, w, _, _, _ = u
            p1 = chart_hydration(db, user_var.get().strip() or default_user, w, days)
            p2 = chart_steps_vs_sleep(db, user_var.get().strip() or default_user, days)
            txt_rep.delete('1.0', tk.END); txt_rep.insert(tk.END, f"Charts saved:\n{p1}\n{p2}")
            # 🖼️ Try to preview the last chart
            try:
                from tkinter import PhotoImage
                img = PhotoImage(file=p1)
                img_label.configure(image=img)
                img_label.image = img
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror('Error', str(e))
    ttk.Button(tab_rep, text="Generate charts", style='Accent.TButton', command=gen_charts).pack(anchor='w', pady=6)

    # 📤 Export tab
    tab_ex = ttk.Frame(nb, padding=16, style='Panel.TFrame'); nb.add(tab_ex, text="Export")
    ttk.Label(tab_ex, text="Share your data in seconds", style='PanelBody.TLabel').pack(anchor='w')
    def do_export_json():
        out = export_json(db, cfg["export_dir"], user_var.get().strip() or default_user, days=14)
        messagebox.showinfo("Export", f"JSON exported: {out}")
    def do_export_xlsx():
        out = export_excel(db, cfg["export_dir"], user_var.get().strip() or default_user, days=14)
        messagebox.showinfo("Export", f"Excel exported: {out}")
    ttk.Button(tab_ex, text="Export JSON", style='Accent.TButton', command=do_export_json).pack(anchor="w", pady=4)
    ttk.Button(tab_ex, text="Export Excel", style='Accent.TButton', command=do_export_xlsx).pack(anchor="w", pady=4)
    def do_export_csv():
        outs = export_csv(db, cfg["export_dir"], user_var.get().strip() or default_user, days=14)
        messagebox.showinfo("Export", f"CSV exported: {outs}")
    ttk.Button(tab_ex, text="Export CSV", style='Accent.TButton', command=do_export_csv).pack(anchor="w", pady=4)

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
            upsert_user(db, name, age, sex, height, weight, activity, city_val, country_val)
            user_var.set(name)
            actl_var.set(activity)
            city_prof_var.set(city_val)
            country_prof_var.set(country_val)
            city_var.set(city_val or cfg.get("default_city", ""))
            country_var.set(country_val or cfg.get("default_country", ""))
            messagebox.showinfo("Saved", "Profile updated.")
            refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    ttk.Button(tab_prof, text="Save Profile", style='Accent.TButton', command=save_profile).pack(anchor="w", pady=6)

    status_bar = tk.Label(root, textvariable=status_var, anchor="w", padx=14, pady=6)
    status_bar.pack(fill="x", side="bottom")
    status_widgets.append(status_bar)

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
            cb()
        except Exception as e:
            messagebox.showerror("Error", f"Weather fetch failed: {e}")

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
            messagebox.showinfo("Success", f"Weather saved for {cname} ({days} day(s)).")
            if callable(on_refresh):
                on_refresh()
            if callable(on_insights):
                on_insights()
            status_var.set("Forecast synced — dashboard and insights auto-refreshed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    apply_theme(theme_state['mode'])
    refresh_dashboard()
    generate_insights()
    root.mainloop()

if __name__ == "__main__":
    main()
