"""
Configuración global del juego Chen Toka - Sinaloa Dragon

Este módulo contiene todas las constantes y configuraciones del juego,
incluyendo resoluciones, físicas, timings y valores de gameplay.
"""

import os
import sys


class Settings:
    """Configuración global del juego."""
    
    # === RESOLUCIÓN Y PANTALLA ===
    GAME_WIDTH = 320      # Resolución interna del juego (retro)
    GAME_HEIGHT = 180
    WINDOW_WIDTH = 1280   # Resolución de la ventana (escalado 4x)
    WINDOW_HEIGHT = 720
    TARGET_FPS = 60
    
    # === TAMAÑOS DE TILES Y MUNDO ===
    TILE_SIZE = 16
    TILES_PER_SCREEN_X = GAME_WIDTH // TILE_SIZE    # 20 tiles
    TILES_PER_SCREEN_Y = GAME_HEIGHT // TILE_SIZE   # 11.25 tiles
    
    # === FÍSICAS ===
    GRAVITY = 800.0              # Pixeles por segundo al cuadrado
    MAX_FALL_SPEED = 400.0       # Velocidad máxima de caída
    
    # Jugador
    PLAYER_SPEED = 120.0         # Velocidad de movimiento horizontal
    PLAYER_JUMP_FORCE = 300.0    # Fuerza inicial del salto
    PLAYER_DOUBLE_JUMP_FORCE = 280.0  # Fuerza del doble salto
    PLAYER_ROLL_SPEED = 200.0    # Velocidad durante el roll
    PLAYER_ROLL_DURATION = 0.3   # Duración del roll en segundos
    
    # === TIMINGS Y MECÁNICAS ===
    COYOTE_TIME = 0.12           # Tiempo de coyote en segundos (120ms)
    JUMP_BUFFER_TIME = 0.1       # Buffer de salto en segundos (100ms)
    HIT_STOP_FRAMES = 8          # Frames de pausa al golpear
    HURT_IFRAMES_DURATION = 0.6  # Duración de invencibilidad tras daño
    PARRY_WINDOW = 0.15          # Ventana de parry en segundos
    
    # === CÁMARA ===
    CAMERA_DEAD_ZONE_X = 80      # Zona muerta horizontal de la cámara
    CAMERA_DEAD_ZONE_Y = 40      # Zona muerta vertical de la cámara
    CAMERA_SMOOTHING = 0.1       # Suavizado de la cámara (0-1)
    
    # === COMBATE ===
    COMBO_WINDOW = 0.5           # Tiempo para continuar combo
    MAX_COMBO_COUNT = 3          # Máximo número en combo
    SUPER_METER_MAX = 3          # Segmentos máximos del super meter
    
    # === SALUD Y RECURSOS ===
    PLAYER_MAX_HP = 50           # HP máximo del jugador
    HEART_DISPLAY_VALUE = 10     # HP por corazón en la UI
    PICKUP_TACO_HEAL = 10        # Curación del taco
    PICKUP_HORCHATA_SUPER = 1    # Super pips de la horchata
    
    # === ENEMIGOS ===
    # Matón (enemigo lento y fuerte)
    MATON_HP = 30
    MATON_SPEED = 40.0
    MATON_ATTACK_DAMAGE = 15
    MATON_ATTACK_WINDUP = 1.0    # Tiempo de preparación de ataque
    
    # Chacal (lanzador de cuchillos)
    CHACAL_HP = 20
    CHACAL_SPEED = 60.0
    CHACAL_THROW_INTERVAL = 2.0  # Intervalo entre lanzamientos
    CHACAL_KNIFE_DAMAGE = 8
    
    # Luchador (agarres)
    LUCHADOR_HP = 35
    LUCHADOR_SPEED = 80.0
    LUCHADOR_GRAB_DAMAGE = 20
    LUCHADOR_LUNGE_DISTANCE = 64
    
    # Dron de Seguridad (volador)
    DRONE_HP = 15
    DRONE_SPEED = 50.0
    DRONE_PATROL_DISTANCE = 128
    DRONE_LASER_DAMAGE = 5
    
    # === HAZARDS ESPECÍFICOS POR NIVEL ===
    # CDMX - Metro
    METRO_INTERVAL = 12.0        # Segundos entre trenes
    METRO_WARNING_TIME = 2.0     # Tiempo de advertencia antes del tren
    METRO_SPEED = 400.0          # Velocidad del tren
    METRO_DAMAGE = 25            # Daño del tren
    
    # Guadalajara - Lluvia
    RAIN_FRICTION_MULTIPLIER = 0.6  # Reducción de fricción por lluvia
    RAIN_PARTICLE_COUNT = 50        # Partículas de lluvia en pantalla
    
    # Oaxaca - Papel Picado
    CONFETTI_INTERVAL = 8.0      # Segundos entre ráfagas de confetti
    CONFETTI_DURATION = 3.0      # Duración del efecto de oscurecimiento
    CONFETTI_OPACITY = 180       # Opacidad del overlay (0-255)
    
    # === BOSS - EL JAGUAR ===
    BOSS_HP_PHASE_1 = 100
    BOSS_HP_PHASE_2 = 80
    BOSS_HP_PHASE_3 = 60
    BOSS_POUNCE_SPEED = 250.0
    BOSS_SHOCKWAVE_RADIUS = 80
    BOSS_CHAIN_GRAB_QTE_TIME = 1.5
    
    # === ARCHIVOS Y PATHS ===
    @staticmethod
    def get_base_path():
        """Obtiene el path base del juego, compatible con PyInstaller."""
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @staticmethod
    def get_asset_path(relative_path):
        """Obtiene el path completo de un asset."""
        base_path = Settings.get_base_path()
        return os.path.join(base_path, 'assets', relative_path)
    
    @staticmethod
    def get_level_path(level_name):
        """Obtiene el path completo de un archivo de nivel."""
        base_path = Settings.get_base_path()
        return os.path.join(base_path, 'src', 'levels', f'data_{level_name}.json')
    
    @staticmethod
    def get_save_path():
        """Obtiene el directorio de guardado, con fallback local."""
        try:
            # Intentar usar APPDATA en Windows
            appdata = os.environ.get('APPDATA')
            if appdata:
                save_dir = os.path.join(appdata, 'ChenToka')
                os.makedirs(save_dir, exist_ok=True)
                return save_dir
        except:
            pass
        
        # Fallback a directorio local
        base_path = Settings.get_base_path()
        save_dir = os.path.join(base_path, 'save')
        os.makedirs(save_dir, exist_ok=True)
        return save_dir
    
    # === COLORES (RGB) ===
    # Paleta inspirada en SNES, colores mexicanos
    COLOR_BLACK = (0, 0, 0)
    COLOR_WHITE = (255, 255, 255)
    COLOR_RED = (220, 38, 47)           # Rojo México
    COLOR_GREEN = (0, 104, 63)          # Verde México
    COLOR_YELLOW = (255, 206, 84)       # Amarillo cálido
    COLOR_BLUE = (25, 130, 196)         # Azul cielo
    COLOR_ORANGE = (255, 159, 26)       # Naranja cálido
    COLOR_PURPLE = (142, 68, 173)       # Morado real
    COLOR_BROWN = (139, 69, 19)         # Café tierra
    COLOR_GRAY = (128, 128, 128)        # Gris neutral
    COLOR_DARK_GRAY = (64, 64, 64)      # Gris oscuro
    COLOR_LIGHT_GRAY = (192, 192, 192)  # Gris claro
    
    # Colores específicos de UI
    COLOR_HP_FULL = COLOR_RED
    COLOR_HP_EMPTY = COLOR_DARK_GRAY
    COLOR_SUPER_FULL = COLOR_YELLOW
    COLOR_SUPER_EMPTY = COLOR_GRAY
    COLOR_COMBO_TEXT = COLOR_WHITE
    
    # === DEBUG ===
    DEBUG_DRAW_HITBOXES = False     # Se puede activar desde opciones
    DEBUG_DRAW_CAMERA_BOUNDS = False
    DEBUG_SHOW_FPS = True
    DEBUG_INVINCIBLE_PLAYER = False
    
    # === INPUT SETTINGS ===
    # Se cargarán desde config.json, estos son los defaults
    DEFAULT_KEYBOARD_MAPPING = {
        'move_left': ['a', 'left'],
        'move_right': ['d', 'right'], 
        'move_up': ['w', 'up'],
        'move_down': ['s', 'down'],
        'jump': ['space'],
        'attack_light': ['j'],
        'attack_heavy': ['k'],
        'roll': ['l'],
        'parry': ['lshift', 'rshift'],
        'pause': ['escape'],
        'confirm': ['return', 'space'],
        'cancel': ['escape', 'x']
    }
    
    DEFAULT_GAMEPAD_MAPPING = {
        'move_left': [-1],           # Analog stick left
        'move_right': [1],           # Analog stick right
        'jump': [0],                 # A button (Xbox)
        'attack_light': [2],         # X button (Xbox)
        'attack_heavy': [3],         # Y button (Xbox)
        'roll': [1],                 # B button (Xbox)
        'parry': [5, 4],            # RB/LB (Xbox)
        'pause': [7],               # Start button (Xbox)
        'confirm': [0],             # A button
        'cancel': [1]               # B button
    }
    
    # === AUDIO SETTINGS ===
    DEFAULT_MASTER_VOLUME = 0.8
    DEFAULT_SFX_VOLUME = 0.7
    DEFAULT_MUSIC_VOLUME = 0.6
    
    # === ACCESSIBILITY ===
    DEFAULT_HIGH_CONTRAST = False
    DEFAULT_SCREEN_SHAKE_INTENSITY = 1.0
    DEFAULT_DAMAGE_NUMBERS = True