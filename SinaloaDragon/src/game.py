"""
Controlador principal del juego Chen Toka - Sinaloa Dragon

Este módulo maneja el estado del juego, las escenas y el bucle principal.
Implementa una máquina de estados para las diferentes pantallas del juego.
"""

import pygame
import sys
from enum import Enum
from typing import List, Dict, Any, Optional

from settings import Settings


class GameState(Enum):
    """Estados posibles del juego."""
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    OPTIONS = "options"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    LEVEL_TRANSITION = "level_transition"


class Game:
    """
    Clase principal del juego que maneja el estado global y las transiciones entre escenas.
    """
    
    def __init__(self, surface: pygame.Surface):
        """
        Inicializa el juego.
        
        Args:
            surface: Superficie principal de renderizado del juego
        """
        self.surface = surface
        self.state = GameState.MAIN_MENU
        self.previous_state = None
        
        # Sistema de tiempo
        self.total_time = 0.0
        self.hit_stop_timer = 0.0
        
        # Carga diferida de módulos para evitar importaciones circulares
        self._assets = None
        self._input_manager = None
        self._save_system = None
        self._current_level = None
        self._player = None
        self._camera_x = 0.0
        self._camera_y = 0.0
        
        # HUD y UI
        self._hud = None
        self._current_menu = None
        
        # Datos del juego
        self.current_level_name = "cdmx"
        self.player_stats = {
            'hp': Settings.PLAYER_MAX_HP,
            'max_hp': Settings.PLAYER_MAX_HP,
            'coins': 0,
            'super_meter': 0,
            'combo_count': 0,
            'unlocked_skills': set()
        }
        
        # Estado del nivel actual
        self.level_data = None
        self.enemies = []
        self.pickups = []
        self.hazards = []
        
        # Efectos visuales
        self.screen_shake_intensity = 0.0
        self.screen_shake_duration = 0.0
        
        print("Juego inicializado - Cargando recursos...")
        self._initialize_game_systems()
    
    def _initialize_game_systems(self):
        """Inicializa los sistemas del juego de forma diferida."""
        try:
            # Importar y configurar sistemas
            from assets import AssetManager
            from input import InputManager
            from save_system import SaveSystem
            from config import ConfigManager
            
            self._assets = AssetManager()
            self._input_manager = InputManager()
            self._save_system = SaveSystem()
            self._config = ConfigManager()
            
            # Cargar configuración
            self._config.load_config()
            
            # Cargar progreso del juego
            self._save_system.load_game()
            
            # Aplicar configuración cargada al input manager
            self._input_manager.load_from_config(self._config.get_controls())
            
            print("Sistemas del juego inicializados correctamente")
            
        except ImportError as e:
            print(f"Error importando sistemas del juego: {e}")
            # Continúar con sistemas básicos para evitar crash
            self._create_fallback_systems()
        except Exception as e:
            print(f"Error inicializando sistemas: {e}")
            self._create_fallback_systems()
    
    def _create_fallback_systems(self):
        """Crea sistemas de fallback básicos si falla la carga normal."""
        print("Usando sistemas de fallback...")
        
        class FallbackAssets:
            def load_sprite(self, name): return None
            def load_sound(self, name): return None
            def load_music(self, name): return None
        
        class FallbackInput:
            def update(self, events): pass
            def is_pressed(self, action): return False
            def is_just_pressed(self, action): return False
            def get_movement_vector(self): return (0, 0)
        
        class FallbackSave:
            def save_game(self, data): pass
            def load_game(self): return {}
        
        class FallbackConfig:
            def load_config(self): pass
            def save_config(self): pass
            def get_controls(self): return Settings.DEFAULT_KEYBOARD_MAPPING
        
        self._assets = FallbackAssets()
        self._input_manager = FallbackInput()
        self._save_system = FallbackSave()
        self._config = FallbackConfig()
    
    def update(self, dt: float, events: List[pygame.event.Event]) -> bool:
        """
        Actualiza el estado del juego.
        
        Args:
            dt: Delta time en segundos
            events: Lista de eventos de pygame
            
        Returns:
            bool: False si el juego debe cerrarse, True para continuar
        """
        # Actualizar tiempo total
        self.total_time += dt
        
        # Manejar hit-stop
        if self.hit_stop_timer > 0:
            self.hit_stop_timer -= dt
            if self.hit_stop_timer <= 0:
                # Salir del hit-stop
                pass
            else:
                # Durante hit-stop, no actualizar gameplay
                return True
        
        # Actualizar input manager
        self._input_manager.update(events)
        
        # Verificar input de salida global
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4 and pygame.key.get_pressed()[pygame.K_LALT]:
                    return False  # Alt+F4 para salir
        
        # Actualizar según el estado actual
        if self.state == GameState.MAIN_MENU:
            return self._update_main_menu(dt, events)
        elif self.state == GameState.PLAYING:
            return self._update_playing(dt, events)
        elif self.state == GameState.PAUSED:
            return self._update_paused(dt, events)
        elif self.state == GameState.OPTIONS:
            return self._update_options(dt, events)
        elif self.state == GameState.GAME_OVER:
            return self._update_game_over(dt, events)
        elif self.state == GameState.VICTORY:
            return self._update_victory(dt, events)
        
        return True
    
    def _update_main_menu(self, dt: float, events: List[pygame.event.Event]) -> bool:
        """Actualiza el menú principal."""
        
        # Input básico del menú principal
        if self._input_manager.is_just_pressed('confirm'):
            # Iniciar juego
            self._start_new_game()
            return True
        
        if self._input_manager.is_just_pressed('cancel'):
            # Salir del juego
            return False
        
        # Teclas rápidas
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self._start_new_game()
                elif event.key == pygame.K_o:
                    self.state = GameState.OPTIONS
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        return True
    
    def _update_playing(self, dt: float, events: List[pygame.event.Event]) -> bool:
        """Actualiza el gameplay principal."""
        
        # Verificar pausa
        if self._input_manager.is_just_pressed('pause'):
            self.previous_state = self.state
            self.state = GameState.PAUSED
            return True
        
        # Actualizar sistemas de juego
        self._update_gameplay_systems(dt)
        
        # Actualizar efectos visuales
        self._update_visual_effects(dt)
        
        return True
    
    def _update_paused(self, dt: float, events: List[pygame.event.Event]) -> bool:
        """Actualiza el menú de pausa."""
        
        if self._input_manager.is_just_pressed('pause') or self._input_manager.is_just_pressed('cancel'):
            # Reanudar juego
            self.state = self.previous_state or GameState.PLAYING
            return True
        
        # Opciones desde pausa
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o:
                    self.state = GameState.OPTIONS
                elif event.key == pygame.K_m:
                    # Volver al menú principal
                    self.state = GameState.MAIN_MENU
                elif event.key == pygame.K_q:
                    # Salir del juego
                    return False
        
        return True
    
    def _update_options(self, dt: float, events: List[pygame.event.Event]) -> bool:
        """Actualiza el menú de opciones."""
        
        if self._input_manager.is_just_pressed('cancel'):
            # Volver al estado anterior
            self.state = self.previous_state or GameState.MAIN_MENU
            return True
        
        # Aquí iría la lógica del menú de opciones
        # Por ahora, implementación básica
        
        return True
    
    def _update_game_over(self, dt: float, events: List[pygame.event.Event]) -> bool:
        """Actualiza la pantalla de game over."""
        
        if self._input_manager.is_just_pressed('confirm'):
            # Reiniciar nivel
            self._restart_current_level()
            return True
        
        if self._input_manager.is_just_pressed('cancel'):
            # Volver al menú principal
            self.state = GameState.MAIN_MENU
            return True
        
        return True
    
    def _update_victory(self, dt: float, events: List[pygame.event.Event]) -> bool:
        """Actualiza la pantalla de victoria."""
        
        if self._input_manager.is_just_pressed('confirm'):
            # Continuar al siguiente nivel o volver al menú
            self.state = GameState.MAIN_MENU
            return True
        
        return True
    
    def _update_gameplay_systems(self, dt: float):
        """Actualiza los sistemas principales del gameplay."""
        
        # Placeholder para sistemas de gameplay
        # Aquí se actualizarían: jugador, enemigos, físicas, colisiones, etc.
        
        # Simulación básica de movimiento de cámara
        target_camera_x = 160  # Centro de la pantalla
        self._camera_x += (target_camera_x - self._camera_x) * Settings.CAMERA_SMOOTHING
        
        # Actualizar estadísticas básicas
        if self.total_time % 5.0 < dt:  # Cada 5 segundos
            if self.player_stats['coins'] < 999:
                self.player_stats['coins'] += 1
    
    def _update_visual_effects(self, dt: float):
        """Actualiza efectos visuales como screen shake."""
        
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= dt
            if self.screen_shake_duration <= 0:
                self.screen_shake_intensity = 0.0
    
    def _start_new_game(self):
        """Inicia un nuevo juego."""
        
        print("Iniciando nuevo juego...")
        
        # Resetear estadísticas del jugador
        self.player_stats = {
            'hp': Settings.PLAYER_MAX_HP,
            'max_hp': Settings.PLAYER_MAX_HP,
            'coins': 0,
            'super_meter': 0,
            'combo_count': 0,
            'unlocked_skills': set()
        }
        
        # Cargar primer nivel
        self.current_level_name = "cdmx"
        self._load_level(self.current_level_name)
        
        # Cambiar estado
        self.state = GameState.PLAYING
    
    def _restart_current_level(self):
        """Reinicia el nivel actual."""
        
        print(f"Reiniciando nivel: {self.current_level_name}")
        
        # Restaurar HP
        self.player_stats['hp'] = self.player_stats['max_hp']
        self.player_stats['combo_count'] = 0
        
        # Recargar nivel
        self._load_level(self.current_level_name)
        
        # Volver al gameplay
        self.state = GameState.PLAYING
    
    def _load_level(self, level_name: str):
        """
        Carga un nivel específico.
        
        Args:
            level_name: Nombre del nivel a cargar (cdmx, guadalajara, oaxaca)
        """
        
        try:
            # Intentar cargar datos del nivel
            from levels.loader import LevelLoader
            
            loader = LevelLoader()
            self.level_data = loader.load_level(level_name)
            
            # Resetear listas de entidades
            self.enemies = []
            self.pickups = []
            self.hazards = []
            
            # Inicializar entidades del nivel
            # (esto se expandirá cuando se implementen los sistemas completos)
            
            print(f"Nivel {level_name} cargado correctamente")
            
        except Exception as e:
            print(f"Error cargando nivel {level_name}: {e}")
            # Crear nivel básico de fallback
            self.level_data = {
                'name': level_name,
                'width': 40,  # tiles
                'height': 20,
                'tiles': [[0] * 40 for _ in range(20)],
                'entities': [],
                'background': f'{level_name}_parallax'
            }
    
    def trigger_hit_stop(self, duration_frames: int = None):
        """
        Activa el efecto de hit-stop.
        
        Args:
            duration_frames: Duración en frames (default: Settings.HIT_STOP_FRAMES)
        """
        if duration_frames is None:
            duration_frames = Settings.HIT_STOP_FRAMES
        
        self.hit_stop_timer = duration_frames / Settings.TARGET_FPS
    
    def trigger_screen_shake(self, intensity: float, duration: float):
        """
        Activa el efecto de screen shake.
        
        Args:
            intensity: Intensidad del shake (multiplicador)
            duration: Duración en segundos
        """
        self.screen_shake_intensity = max(self.screen_shake_intensity, intensity)
        self.screen_shake_duration = max(self.screen_shake_duration, duration)
    
    def render(self, surface: pygame.Surface):
        """
        Renderiza el juego en la superficie dada.
        
        Args:
            surface: Superficie donde renderizar
        """
        
        # Limpiar superficie
        surface.fill(Settings.COLOR_BLACK)
        
        # Aplicar screen shake si está activo
        shake_offset_x = 0
        shake_offset_y = 0
        
        if self.screen_shake_intensity > 0:
            import random
            shake_offset_x = random.randint(-int(self.screen_shake_intensity * 3), int(self.screen_shake_intensity * 3))
            shake_offset_y = random.randint(-int(self.screen_shake_intensity * 3), int(self.screen_shake_intensity * 3))
        
        # Renderizar según el estado actual
        if self.state == GameState.MAIN_MENU:
            self._render_main_menu(surface)
        elif self.state == GameState.PLAYING:
            self._render_gameplay(surface, shake_offset_x, shake_offset_y)
        elif self.state == GameState.PAUSED:
            self._render_gameplay(surface, shake_offset_x, shake_offset_y)
            self._render_pause_overlay(surface)
        elif self.state == GameState.OPTIONS:
            self._render_options(surface)
        elif self.state == GameState.GAME_OVER:
            self._render_game_over(surface)
        elif self.state == GameState.VICTORY:
            self._render_victory(surface)
        
        # Renderizar FPS si está habilitado
        if Settings.DEBUG_SHOW_FPS:
            self._render_fps(surface)
    
    def _render_main_menu(self, surface: pygame.Surface):
        """Renderiza el menú principal."""
        
        # Fondo
        surface.fill((20, 30, 60))  # Azul oscuro
        
        # Título del juego
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 18)
        
        title_text = font_large.render("CHEN TOKA", True, Settings.COLOR_YELLOW)
        subtitle_text = font_medium.render("Sinaloa Dragon", True, Settings.COLOR_WHITE)
        
        # Centrar título
        title_rect = title_text.get_rect(center=(Settings.GAME_WIDTH // 2, 60))
        subtitle_rect = subtitle_text.get_rect(center=(Settings.GAME_WIDTH // 2, 85))
        
        surface.blit(title_text, title_rect)
        surface.blit(subtitle_text, subtitle_rect)
        
        # Menú de opciones
        menu_y = 120
        start_text = font_medium.render("ENTER - Iniciar Juego", True, Settings.COLOR_WHITE)
        options_text = font_small.render("O - Opciones", True, Settings.COLOR_GRAY)
        exit_text = font_small.render("ESC - Salir", True, Settings.COLOR_GRAY)
        
        surface.blit(start_text, (Settings.GAME_WIDTH // 2 - start_text.get_width() // 2, menu_y))
        surface.blit(options_text, (Settings.GAME_WIDTH // 2 - options_text.get_width() // 2, menu_y + 25))
        surface.blit(exit_text, (Settings.GAME_WIDTH // 2 - exit_text.get_width() // 2, menu_y + 45))
    
    def _render_gameplay(self, surface: pygame.Surface, shake_x: int, shake_y: int):
        """Renderiza el gameplay principal."""
        
        # Fondo de nivel (placeholder)
        if self.current_level_name == "cdmx":
            surface.fill((40, 60, 80))  # Azul grisáceo para CDMX
        elif self.current_level_name == "guadalajara":
            surface.fill((50, 70, 50))  # Verde grisáceo para Guadalajara
        elif self.current_level_name == "oaxaca":
            surface.fill((80, 60, 40))  # Naranja grisáceo para Oaxaca
        else:
            surface.fill((60, 60, 60))  # Gris neutral
        
        # Dibujar "suelo" básico
        ground_y = Settings.GAME_HEIGHT - 32
        pygame.draw.rect(surface, Settings.COLOR_BROWN, 
                        (shake_x, ground_y + shake_y, Settings.GAME_WIDTH, 32))
        
        # Dibujar jugador placeholder (rectángulo)
        player_x = Settings.GAME_WIDTH // 2 - 8 + shake_x
        player_y = ground_y - 24 + shake_y
        pygame.draw.rect(surface, Settings.COLOR_GREEN, (player_x, player_y, 16, 24))
        
        # Dibujar algunos enemigos placeholder
        for i in range(3):
            enemy_x = 50 + i * 80 + int(self.total_time * 20) % 200 + shake_x
            enemy_y = ground_y - 16 + shake_y
            pygame.draw.rect(surface, Settings.COLOR_RED, (enemy_x, enemy_y, 16, 16))
        
        # Renderizar HUD
        self._render_hud(surface)
    
    def _render_pause_overlay(self, surface: pygame.Surface):
        """Renderiza el overlay de pausa."""
        
        # Overlay semi-transparente
        overlay = pygame.Surface((Settings.GAME_WIDTH, Settings.GAME_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        surface.blit(overlay, (0, 0))
        
        # Texto de pausa
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 24)
        
        pause_text = font_large.render("PAUSA", True, Settings.COLOR_WHITE)
        resume_text = font_medium.render("ESC - Continuar", True, Settings.COLOR_WHITE)
        menu_text = font_medium.render("M - Menú Principal", True, Settings.COLOR_WHITE)
        quit_text = font_medium.render("Q - Salir", True, Settings.COLOR_WHITE)
        
        y = Settings.GAME_HEIGHT // 2 - 40
        surface.blit(pause_text, (Settings.GAME_WIDTH // 2 - pause_text.get_width() // 2, y))
        surface.blit(resume_text, (Settings.GAME_WIDTH // 2 - resume_text.get_width() // 2, y + 30))
        surface.blit(menu_text, (Settings.GAME_WIDTH // 2 - menu_text.get_width() // 2, y + 50))
        surface.blit(quit_text, (Settings.GAME_WIDTH // 2 - quit_text.get_width() // 2, y + 70))
    
    def _render_options(self, surface: pygame.Surface):
        """Renderiza el menú de opciones."""
        
        surface.fill((30, 30, 50))
        
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 24)
        
        title_text = font_large.render("OPCIONES", True, Settings.COLOR_WHITE)
        back_text = font_medium.render("ESC - Volver", True, Settings.COLOR_WHITE)
        
        surface.blit(title_text, (Settings.GAME_WIDTH // 2 - title_text.get_width() // 2, 40))
        surface.blit(back_text, (Settings.GAME_WIDTH // 2 - back_text.get_width() // 2, Settings.GAME_HEIGHT - 40))
        
        # Placeholder para opciones
        y = 80
        options = [
            "Controles: Remapear (WIP)",
            "Audio: Master 80%",
            "Pantalla: Windowed",
            "Debug: Desactivado"
        ]
        
        for option in options:
            option_text = font_medium.render(option, True, Settings.COLOR_GRAY)
            surface.blit(option_text, (20, y))
            y += 25
    
    def _render_game_over(self, surface: pygame.Surface):
        """Renderiza la pantalla de game over."""
        
        surface.fill((40, 20, 20))  # Rojo oscuro
        
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 24)
        
        game_over_text = font_large.render("GAME OVER", True, Settings.COLOR_RED)
        retry_text = font_medium.render("ENTER - Reintentar", True, Settings.COLOR_WHITE)
        menu_text = font_medium.render("ESC - Menú Principal", True, Settings.COLOR_WHITE)
        
        y = Settings.GAME_HEIGHT // 2 - 30
        surface.blit(game_over_text, (Settings.GAME_WIDTH // 2 - game_over_text.get_width() // 2, y))
        surface.blit(retry_text, (Settings.GAME_WIDTH // 2 - retry_text.get_width() // 2, y + 40))
        surface.blit(menu_text, (Settings.GAME_WIDTH // 2 - menu_text.get_width() // 2, y + 60))
    
    def _render_victory(self, surface: pygame.Surface):
        """Renderiza la pantalla de victoria."""
        
        surface.fill((20, 40, 20))  # Verde oscuro
        
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 24)
        
        victory_text = font_large.render("¡VICTORIA!", True, Settings.COLOR_GREEN)
        continue_text = font_medium.render("ENTER - Continuar", True, Settings.COLOR_WHITE)
        
        y = Settings.GAME_HEIGHT // 2 - 20
        surface.blit(victory_text, (Settings.GAME_WIDTH // 2 - victory_text.get_width() // 2, y))
        surface.blit(continue_text, (Settings.GAME_WIDTH // 2 - continue_text.get_width() // 2, y + 40))
    
    def _render_hud(self, surface: pygame.Surface):
        """Renderiza el HUD del juego."""
        
        # Corazones de vida
        hearts_to_draw = (self.player_stats['hp'] + Settings.HEART_DISPLAY_VALUE - 1) // Settings.HEART_DISPLAY_VALUE
        max_hearts = self.player_stats['max_hp'] // Settings.HEART_DISPLAY_VALUE
        
        for i in range(max_hearts):
            x = 10 + i * 16
            y = 10
            color = Settings.COLOR_HP_FULL if i < hearts_to_draw else Settings.COLOR_HP_EMPTY
            
            # Dibujar corazón como rectángulo pequeño
            pygame.draw.rect(surface, color, (x, y, 12, 12))
        
        # Contador de monedas
        font = pygame.font.Font(None, 24)
        coins_text = font.render(f"Monedas: {self.player_stats['coins']}", True, Settings.COLOR_YELLOW)
        surface.blit(coins_text, (10, 30))
        
        # Super meter
        super_x = Settings.GAME_WIDTH - 80
        super_y = 10
        
        for i in range(Settings.SUPER_METER_MAX):
            x = super_x + i * 20
            color = Settings.COLOR_SUPER_FULL if i < self.player_stats['super_meter'] else Settings.COLOR_SUPER_EMPTY
            pygame.draw.rect(surface, color, (x, super_y, 16, 8))
        
        # Combo counter
        if self.player_stats['combo_count'] > 0:
            combo_text = font.render(f"Combo: {self.player_stats['combo_count']}", True, Settings.COLOR_COMBO_TEXT)
            surface.blit(combo_text, (Settings.GAME_WIDTH - combo_text.get_width() - 10, 30))
    
    def _render_fps(self, surface: pygame.Surface):
        """Renderiza el contador de FPS."""
        
        # Calcular FPS aproximado
        if hasattr(self, '_last_fps_time'):
            dt = self.total_time - self._last_fps_time
            if dt > 0:
                fps = 1.0 / dt
            else:
                fps = 60
        else:
            fps = 60
        
        self._last_fps_time = self.total_time
        
        font = pygame.font.Font(None, 18)
        fps_text = font.render(f"FPS: {int(fps)}", True, Settings.COLOR_WHITE)
        surface.blit(fps_text, (Settings.GAME_WIDTH - fps_text.get_width() - 5, Settings.GAME_HEIGHT - 20))
    
    def shutdown(self):
        """Realiza limpieza antes del cierre del juego."""
        
        print("Guardando configuración y progreso...")
        
        try:
            # Guardar configuración
            if hasattr(self, '_config') and self._config:
                self._config.save_config()
            
            # Guardar progreso del juego
            if hasattr(self, '_save_system') and self._save_system:
                save_data = {
                    'player_stats': self.player_stats,
                    'current_level': self.current_level_name,
                    'total_time_played': self.total_time
                }
                self._save_system.save_game(save_data)
            
            print("Guardado completado")
            
        except Exception as e:
            print(f"Error durante el guardado: {e}")
        
        print("Chen Toka cerrado correctamente")