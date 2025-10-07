"""
Gamification System for NovaFit Plus
===================================
Advanced goal tracking and achievement system with rewards, streaks, and challenges.
Motivates users through game mechanics while promoting healthy habits.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable
import datetime as dt
import json
from dataclasses import dataclass, asdict
from enum import Enum

class GoalType(Enum):
    HYDRATION = "hydration"
    STEPS = "steps"
    SLEEP = "sleep"
    CALORIES = "calories"
    STREAK = "streak"
    CHALLENGE = "challenge"

class AchievementTier(Enum):
    BRONZE = "bronze"
    SILVER = "silver" 
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

@dataclass
class Goal:
    """Individual goal configuration"""
    id: str
    title: str
    description: str
    goal_type: GoalType
    target_value: float
    current_value: float = 0.0
    deadline: Optional[str] = None  # ISO date string
    reward_points: int = 10
    is_completed: bool = False
    created_date: str = ""
    completed_date: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = dt.date.today().isoformat()

@dataclass
class Achievement:
    """Achievement/badge configuration"""
    id: str
    title: str
    description: str
    icon: str
    tier: AchievementTier
    points: int
    unlock_condition: str  # Description of how to unlock
    is_unlocked: bool = False
    unlock_date: Optional[str] = None
    progress: float = 0.0  # 0.0 to 1.0
    
@dataclass
class UserProfile:
    """Gamification user profile"""
    total_points: int = 0
    level: int = 1
    current_streak: int = 0
    longest_streak: int = 0
    achievements_unlocked: int = 0
    goals_completed: int = 0
    last_activity_date: Optional[str] = None

class GamificationEngine:
    """Main gamification engine"""
    
    def __init__(self, db_path: str, user_name: str):
        self.db_path = db_path
        self.user_name = user_name
        self.goals: Dict[str, Goal] = {}
        self.achievements: Dict[str, Achievement] = {}
        self.user_profile = UserProfile()
        
        # Load gamification data
        self.load_data()
        self.setup_default_achievements()
        
    def setup_default_achievements(self):
        """Setup default achievements if not already loaded"""
        default_achievements = [
            # Hydration achievements
            Achievement(
                "hydro_novice", "Hydration Novice", "Drink 2L of water in one day",
                "💧", AchievementTier.BRONZE, 50, "Drink 2000ml in a single day"
            ),
            Achievement(
                "hydro_master", "Hydration Master", "Maintain hydration goals for 7 days",
                "🌊", AchievementTier.SILVER, 100, "Meet hydration goal 7 days in a row"
            ),
            Achievement(
                "hydro_legend", "Hydration Legend", "30 day hydration streak",
                "⛲", AchievementTier.GOLD, 250, "Meet hydration goal 30 days in a row"
            ),
            
            # Steps achievements
            Achievement(
                "walker", "Daily Walker", "Walk 10,000 steps in one day",
                "🚶", AchievementTier.BRONZE, 50, "Reach 10,000 steps in a single day"
            ),
            Achievement(
                "marathoner", "Marathon Walker", "Walk 50,000 steps in one week",
                "🏃", AchievementTier.SILVER, 150, "Accumulate 50,000 steps in 7 days"
            ),
            Achievement(
                "step_master", "Step Master", "Maintain 10k+ steps for 30 days",
                "👑", AchievementTier.GOLD, 300, "10,000+ steps for 30 consecutive days"
            ),
            
            # Sleep achievements
            Achievement(
                "well_rested", "Well Rested", "Get 8+ hours of sleep",
                "😴", AchievementTier.BRONZE, 40, "Sleep 8 or more hours in one night"
            ),
            Achievement(
                "sleep_champion", "Sleep Champion", "Consistent 8h sleep for a week",
                "🛌", AchievementTier.SILVER, 120, "8+ hours sleep for 7 consecutive nights"
            ),
            
            # Health Score achievements
            Achievement(
                "healthy_start", "Healthy Start", "Achieve 70+ health score",
                "❤️", AchievementTier.BRONZE, 60, "Reach a health score of 70 or higher"
            ),
            Achievement(
                "health_guru", "Health Guru", "Achieve 90+ health score",
                "💪", AchievementTier.GOLD, 200, "Reach a health score of 90 or higher"
            ),
            
            # Streak achievements
            Achievement(
                "consistent", "Consistency King", "7 day activity streak",
                "🔥", AchievementTier.SILVER, 100, "Log activity for 7 consecutive days"
            ),
            Achievement(
                "unstoppable", "Unstoppable", "30 day activity streak",
                "⚡", AchievementTier.PLATINUM, 500, "Log activity for 30 consecutive days"
            ),
        ]
        
        for achievement in default_achievements:
            if achievement.id not in self.achievements:
                self.achievements[achievement.id] = achievement
    
    def add_goal(self, goal: Goal) -> str:
        """Add a new goal"""
        self.goals[goal.id] = goal
        self.save_data()
        return goal.id
    
    def complete_goal(self, goal_id: str) -> Optional[Goal]:
        """Mark a goal as completed"""
        if goal_id in self.goals:
            goal = self.goals[goal_id]
            if not goal.is_completed:
                goal.is_completed = True
                goal.completed_date = dt.date.today().isoformat()
                self.user_profile.total_points += goal.reward_points
                self.user_profile.goals_completed += 1
                self.update_level()
                self.save_data()
                return goal
        return None
    
    def update_goal_progress(self, goal_id: str, current_value: float):
        """Update goal progress"""
        if goal_id in self.goals:
            goal = self.goals[goal_id]
            goal.current_value = current_value
            
            # Auto-complete if target reached
            if current_value >= goal.target_value and not goal.is_completed:
                self.complete_goal(goal_id)
            
            self.save_data()
    
    def check_achievements(self, activity_data: Dict) -> List[Achievement]:
        """Check for newly unlocked achievements"""
        newly_unlocked = []
        
        # Check hydration achievements
        daily_water = activity_data.get('daily_water_ml', 0)
        if daily_water >= 2000:
            achievement = self.unlock_achievement('hydro_novice')
            if achievement:
                newly_unlocked.append(achievement)
        
        # Check steps achievements
        daily_steps = activity_data.get('daily_steps', 0)
        if daily_steps >= 10000:
            achievement = self.unlock_achievement('walker')
            if achievement:
                newly_unlocked.append(achievement)
        
        # Check sleep achievements
        sleep_hours = activity_data.get('sleep_hours', 0)
        if sleep_hours >= 8:
            achievement = self.unlock_achievement('well_rested')
            if achievement:
                newly_unlocked.append(achievement)
        
        # Check health score achievements
        health_score = activity_data.get('health_score', 0)
        if health_score >= 70:
            achievement = self.unlock_achievement('healthy_start')
            if achievement:
                newly_unlocked.append(achievement)
        if health_score >= 90:
            achievement = self.unlock_achievement('health_guru')
            if achievement:
                newly_unlocked.append(achievement)
        
        # Update streak-based achievements
        self.update_streaks(activity_data)
        
        return newly_unlocked
    
    def unlock_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Unlock an achievement"""
        if achievement_id in self.achievements:
            achievement = self.achievements[achievement_id]
            if not achievement.is_unlocked:
                achievement.is_unlocked = True
                achievement.unlock_date = dt.date.today().isoformat()
                self.user_profile.total_points += achievement.points
                self.user_profile.achievements_unlocked += 1
                self.update_level()
                self.save_data()
                return achievement
        return None
    
    def update_streaks(self, activity_data: Dict):
        """Update activity streaks"""
        today = dt.date.today().isoformat()
        
        # Check if user was active today
        has_activity = (
            activity_data.get('daily_steps', 0) > 1000 or
            activity_data.get('daily_water_ml', 0) > 500 or
            activity_data.get('sleep_hours', 0) > 4
        )
        
        if has_activity:
            if self.user_profile.last_activity_date:
                last_date = dt.date.fromisoformat(self.user_profile.last_activity_date)
                if (dt.date.today() - last_date).days == 1:
                    # Consecutive day
                    self.user_profile.current_streak += 1
                elif (dt.date.today() - last_date).days > 1:
                    # Streak broken
                    self.user_profile.current_streak = 1
            else:
                # First activity
                self.user_profile.current_streak = 1
            
            self.user_profile.last_activity_date = today
            
            # Update longest streak
            if self.user_profile.current_streak > self.user_profile.longest_streak:
                self.user_profile.longest_streak = self.user_profile.current_streak
            
            # Check streak achievements
            if self.user_profile.current_streak >= 7:
                self.unlock_achievement('consistent')
            if self.user_profile.current_streak >= 30:
                self.unlock_achievement('unstoppable')
    
    def update_level(self):
        """Update user level based on points"""
        # Simple level formula: level = sqrt(points / 100) + 1
        import math
        new_level = int(math.sqrt(self.user_profile.total_points / 100)) + 1
        
        if new_level > self.user_profile.level:
            self.user_profile.level = new_level
            return True  # Level up occurred
        return False
    
    def get_level_progress(self) -> tuple:
        """Get current level progress (current_points, points_for_next_level)"""
        import math
        current_level = self.user_profile.level
        points_for_current = (current_level - 1) ** 2 * 100
        points_for_next = current_level ** 2 * 100
        
        return (
            self.user_profile.total_points - points_for_current,
            points_for_next - points_for_current
        )
    
    def suggest_goals(self, activity_data: Dict) -> List[Goal]:
        """Suggest new goals based on user activity"""
        suggestions = []
        
        # Analyze patterns and suggest improvements
        avg_steps = activity_data.get('avg_steps_7d', 5000)
        avg_water = activity_data.get('avg_water_7d', 1500)
        avg_sleep = activity_data.get('avg_sleep_7d', 7)
        
        if avg_steps < 8000:
            suggestions.append(Goal(
                id=f"steps_goal_{dt.date.today().isoformat()}",
                title="Step It Up",
                description=f"Increase daily steps to {avg_steps + 2000}",
                goal_type=GoalType.STEPS,
                target_value=avg_steps + 2000,
                deadline=(dt.date.today() + dt.timedelta(days=7)).isoformat(),
                reward_points=75
            ))
        
        if avg_water < 2000:
            suggestions.append(Goal(
                id=f"hydration_goal_{dt.date.today().isoformat()}",
                title="Hydration Challenge",
                description="Drink 2L of water daily for a week",
                goal_type=GoalType.HYDRATION,
                target_value=2000,
                deadline=(dt.date.today() + dt.timedelta(days=7)).isoformat(),
                reward_points=50
            ))
        
        if avg_sleep < 8:
            suggestions.append(Goal(
                id=f"sleep_goal_{dt.date.today().isoformat()}",
                title="Sleep Better",
                description="Get 8+ hours of sleep for 5 nights",
                goal_type=GoalType.SLEEP,
                target_value=5,  # 5 nights with 8+ hours
                deadline=(dt.date.today() + dt.timedelta(days=7)).isoformat(),
                reward_points=60
            ))
        
        return suggestions
    
    def _enum_serializer(self, obj):
        """Custom serializer for enum objects"""
        if isinstance(obj, (GoalType, AchievementTier)):
            return obj.value
        return str(obj)
    
    def save_data(self):
        """Save gamification data to file"""
        data = {
            'user_profile': asdict(self.user_profile),
            'goals': {k: asdict(v) for k, v in self.goals.items()},
            'achievements': {k: asdict(v) for k, v in self.achievements.items()}
        }
        
        filename = f"gamification_{self.user_name}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=self._enum_serializer)
        except Exception as e:
            print(f"Failed to save gamification data: {e}")
    
    def load_data(self):
        """Load gamification data from file"""
        filename = f"gamification_{self.user_name}.json"
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Load user profile
            if 'user_profile' in data:
                self.user_profile = UserProfile(**data['user_profile'])
            
            # Load goals
            if 'goals' in data:
                for goal_id, goal_data in data['goals'].items():
                    # Convert string enum back to enum
                    goal_type_str = goal_data['goal_type']
                    if '.' in goal_type_str:  # Handle format like 'GoalType.HYDRATION'
                        goal_type_str = goal_type_str.split('.')[-1]
                    goal_data['goal_type'] = GoalType(goal_type_str.lower())
                    self.goals[goal_id] = Goal(**goal_data)
            
            # Load achievements
            if 'achievements' in data:
                for ach_id, ach_data in data['achievements'].items():
                    # Convert string enum back to enum
                    tier_str = ach_data['tier']
                    if '.' in tier_str:  # Handle format like 'AchievementTier.BRONZE'
                        tier_str = tier_str.split('.')[-1]
                    ach_data['tier'] = AchievementTier(tier_str.lower())
                    self.achievements[ach_id] = Achievement(**ach_data)
                    
        except (FileNotFoundError, json.JSONDecodeError):
            # No saved data, start fresh
            pass

class GamificationWidget:
    """Widget for displaying gamification elements"""
    
    def __init__(self, parent, engine: GamificationEngine):
        self.parent = parent
        self.engine = engine
        self.setup_widget()
    
    def setup_widget(self):
        """Setup gamification widget UI"""
        # Main frame
        self.frame = ttk.LabelFrame(
            self.parent,
            text="🏆 Your Progress",
            padding=10
        )
        self.frame.pack(fill="x", pady=10)
        
        # User level and XP
        level_frame = ttk.Frame(self.frame)
        level_frame.pack(fill="x", pady=(0, 10))
        
        self.level_label = ttk.Label(
            level_frame,
            text=f"Level {self.engine.user_profile.level}",
            font=("TkDefaultFont", 14, "bold"),
            style='Level.TLabel'
        )
        self.level_label.pack(side="left")
        
        self.points_label = ttk.Label(
            level_frame,
            text=f"{self.engine.user_profile.total_points} XP",
            style='Points.TLabel'
        )
        self.points_label.pack(side="right")
        
        # Level progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame,
            variable=self.progress_var,
            maximum=100,
            length=300,
            style='Level.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        # Stats frame
        stats_frame = ttk.Frame(self.frame)
        stats_frame.pack(fill="x")
        
        # Streak
        streak_frame = ttk.Frame(stats_frame)
        streak_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(
            streak_frame,
            text="🔥 Current Streak",
            style='Stat.TLabel'
        ).pack()
        
        self.streak_label = ttk.Label(
            streak_frame,
            text=f"{self.engine.user_profile.current_streak} days",
            font=("TkDefaultFont", 12, "bold"),
            style='StatValue.TLabel'
        )
        self.streak_label.pack()
        
        # Achievements
        ach_frame = ttk.Frame(stats_frame)
        ach_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(
            ach_frame,
            text="🏅 Achievements",
            style='Stat.TLabel'
        ).pack()
        
        total_achievements = len(self.engine.achievements)
        unlocked = self.engine.user_profile.achievements_unlocked
        
        self.achievements_label = ttk.Label(
            ach_frame,
            text=f"{unlocked}/{total_achievements}",
            font=("TkDefaultFont", 12, "bold"),
            style='StatValue.TLabel'
        )
        self.achievements_label.pack()
        
        # Goals completed
        goals_frame = ttk.Frame(stats_frame)
        goals_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(
            goals_frame,
            text="🎯 Goals",
            style='Stat.TLabel'
        ).pack()
        
        self.goals_label = ttk.Label(
            goals_frame,
            text=f"{self.engine.user_profile.goals_completed}",
            font=("TkDefaultFont", 12, "bold"),
            style='StatValue.TLabel'
        )
        self.goals_label.pack()
        
        self.update_display()
    
    def update_display(self):
        """Update the display with current data"""
        # Update level and points
        self.level_label.config(text=f"Level {self.engine.user_profile.level}")
        self.points_label.config(text=f"{self.engine.user_profile.total_points} XP")
        
        # Update progress bar
        current_points, points_needed = self.engine.get_level_progress()
        if points_needed > 0:
            progress = (current_points / points_needed) * 100
        else:
            progress = 100
        self.progress_var.set(progress)
        
        # Update stats
        self.streak_label.config(text=f"{self.engine.user_profile.current_streak} days")
        
        total_achievements = len(self.engine.achievements)
        unlocked = self.engine.user_profile.achievements_unlocked
        self.achievements_label.config(text=f"{unlocked}/{total_achievements}")
        
        self.goals_label.config(text=f"{self.engine.user_profile.goals_completed}")
    
    def show_achievement_popup(self, achievement: Achievement):
        """Show achievement unlock popup"""
        popup = tk.Toplevel(self.parent)
        popup.title("Achievement Unlocked!")
        popup.geometry("350x200")
        popup.resizable(False, False)
        
        # Center the popup
        popup.transient(self.parent)
        popup.grab_set()
        
        # Achievement content
        ttk.Label(
            popup,
            text="🎉 Achievement Unlocked! 🎉",
            font=("TkDefaultFont", 14, "bold")
        ).pack(pady=20)
        
        ttk.Label(
            popup,
            text=achievement.icon,
            font=("TkDefaultFont", 24)
        ).pack()
        
        ttk.Label(
            popup,
            text=achievement.title,
            font=("TkDefaultFont", 12, "bold")
        ).pack(pady=5)
        
        ttk.Label(
            popup,
            text=achievement.description,
            style='PanelBody.TLabel'
        ).pack()
        
        ttk.Label(
            popup,
            text=f"+{achievement.points} XP",
            font=("TkDefaultFont", 11, "bold"),
            foreground="green"
        ).pack(pady=10)
        
        ttk.Button(
            popup,
            text="Awesome!",
            command=popup.destroy,
            style='Accent.TButton'
        ).pack(pady=10)
        
        # Auto-close after 5 seconds
        popup.after(5000, popup.destroy)


def setup_gamification_styles(style: ttk.Style):
    """Setup styles for gamification widgets"""
    style.configure(
        'Level.TLabel',
        background='#ffffff',
        foreground='#3b82f6',
        font=('TkDefaultFont', 14, 'bold')
    )
    
    style.configure(
        'Points.TLabel',
        background='#ffffff',
        foreground='#059669'
    )
    
    style.configure(
        'Level.Horizontal.TProgressbar',
        troughcolor='#e5e7eb',
        background='#3b82f6'
    )
    
    style.configure(
        'Stat.TLabel',
        background='#ffffff',
        foreground='#6b7280',
        font=('TkDefaultFont', 9)
    )
    
    style.configure(
        'StatValue.TLabel',
        background='#ffffff',
        foreground='#1f2937'
    )