import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from typing import Optional
from .utils import load_config, today_iso
from .db import get_user, daily_water_total, add_water_intake, weather_on_date, insert_weather, upsert_activity, upsert_user, tail
from .db import migrate_schema, sleep_on_date
from .profile import bmi, bmr_mifflin, maintenance_calories
from .hydration import daily_water_goal_ml
from . import weather as wz
from .analysis import kpis, best_running_days, hydration_adherence, sleep_stats, health_score
from .export import export_json, export_excel, export_csv
from .reports import chart_hydration, chart_steps_vs_sleep

def _ensure(db):
    migrate_schema(db)

def dashboard_text(db, user):
    u = get_user(db, user) or (None, user, 30, "M", 166, 66, "light")
    _, name, age, sex, h, w, al = u
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

    root = tk.Tk()
    root.title("NovaFit Plus — GUI")
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass
    base_font = tkfont.nametofont('TkDefaultFont'); base_font.configure(size=10)
    title_font = tkfont.Font(family=base_font.actual('family'), size=12, weight='bold')
    style.configure('Title.TLabel', font=title_font)
    # Simple color accents
    style.configure('Accent.Horizontal.TProgressbar', troughcolor='#E6E6E6')
    style.configure('Health.Horizontal.TProgressbar', troughcolor='#E6E6E6')

    def apply_theme(mode='light'):
        if mode == 'dark':
            root.configure(bg='#1e1e1e')
            style.configure('.', background='#1e1e1e', foreground='#f2f2f2')
            style.configure('TLabel', background='#1e1e1e', foreground='#f2f2f2')
            style.configure('TFrame', background='#1e1e1e')
            style.configure('TNotebook', background='#1e1e1e')
            style.configure('TNotebook.Tab', background='#333333', foreground='#f2f2f2')
        else:
            root.configure(bg='SystemButtonFace')
            style.configure('.', background='SystemButtonFace', foreground='black')
            style.configure('TLabel', background='SystemButtonFace', foreground='black')
            style.configure('TFrame', background='SystemButtonFace')
            style.configure('TNotebook', background='SystemButtonFace')
            style.configure('TNotebook.Tab', background='SystemButtonFace', foreground='black')
    apply_theme('light')

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)

    user_var = tk.StringVar(value=default_user)

    # Dashboard
    tab_dash = ttk.Frame(nb, padding=10); nb.add(tab_dash, text="Dashboard")
    top_dash = ttk.Frame(tab_dash); top_dash.pack(fill="x")
    ttk.Label(top_dash, text="User:").pack(side="left")
    ttk.Entry(top_dash, textvariable=user_var, width=20).pack(side="left", padx=6)

    ttk.Label(tab_dash, text='Overview', style='Title.TLabel').pack(anchor='w')
    dash_text = tk.Text(tab_dash, width=100, height=14, wrap="word"); dash_text.pack(fill="both", expand=True, pady=8)

    hyd_frame = ttk.Frame(tab_dash); hyd_frame.pack(fill="x")
    ttk.Label(hyd_frame, text="Hydration % (today)").pack(side="left", padx=6)
    pb = ttk.Progressbar(hyd_frame, maximum=100, length=300); pb.pack(side="left", padx=6)
    lbl_pb = ttk.Label(hyd_frame, text="0%"); lbl_pb.pack(side="left", padx=6)

    sleep_frame = ttk.Frame(tab_dash); sleep_frame.pack(fill="x", pady=4)
    ttk.Label(sleep_frame, text="Weekly Sleep % (vs 8h)").pack(side="left", padx=6)
    sleep_pb = ttk.Progressbar(sleep_frame, maximum=120, length=300); sleep_pb.pack(side="left", padx=6)
    lbl_sleep = ttk.Label(sleep_frame, text="0%"); lbl_sleep.pack(side="left", padx=6)

    score_frame = ttk.Frame(tab_dash); score_frame.pack(fill="x", pady=4)
    ttk.Label(score_frame, text="Health Score (7d)").pack(side="left", padx=6)
    health_pb = ttk.Progressbar(score_frame, maximum=100, length=200, style='Health.Horizontal.TProgressbar')
    health_pb.pack(side="left", padx=6)
    lbl_score = ttk.Label(score_frame, text="--"); lbl_score.pack(side="left", padx=6)

    theme_frame = ttk.Frame(tab_dash); theme_frame.pack(fill='x', pady=6)
    ttk.Label(theme_frame, text='Theme:').pack(side='left', padx=6)
    ttk.Button(theme_frame, text='Light', command=lambda: apply_theme('light')).pack(side='left', padx=2)
    ttk.Button(theme_frame, text='Dark', command=lambda: apply_theme('dark')).pack(side='left', padx=2)

    def refresh_dashboard():
        text, total, goal = dashboard_text(db, user_var.get().strip() or default_user)
        dash_text.delete("1.0", tk.END); dash_text.insert(tk.END, text)
        pct = 0 if goal <= 0 else int(total*100/goal)
        pb["value"] = pct; lbl_pb.config(text=f"{pct}%")
        w7 = sleep_stats(db, user_var.get().strip() or default_user, days=7)
        sleep_pct = int(w7["percent_vs_8h"]) if w7 else 0
        sleep_pb["value"] = sleep_pct; lbl_sleep.config(text=f"{sleep_pct}%")
        u = get_user(db, user_var.get().strip() or default_user) or (None, default_user, 30, 'M', 166, 66, 'light')
        _, _, _, _, h, w, _ = u
        hs = health_score(db, user_var.get().strip() or default_user, w, h, days=7)
        health_pb['value'] = int(hs['score'])
        lbl_score.config(text=f"{hs['score']}")

    btns = ttk.Frame(tab_dash); btns.pack(fill="x", pady=6)
    def quick_add(ml):
        add_water_intake(db, user_var.get().strip() or default_user, today_iso(), ml, "gui")
        refresh_dashboard()
    ttk.Button(btns, text="Refresh", command=refresh_dashboard).pack(side="left", padx=4)
    ttk.Button(btns, text="Water +250 ml", command=lambda: quick_add(250)).pack(side="left", padx=4)
    ttk.Button(btns, text="Water +500 ml", command=lambda: quick_add(500)).pack(side="left", padx=4)
    ttk.Button(btns, text="Fetch Today's Weather", command=lambda: fetch_today_weather(db, cfg, refresh_dashboard)).pack(side="right", padx=4)

    # Activity tab
    tab_act = ttk.Frame(nb, padding=10); nb.add(tab_act, text="Activity")
    act_grid = ttk.Frame(tab_act); act_grid.pack(fill="x")
    steps_var = tk.StringVar(); cals_var = tk.StringVar(); mood_var = tk.StringVar(value="3"); notes_var = tk.StringVar(); sleep_var = tk.StringVar()
    for i, (label, var) in enumerate([("Steps", steps_var), ("Calories", cals_var), ("Mood (1-5)", mood_var), ("Sleep hours", sleep_var)]):
        ttk.Label(act_grid, text=label).grid(row=0, column=2*i, sticky="e", padx=4, pady=4)
        ttk.Entry(act_grid, textvariable=var, width=10).grid(row=0, column=2*i+1, sticky="w", padx=4, pady=4)
    ttk.Label(tab_act, text="Notes").pack(anchor="w")
    ent_notes = ttk.Entry(tab_act, textvariable=notes_var, width=80); ent_notes.pack(fill="x")

    def save_activity():
        try:
            steps = int(steps_var.get() or 0)
            cals = int(cals_var.get() or 0)
            mood = int(mood_var.get() or 3); mood = max(1, min(5, mood))
            sleep = float(sleep_var.get() or 0.0)
            upsert_activity(db, user_var.get().strip() or default_user, today_iso(), steps, cals, mood, notes_var.get().strip(), sleep)
            messagebox.showinfo("Saved", "Activity saved.")
            refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    ttk.Button(tab_act, text="Save Today's Activity", command=save_activity).pack(pady=8)

    # Water tab
    tab_water = ttk.Frame(nb, padding=10); nb.add(tab_water, text="Water")
    ttk.Label(tab_water, text="Quick add:").pack(anchor="w")
    wbtns = ttk.Frame(tab_water); wbtns.pack(anchor="w", pady=4)
    for ml in (250, 500, 750):
        ttk.Button(wbtns, text=f"+{ml} ml", command=lambda m=ml: quick_add(m)).pack(side="left", padx=4)
    cust_var = tk.StringVar()
    ttk.Entry(tab_water, textvariable=cust_var, width=10).pack(side="left", padx=4)
    ttk.Button(tab_water, text="Add custom ml", command=lambda: (quick_add(int(cust_var.get() or 0)))).pack(side="left", padx=4)

    # Weather tab
    tab_w = ttk.Frame(nb, padding=10); nb.add(tab_w, text="Weather")
    city_var = tk.StringVar(value=cfg.get("default_city", "")); country_var = tk.StringVar(value=cfg.get("default_country","")); days_var = tk.StringVar(value="3")
    for i, (label, var) in enumerate([("City", city_var), ("Country", country_var), ("Days (1-7)", days_var)]):
        ttk.Label(tab_w, text=label).grid(row=0, column=2*i, sticky="e", padx=4, pady=4)
        ttk.Entry(tab_w, textvariable=var, width=16).grid(row=0, column=2*i+1, sticky="w", padx=4, pady=4)
    ttk.Button(tab_w, text="Fetch Forecast", command=lambda: fetch_forecast(db, city_var.get(), country_var.get(), days_var.get())).grid(row=1, column=0, columnspan=6, pady=6)

    # Insights tab
    tab_ins = ttk.Frame(nb, padding=10); nb.add(tab_ins, text='Insights')
    tf_var = tk.StringVar(value='7')
    rb_frame = ttk.Frame(tab_ins); rb_frame.pack(fill='x')
    ttk.Label(rb_frame, text='Health Score period:').pack(side='left', padx=6)
    ttk.Radiobutton(rb_frame, text='7 days', variable=tf_var, value='7').pack(side='left', padx=4)
    ttk.Radiobutton(rb_frame, text='30 days', variable=tf_var, value='30').pack(side='left', padx=4)

    txt_ins = tk.Text(tab_ins, width=100, height=14, wrap='word'); txt_ins.pack(fill='both', expand=True, pady=8)

    qa = ttk.Frame(tab_ins); qa.pack(fill='x')
    ttk.Label(qa, text='Quick actions:').pack(side='left', padx=6)
    ttk.Button(qa, text='+250 ml', command=lambda: (add_water_intake(db, user_var.get().strip() or default_user, today_iso(), 250, 'insight'), refresh_dashboard(), generate_insights())).pack(side='left', padx=2)
    ttk.Button(qa, text='+500 ml', command=lambda: (add_water_intake(db, user_var.get().strip() or default_user, today_iso(), 500, 'insight'), refresh_dashboard(), generate_insights())).pack(side='left', padx=2)
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
        u = get_user(db, user_var.get().strip() or default_user) or (None, default_user, 30, 'M', 166, 66, 'light')
        _, _, _, _, h, w, al = u
        # Health score
        hs = health_score(db, user_var.get().strip() or default_user, w, h, days=period)
        score = hs.get('score', 0)
        if score >= 85: band = 'Excellent'
        elif score >= 70: band = 'Good'
        elif score >= 50: band = 'Fair'
        else: band = 'Needs attention'
        # Hydration insight
        from .hydration import hydration_progress
        prog = hydration_progress(db, user_var.get().strip() or default_user, today_iso(), w)
        hyd_pct = 0 if prog['goal_ml'] <= 0 else int(prog['total_ml']*100/prog['goal_ml'])
        hyd_ins = 'On track for hydration today.' if hyd_pct >= 100 else f"Drink {prog['remaining_ml']} ml more to reach today's goal."
        # Sleep insight (weekly)
        ss7 = sleep_stats(db, user_var.get().strip() or default_user, days=7)
        sleep_ins = 'Sleep average meets target.' if ss7['percent_vs_8h'] >= 100 else f"Avg {ss7['avg_hours']}h (vs 8h). Aim +{round(max(0,8-ss7['avg_hours'])*60)} min/night."
        # Steps trend insight
        kp = kpis(db, user_var.get().strip() or default_user, 7)
        st = int(kp.get('steps_movavg_7d_last') or 0)
        steps_ins = 'Great step trend.' if st >= 10000 else f"7d avg {st} steps. Consider a 3k–5k walk to boost."
        # Weather-based tip
        wrow = weather_on_date(db, today_iso())
        wx_ins = 'Weather not saved for today.' if not wrow else ( 'Hot day — prioritize water.' if (wrow[0] and wrow[0] > 30) else 'Weather is mild — good for outdoor activity.' )
        # Compose text
        lines = [
            f"Health Score ({period}d): {score} ({band})",
            f"Hydration: {hyd_ins}",
            f"Sleep: {sleep_ins}",
            f"Steps: {steps_ins}",
            f"Weather: {wx_ins}",
        ]
        txt_ins.delete('1.0', tk.END); txt_ins.insert(tk.END, '\n'.join(lines))

    ttk.Button(tab_ins, text='Generate insights', command=generate_insights).pack(anchor='w', pady=6)

    # Analytics tab
    tab_an = ttk.Frame(nb, padding=10); nb.add(tab_an, text="Analytics")
    days_an_var = tk.StringVar(value="14")
    ttk.Label(tab_an, text="Analyze last N days:").pack(anchor="w")
    ttk.Entry(tab_an, textvariable=days_an_var, width=10).pack(anchor="w")
    txt_an = tk.Text(tab_an, width=100, height=16, wrap="word"); txt_an.pack(fill="both", expand=True, pady=8)

    def run_analytics():
        try:
            days = int(days_an_var.get() or 14)
            res = kpis(db, user_var.get().strip() or default_user, days)
            lines = [f"KPIs: {res}"]
            lines.append("Best running days:")
            for d, cond, score in best_running_days(db, days):
                lines.append(f"  {d} — {cond} — Score {score}")
            lines.append("Hydration adherence (7 days):")
            u = get_user(db, user_var.get().strip() or default_user) or (None, default_user, 30, "M", 166, 66, "light")
            _, _, _, _, h, w, _ = u
            rep = hydration_adherence(db, user_var.get().strip() or default_user, w, days=7)
            for row in rep:
                lines.append(f"  {row}")
            hs = health_score(db, user_var.get().strip() or default_user, w, h, days=7)
            lines.append(f"Health Score (7d): {hs}")
            txt_an.delete('1.0', tk.END); txt_an.insert(tk.END, "\n".join(lines))
        except Exception as e:
            messagebox.showerror("Error", str(e))
    ttk.Button(tab_an, text="Run Analytics", command=run_analytics).pack(anchor="w")

    # Reports tab
    tab_rep = ttk.Frame(nb, padding=10); nb.add(tab_rep, text="Reports")
    rep_days_var = tk.StringVar(value="14")
    ttk.Label(tab_rep, text="Days:").pack(anchor='w')
    ttk.Entry(tab_rep, textvariable=rep_days_var, width=10).pack(anchor='w')
    txt_rep = tk.Text(tab_rep, width=100, height=16, wrap='word'); txt_rep.pack(fill='both', expand=True, pady=8)
    img_label = ttk.Label(tab_rep); img_label.pack()
    def gen_charts():
        try:
            days = int(rep_days_var.get() or 14)
            u = get_user(db, user_var.get().strip() or default_user) or (None, default_user, 30, 'M', 166, 66, 'light')
            _, _, _, _, h, w, _ = u
            p1 = chart_hydration(db, user_var.get().strip() or default_user, w, days)
            p2 = chart_steps_vs_sleep(db, user_var.get().strip() or default_user, days)
            txt_rep.delete('1.0', tk.END); txt_rep.insert(tk.END, f"Charts saved:\n{p1}\n{p2}")
            # Try to preview the last chart
            try:
                from tkinter import PhotoImage
                img = PhotoImage(file=p1)
                img_label.configure(image=img)
                img_label.image = img
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror('Error', str(e))
    ttk.Button(tab_rep, text="Generate charts", command=gen_charts).pack(anchor='w', pady=6)

    # Export tab
    tab_ex = ttk.Frame(nb, padding=10); nb.add(tab_ex, text="Export")
    def do_export_json():
        out = export_json(db, cfg["export_dir"], user_var.get().strip() or default_user, days=14)
        messagebox.showinfo("Export", f"JSON exported: {out}")
    def do_export_xlsx():
        out = export_excel(db, cfg["export_dir"], user_var.get().strip() or default_user, days=14)
        messagebox.showinfo("Export", f"Excel exported: {out}")
    ttk.Button(tab_ex, text="Export JSON", command=do_export_json).pack(anchor="w", pady=4)
    ttk.Button(tab_ex, text="Export Excel", command=do_export_xlsx).pack(anchor="w", pady=4)
    def do_export_csv():
        outs = export_csv(db, cfg["export_dir"], user_var.get().strip() or default_user, days=14)
        messagebox.showinfo("Export", f"CSV exported: {outs}")
    ttk.Button(tab_ex, text="Export CSV", command=do_export_csv).pack(anchor="w", pady=4)

    # Profile tab
    tab_prof = ttk.Frame(nb, padding=10); nb.add(tab_prof, text="Profile")
    name_var = tk.StringVar(value=default_user); age_var = tk.StringVar(value="30"); sex_var = tk.StringVar(value="M"); ht_var = tk.StringVar(value="166"); wt_var = tk.StringVar(value="66"); actl_var = tk.StringVar(value="light")
    grid = ttk.Frame(tab_prof); grid.pack(fill="x")
    for i, (lab, var) in enumerate([("Name", name_var), ("Age", age_var), ("Sex", sex_var), ("Height cm", ht_var), ("Weight kg", wt_var), ("Activity level", actl_var)]):
        ttk.Label(grid, text=lab).grid(row=i, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(grid, textvariable=var, width=20).grid(row=i, column=1, sticky="w", padx=4, pady=4)
    def save_profile():
        try:
            upsert_user(db, name_var.get().strip() or default_user, int(age_var.get() or 30), sex_var.get().strip() or "M", float(ht_var.get() or 166), float(wt_var.get() or 66), actl_var.get().strip() or "light")
            user_var.set(name_var.get().strip() or default_user)
            messagebox.showinfo("Saved", "Profile updated.")
            refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    ttk.Button(tab_prof, text="Save Profile", command=save_profile).pack(anchor="w", pady=6)

    # Helpers
    def fetch_today_weather(db, cfg, cb):
        try:
            lat, lon, cname = wz.geocode_city(cfg["default_city"], cfg["default_country"])
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

    def fetch_forecast(db, city, country, days):
        try:
            days = max(1, min(int(days or 1), 7))
            lat, lon, cname = wz.geocode_city(city, country)
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
        except Exception as e:
            messagebox.showerror("Error", str(e))

    refresh_dashboard()
    root.mainloop()

if __name__ == "__main__":
    main()
