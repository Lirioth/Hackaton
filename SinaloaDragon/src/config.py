"""
Sistema de Configuración para Chen Toka - Sinaloa Dragon

Este módulo maneja las configuraciones del juego, preferencias
del usuario y opciones persistentes.
"""

import json
import os
from typing import Dict, Any, Optional, List
from settings import Settings


class GameConfig:
    """Configuración principal del juego."""
    
    def __init__(self):
        """Inicializa la configuración con valores por defecto."""
        
        # Información de versión
        self.config_version = "1.0"
        self.game_version = Settings.GAME_VERSION
        
        # Configuraciones de video
        self.window_width = Settings.WINDOW_WIDTH
        self.window_height = Settings.WINDOW_HEIGHT
        self.fullscreen = False
        self.vsync = True
        self.fps_limit = Settings.FPS
        self.pixel_perfect = True
        
        # Configuraciones de audio
        self.master_volume = 1.0
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.voice_volume = 0.9
        self.audio_enabled = True
        self.music_enabled = True
        self.sfx_enabled = True
        
        # Configuraciones de gameplay
        self.difficulty = "normal"  # "easy", "normal", "hard", "expert"
        self.language = "es"  # "es", "en"
        self.subtitle_enabled = True
        self.auto_save = True
        self.save_frequency = 30  # segundos
        
        # Configuraciones de controles
        self.input_device = "keyboard"  # "keyboard", "gamepad", "mixed"
        self.gamepad_enabled = True
        self.keyboard_repeat_delay = 0.5
        self.gamepad_deadzone = 0.1
        self.input_buffer_time = 0.1
        
        # Configuraciones de accesibilidad
        self.colorblind_mode = "none"  # "none", "protanopia", "deuteranopia", "tritanopia"
        self.high_contrast = False
        self.screen_flash = True
        self.camera_shake = True
        self.motion_reduction = False
        
        # Configuraciones de debug
        self.debug_mode = False
        self.show_fps = False
        self.show_hitboxes = False
        self.show_collision_info = False
        self.enable_cheats = False
        self.log_level = "info"  # "debug", "info", "warning", "error"
        
        # Configuraciones de red (para futuras expansiones)
        self.online_features = False
        self.statistics_sharing = False
        
        # Mapeo de controles personalizado
        self.custom_key_bindings = {}
        self.custom_gamepad_bindings = {}
        
        # Configuraciones de interfaz
        self.ui_scale = 1.0
        self.show_tutorials = True
        self.show_tooltips = True
        self.menu_animations = True
        self.hud_opacity = 1.0
        
        print("Configuración de juego inicializada con valores por defecto")
    
    def get_video_config(self) -> Dict[str, Any]:
        """Obtiene configuraciones de video."""
        
        return {
            'window_width': self.window_width,
            'window_height': self.window_height,
            'fullscreen': self.fullscreen,
            'vsync': self.vsync,
            'fps_limit': self.fps_limit,
            'pixel_perfect': self.pixel_perfect
        }
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Obtiene configuraciones de audio."""
        
        return {
            'master_volume': self.master_volume,
            'music_volume': self.music_volume,
            'sfx_volume': self.sfx_volume,
            'voice_volume': self.voice_volume,
            'audio_enabled': self.audio_enabled,
            'music_enabled': self.music_enabled,
            'sfx_enabled': self.sfx_enabled
        }
    
    def get_control_config(self) -> Dict[str, Any]:
        """Obtiene configuraciones de controles."""
        
        return {
            'input_device': self.input_device,
            'gamepad_enabled': self.gamepad_enabled,
            'keyboard_repeat_delay': self.keyboard_repeat_delay,
            'gamepad_deadzone': self.gamepad_deadzone,
            'input_buffer_time': self.input_buffer_time,
            'custom_key_bindings': self.custom_key_bindings,
            'custom_gamepad_bindings': self.custom_gamepad_bindings
        }
    
    def get_accessibility_config(self) -> Dict[str, Any]:
        """Obtiene configuraciones de accesibilidad."""
        
        return {
            'colorblind_mode': self.colorblind_mode,
            'high_contrast': self.high_contrast,
            'screen_flash': self.screen_flash,
            'camera_shake': self.camera_shake,
            'motion_reduction': self.motion_reduction
        }
    
    def set_difficulty(self, difficulty: str):
        """
        Establece la dificultad del juego.
        
        Args:
            difficulty: Nivel de dificultad
        """
        
        valid_difficulties = ["easy", "normal", "hard", "expert"]
        if difficulty in valid_difficulties:
            self.difficulty = difficulty
            print(f"Dificultad establecida en: {difficulty}")
        else:
            print(f"Dificultad inválida: {difficulty}")
    
    def set_language(self, language: str):
        """
        Establece el idioma del juego.
        
        Args:
            language: Código de idioma
        """
        
        valid_languages = ["es", "en"]
        if language in valid_languages:
            self.language = language
            print(f"Idioma establecido en: {language}")
        else:
            print(f"Idioma no soportado: {language}")
    
    def toggle_fullscreen(self):
        """Alterna modo pantalla completa."""
        
        self.fullscreen = not self.fullscreen
        print(f"Pantalla completa: {'ON' if self.fullscreen else 'OFF'}")
    
    def set_volume(self, volume_type: str, value: float):
        """
        Establece un tipo de volumen específico.
        
        Args:
            volume_type: Tipo de volumen ('master', 'music', 'sfx', 'voice')
            value: Valor entre 0.0 y 1.0
        """
        
        value = max(0.0, min(1.0, value))  # Clampear entre 0 y 1
        
        if volume_type == "master":
            self.master_volume = value
        elif volume_type == "music":
            self.music_volume = value
        elif volume_type == "sfx":
            self.sfx_volume = value
        elif volume_type == "voice":
            self.voice_volume = value
        else:
            print(f"Tipo de volumen inválido: {volume_type}")
            return
        
        print(f"Volumen {volume_type} establecido en: {value:.2f}")
    
    def toggle_debug_mode(self):
        """Alterna modo debug."""
        
        self.debug_mode = not self.debug_mode
        print(f"Modo debug: {'ON' if self.debug_mode else 'OFF'}")
    
    def apply_accessibility_preset(self, preset: str):
        """
        Aplica un preset de accesibilidad.
        
        Args:
            preset: Nombre del preset
        """
        
        if preset == "high_visibility":
            self.high_contrast = True
            self.ui_scale = 1.2
            self.hud_opacity = 1.0
            print("Preset de alta visibilidad aplicado")
        
        elif preset == "motion_sensitive":
            self.camera_shake = False
            self.screen_flash = False
            self.motion_reduction = True
            self.menu_animations = False
            print("Preset para sensibilidad al movimiento aplicado")
        
        elif preset == "colorblind_friendly":
            self.high_contrast = True
            # El modo específico de daltonismo debe configurarse por separado
            print("Preset amigable para daltónicos aplicado")
        
        elif preset == "default":
            # Restaurar valores por defecto
            self.high_contrast = False
            self.screen_flash = True
            self.camera_shake = True
            self.motion_reduction = False
            self.ui_scale = 1.0
            self.hud_opacity = 1.0
            self.menu_animations = True
            self.colorblind_mode = "none"
            print("Configuración de accesibilidad restaurada a valores por defecto")
        
        else:
            print(f"Preset de accesibilidad desconocido: {preset}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la configuración a diccionario.
        
        Returns:
            Diccionario con toda la configuración
        """
        
        return {
            'config_version': self.config_version,
            'game_version': self.game_version,
            'video': self.get_video_config(),
            'audio': self.get_audio_config(),
            'gameplay': {
                'difficulty': self.difficulty,
                'language': self.language,
                'subtitle_enabled': self.subtitle_enabled,
                'auto_save': self.auto_save,
                'save_frequency': self.save_frequency
            },
            'controls': self.get_control_config(),
            'accessibility': self.get_accessibility_config(),
            'debug': {
                'debug_mode': self.debug_mode,
                'show_fps': self.show_fps,
                'show_hitboxes': self.show_hitboxes,
                'show_collision_info': self.show_collision_info,
                'enable_cheats': self.enable_cheats,
                'log_level': self.log_level
            },
            'interface': {
                'ui_scale': self.ui_scale,
                'show_tutorials': self.show_tutorials,
                'show_tooltips': self.show_tooltips,
                'menu_animations': self.menu_animations,
                'hud_opacity': self.hud_opacity
            },
            'network': {
                'online_features': self.online_features,
                'statistics_sharing': self.statistics_sharing
            }
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """
        Carga configuración desde diccionario.
        
        Args:
            data: Diccionario con configuración
        """
        
        # Información de versión
        self.config_version = data.get('config_version', '1.0')
        self.game_version = data.get('game_version', Settings.GAME_VERSION)
        
        # Video
        video_config = data.get('video', {})
        self.window_width = video_config.get('window_width', Settings.WINDOW_WIDTH)
        self.window_height = video_config.get('window_height', Settings.WINDOW_HEIGHT)
        self.fullscreen = video_config.get('fullscreen', False)
        self.vsync = video_config.get('vsync', True)
        self.fps_limit = video_config.get('fps_limit', Settings.FPS)
        self.pixel_perfect = video_config.get('pixel_perfect', True)
        
        # Audio
        audio_config = data.get('audio', {})
        self.master_volume = audio_config.get('master_volume', 1.0)
        self.music_volume = audio_config.get('music_volume', 0.7)
        self.sfx_volume = audio_config.get('sfx_volume', 0.8)
        self.voice_volume = audio_config.get('voice_volume', 0.9)
        self.audio_enabled = audio_config.get('audio_enabled', True)
        self.music_enabled = audio_config.get('music_enabled', True)
        self.sfx_enabled = audio_config.get('sfx_enabled', True)
        
        # Gameplay
        gameplay_config = data.get('gameplay', {})
        self.difficulty = gameplay_config.get('difficulty', 'normal')
        self.language = gameplay_config.get('language', 'es')
        self.subtitle_enabled = gameplay_config.get('subtitle_enabled', True)
        self.auto_save = gameplay_config.get('auto_save', True)
        self.save_frequency = gameplay_config.get('save_frequency', 30)
        
        # Controles
        controls_config = data.get('controls', {})
        self.input_device = controls_config.get('input_device', 'keyboard')
        self.gamepad_enabled = controls_config.get('gamepad_enabled', True)
        self.keyboard_repeat_delay = controls_config.get('keyboard_repeat_delay', 0.5)
        self.gamepad_deadzone = controls_config.get('gamepad_deadzone', 0.1)
        self.input_buffer_time = controls_config.get('input_buffer_time', 0.1)
        self.custom_key_bindings = controls_config.get('custom_key_bindings', {})
        self.custom_gamepad_bindings = controls_config.get('custom_gamepad_bindings', {})
        
        # Accesibilidad
        accessibility_config = data.get('accessibility', {})
        self.colorblind_mode = accessibility_config.get('colorblind_mode', 'none')
        self.high_contrast = accessibility_config.get('high_contrast', False)
        self.screen_flash = accessibility_config.get('screen_flash', True)
        self.camera_shake = accessibility_config.get('camera_shake', True)
        self.motion_reduction = accessibility_config.get('motion_reduction', False)
        
        # Debug
        debug_config = data.get('debug', {})
        self.debug_mode = debug_config.get('debug_mode', False)
        self.show_fps = debug_config.get('show_fps', False)
        self.show_hitboxes = debug_config.get('show_hitboxes', False)
        self.show_collision_info = debug_config.get('show_collision_info', False)
        self.enable_cheats = debug_config.get('enable_cheats', False)
        self.log_level = debug_config.get('log_level', 'info')
        
        # Interfaz
        interface_config = data.get('interface', {})
        self.ui_scale = interface_config.get('ui_scale', 1.0)
        self.show_tutorials = interface_config.get('show_tutorials', True)
        self.show_tooltips = interface_config.get('show_tooltips', True)
        self.menu_animations = interface_config.get('menu_animations', True)
        self.hud_opacity = interface_config.get('hud_opacity', 1.0)
        
        # Red
        network_config = data.get('network', {})
        self.online_features = network_config.get('online_features', False)
        self.statistics_sharing = network_config.get('statistics_sharing', False)
        
        print("Configuración cargada desde diccionario")


class ConfigManager:
    """
    Administrador principal de configuración del juego.
    """
    
    def __init__(self, config_directory: str = None):
        """
        Inicializa el administrador de configuración.
        
        Args:
            config_directory: Directorio donde guardar configuraciones
        """
        
        self.config_directory = config_directory or Settings.SAVE_DIRECTORY
        self.config_file = os.path.join(self.config_directory, "config.json")
        self.backup_config_file = os.path.join(self.config_directory, "config_backup.json")
        
        self.config = GameConfig()
        
        # Crear directorio si no existe
        self._ensure_config_directory()
        
        print(f"Administrador de configuración inicializado en: {self.config_directory}")
    
    def _ensure_config_directory(self):
        """Asegura que el directorio de configuración existe."""
        
        try:
            os.makedirs(self.config_directory, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorio de configuración: {e}")
    
    def save_config(self) -> bool:
        """
        Guarda la configuración actual.
        
        Returns:
            True si el guardado fue exitoso
        """
        
        try:
            # Crear backup si existe configuración previa
            if os.path.exists(self.config_file):
                self._create_backup()
            
            # Guardar configuración
            config_dict = self.config.to_dict()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            print(f"Configuración guardada en: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return False
    
    def load_config(self) -> bool:
        """
        Carga la configuración guardada.
        
        Returns:
            True si la carga fue exitosa
        """
        
        # Intentar cargar archivo principal
        if self._load_from_file(self.config_file):
            return True
        
        # Si falla, intentar backup
        print("Archivo de configuración corrupto, intentando backup...")
        if self._load_from_file(self.backup_config_file):
            print("Configuración cargada desde backup")
            self.save_config()  # Restaurar archivo principal
            return True
        
        print("No se pudo cargar configuración, usando valores por defecto")
        return False
    
    def _load_from_file(self, file_path: str) -> bool:
        """
        Carga configuración desde un archivo específico.
        
        Args:
            file_path: Ruta del archivo a cargar
            
        Returns:
            True si la carga fue exitosa
        """
        
        try:
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            self.config.from_dict(config_dict)
            print(f"Configuración cargada desde: {file_path}")
            return True
            
        except Exception as e:
            print(f"Error cargando configuración desde {file_path}: {e}")
            return False
    
    def _create_backup(self):
        """Crea backup de la configuración actual."""
        
        try:
            if os.path.exists(self.config_file):
                import shutil
                shutil.copy2(self.config_file, self.backup_config_file)
                print("Backup de configuración creado")
        except Exception as e:
            print(f"Error creando backup de configuración: {e}")
    
    def reset_config(self, category: str = "all") -> bool:
        """
        Resetea configuración a valores por defecto.
        
        Args:
            category: Categoría a resetear ("all", "video", "audio", etc.)
            
        Returns:
            True si el reset fue exitoso
        """
        
        try:
            if category == "all":
                self.config = GameConfig()
                print("Toda la configuración reseteada a valores por defecto")
            
            elif category == "video":
                # Resetear solo configuraciones de video
                default_config = GameConfig()
                video_config = default_config.get_video_config()
                
                self.config.window_width = video_config['window_width']
                self.config.window_height = video_config['window_height']
                self.config.fullscreen = video_config['fullscreen']
                self.config.vsync = video_config['vsync']
                self.config.fps_limit = video_config['fps_limit']
                self.config.pixel_perfect = video_config['pixel_perfect']
                
                print("Configuración de video reseteada")
            
            elif category == "audio":
                # Resetear solo configuraciones de audio
                default_config = GameConfig()
                audio_config = default_config.get_audio_config()
                
                self.config.master_volume = audio_config['master_volume']
                self.config.music_volume = audio_config['music_volume']
                self.config.sfx_volume = audio_config['sfx_volume']
                self.config.voice_volume = audio_config['voice_volume']
                self.config.audio_enabled = audio_config['audio_enabled']
                self.config.music_enabled = audio_config['music_enabled']
                self.config.sfx_enabled = audio_config['sfx_enabled']
                
                print("Configuración de audio reseteada")
            
            elif category == "controls":
                # Resetear configuraciones de controles
                default_config = GameConfig()
                control_config = default_config.get_control_config()
                
                self.config.input_device = control_config['input_device']
                self.config.gamepad_enabled = control_config['gamepad_enabled']
                self.config.keyboard_repeat_delay = control_config['keyboard_repeat_delay']
                self.config.gamepad_deadzone = control_config['gamepad_deadzone']
                self.config.input_buffer_time = control_config['input_buffer_time']
                self.config.custom_key_bindings = {}
                self.config.custom_gamepad_bindings = {}
                
                print("Configuración de controles reseteada")
            
            else:
                print(f"Categoría de reset desconocida: {category}")
                return False
            
            return self.save_config()
            
        except Exception as e:
            print(f"Error reseteando configuración: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """
        Exporta la configuración a un archivo.
        
        Args:
            export_path: Ruta donde exportar
            
        Returns:
            True si la exportación fue exitosa
        """
        
        try:
            config_dict = self.config.to_dict()
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            print(f"Configuración exportada a: {export_path}")
            return True
            
        except Exception as e:
            print(f"Error exportando configuración: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        Importa configuración desde un archivo.
        
        Args:
            import_path: Ruta del archivo a importar
            
        Returns:
            True si la importación fue exitosa
        """
        
        try:
            if not os.path.exists(import_path):
                print(f"Archivo de importación no encontrado: {import_path}")
                return False
            
            # Crear backup de la configuración actual
            if os.path.exists(self.config_file):
                self._create_backup()
            
            # Cargar configuración importada
            if self._load_from_file(import_path):
                self.save_config()
                print(f"Configuración importada desde: {import_path}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error importando configuración: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de la configuración actual.
        
        Returns:
            Diccionario con resumen de configuración
        """
        
        return {
            'video_mode': f"{self.config.window_width}x{self.config.window_height}",
            'fullscreen': self.config.fullscreen,
            'audio_enabled': self.config.audio_enabled,
            'difficulty': self.config.difficulty,
            'language': self.config.language,
            'debug_mode': self.config.debug_mode,
            'accessibility_features': {
                'high_contrast': self.config.high_contrast,
                'colorblind_mode': self.config.colorblind_mode,
                'motion_reduction': self.config.motion_reduction
            }
        }