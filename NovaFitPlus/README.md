# 🏃‍♂️ NovaFit Plus

> **A comprehensive health and fitness tracking application with both CLI and GUI interfaces**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GUI: Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)

---

## 🚀 Quick Start

### **Option 1: One-Click Launch (Recommended)**
```bash
# Windows
.\start_gui.bat    # Launch GUI
.\start_cli.bat    # Launch CLI

# macOS/Linux  
./start_gui.sh     # Launch GUI
./start_cli.sh     # Launch CLI
```

### **Option 2: Manual Setup**
```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python -m novafit_plus.ui_tk    # GUI
python -m novafit_plus.app      # CLI
```

---

## 📱 What is NovaFit Plus?

NovaFit Plus is your **all-in-one health companion** that helps you:

- 📊 **Track daily activities** (steps, calories, mood, sleep)
- 💧 **Monitor hydration** with smart daily goals
- 🌤️ **Integrate weather data** for better health insights
- 📈 **Analyze your progress** with detailed charts and reports
- 🎯 **Stay motivated** with achievements and health scores

**Two ways to use it:**
- 🖥️ **Command Line (CLI)**: Fast, keyboard-driven interface
- 🖼️ **Graphical (GUI)**: Visual, mouse-friendly interface

---

## ✨ Key Features

### 🏃 **Activity & Health Tracking**
- Daily steps, calories, and mood logging
- Sleep hours monitoring with 8-hour target analysis
- **Health Score (0-100)** combining all your metrics
- BMI and BMR calculations with calorie recommendations

### 💧 **Smart Hydration**
- Personalized daily water goals based on your weight and activity
- Quick-add buttons for common drink sizes
- Weather-adjusted hydration recommendations
- Detailed hydration analytics and adherence tracking

### 🌤️ **Weather Integration**
- Real-time weather data (no API key needed!)
- Global city support
- Weather-based health recommendations
- Automatic hydration goal adjustments

### 📊 **Analytics & Insights**
- Weekly and monthly trend analysis
- Progress charts and visualizations
- Health insights and recommendations
- Goal achievement tracking

### 📈 **Data Export**
- Professional Excel reports with multiple sheets
- JSON exports for data analysis
- Comprehensive health summaries
- Backup and data portability

### 🎮 **Gamification**
- Achievement system for health goals
- User levels based on consistent tracking
- Points and rewards for healthy habits
- Progress milestones and celebrations

---

## 🖥️ User Interfaces

### **CLI Interface - For Power Users**
```
┌─────────────────────────────────┐
│          NovaFit Plus           │
├─────────────────────────────────┤
│ 1) Setup Profile                │
│ 2) Log Activity                 │
│ 3) Log Water Intake             │
│ 4) View Dashboard               │
│ 5) Get Weather                  │
│ 6) View Analytics               │
│ 7) Export Data                  │
│ 8) Generate Demo Data           │
│ 0) Exit                         │
└─────────────────────────────────┘
```

### **GUI Interface - Visual & Intuitive**
- **Dashboard**: Overview of all your metrics
- **Activity**: Log workouts and daily activities  
- **Water**: Track hydration with visual progress
- **Weather**: Manage weather settings and forecasts
- **Analytics**: Charts, graphs, and trend analysis
- **Export**: Generate reports and export data
- **Profile**: Manage your personal information
- **Advanced**: App settings and data management

---

## 🏗️ Project Structure

```
NovaFitPlus/
├── 📱 start_gui.bat/.sh        # One-click GUI launcher
├── 🖥️ start_cli.bat/.sh        # One-click CLI launcher
├── 📋 requirements.txt          # Python dependencies
├── 📄 README.md                 # This file
├── ⚙️ config.json              # App configuration
│
├── 📦 novafit_plus/            # Main application
│   ├── 🖼️ ui_tk.py             # GUI interface
│   ├── 🖥️ app.py               # CLI interface
│   ├── 💾 db.py                # Database operations
│   ├── 👤 profile.py           # User management
│   ├── 💧 hydration.py         # Water tracking
│   ├── 🌤️ weather.py           # Weather integration
│   ├── 📊 analysis.py          # Analytics engine
│   ├── 📈 export.py            # Data export
│   └── �� gamification.py      # Achievement system
│
├── 💾 data/                    # Your data (stays local!)
└── 📊 exports/                 # Generated reports
```

---

## 💾 Your Data & Privacy

### **🔒 Privacy First**
- **100% Local Storage**: All your data stays on YOUR device
- **No Cloud Sync**: No accounts, no servers, no data sharing
- **Complete Control**: Export, backup, or delete anytime

### **📊 Data Types**
- **User Profiles**: Age, height, weight, activity level
- **Activities**: Steps, calories, mood, sleep, notes
- **Hydration**: Water intake logs and daily goals
- **Weather**: Local weather data for health insights

---

## 🛠️ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.9+ | 3.11+ |
| **RAM** | 256 MB | 512 MB |
| **Storage** | 50 MB | 100 MB |
| **Display** | 1024x768 | 1280x720+ |

**Supported Platforms:**
- ✅ Windows 10/11
- ✅ macOS 10.15+  
- ✅ Linux (Ubuntu, Debian, etc.)

---

## 🎯 Example Usage

### **First Time Setup**
1. Run the app: `.\start_gui.bat`
2. Go to **Profile** tab
3. Enter your details (age, height, weight, etc.)
4. Set your location for weather data

### **Daily Routine**
1. **Morning**: Log yesterday's sleep hours
2. **Throughout day**: Add water intake as you drink
3. **Evening**: Log steps, mood, and any notes
4. **Weekly**: Check analytics to see your progress

### **Weekly Review**
1. Go to **Analytics** tab
2. Review your health score trends
3. Check hydration adherence
4. Export data for deeper analysis

---

## 🐛 Troubleshooting

### **Common Issues**

| Problem | Solution |
|---------|----------|
| App won't start | Run `pip install -r requirements.txt` |
| Database errors | Check `data/` folder permissions |
| GUI looks weird | Update Python, check display scaling |
| Weather not working | Verify internet connection |

### **Need Help?**
1. Check error messages carefully
2. Verify Python version: `python --version`
3. Ensure all dependencies installed
4. Try running manually: `python -m novafit_plus.ui_tk`

---

## 🎨 Customization

### **Themes**
Edit `theme_config.json` to customize:
- Light/Dark mode
- Color schemes  
- UI elements

### **Settings**
Edit `config.json` to change:
- Default city/country
- Database location
- Export directory

---

## 🤝 Contributing & Support

### **Contributing**
We welcome contributions! You can help by:
- 🐛 Reporting bugs
- 💡 Suggesting features  
- 📝 Improving documentation
- 🔧 Submitting code improvements

### **Built With**
- **Python 3.9+** - Core language
- **Tkinter** - GUI framework
- **SQLite** - Local database
- **Open-Meteo API** - Weather data
- **Faker** - Demo data generation

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

---

<div align="center">

**🏃‍♂️ NovaFit Plus** - *Your personal health companion*

*Made with ❤️ for a healthier you*

[⭐ Star this project](https://github.com) • [🐛 Report Bug](https://github.com) • [💡 Request Feature](https://github.com)

</div>
