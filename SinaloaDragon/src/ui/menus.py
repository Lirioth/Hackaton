"""
Sistema de Menús para Chen Toka - Sinaloa Dragon

Este módulo contiene todos los menús del juego: principal, pausa, opciones,
remapeo de controles y pantallas de victoria/game over.
"""

import pygame
import math
from typing import List, Dict, Any, Optional, Callable
from settings import Settings


class MenuOption:
    """Opción individual de un menú."""
    
    def __init__(self, text: str, action: Callable = None, submenu = None):
        """
        Inicializa una opción de menú.
        
        Args:
            text: Texto a mostrar
            action: Función a ejecutar cuando se selecciona
            submenu: Submenú a abrir cuando se selecciona
        """
        
        self.text = text
        self.action = action
        self.submenu = submenu
        self.enabled = True
        self.visible = True


class Menu:
    """Clase base para todos los menús."""
    
    def __init__(self, title: str):
        """
        Inicializa un menú.
        
        Args:
            title: Título del menú
        """
        
        self.title = title
        self.options: List[MenuOption] = []
        self.selected_index = 0
        self.visible = True
        
        # Animación
        self.selection_pulse = 0.0
        self.fade_alpha = 255
        
        # Navegación
        self.can_navigate = True
        self.escape_action = None  # Acción al presionar escape
    
    def add_option(self, option: MenuOption):
        """
        Añade una opción al menú.
        
        Args:
            option: Opción a añadir
        """
        
        self.options.append(option)
    
    def update(self, dt: float, input_manager):
        """
        Actualiza el menú.
        
        Args:
            dt: Delta time en segundos
            input_manager: Administrador de entrada
        """
        
        if not self.visible or not self.can_navigate:
            return
        
        # Actualizar animación
        self.selection_pulse += dt * 5.0
        
        # Navegación vertical
        if input_manager.is_just_pressed('move_up'):
            self._move_selection(-1)
        elif input_manager.is_just_pressed('move_down'):
            self._move_selection(1)
        
        # Selección
        if input_manager.is_just_pressed('confirm'):
            self._select_current_option()
        
        # Escape
        if input_manager.is_just_pressed('cancel'):
            if self.escape_action:
                self.escape_action()
    
    def _move_selection(self, direction: int):
        """
        Mueve la selección en la dirección especificada.
        
        Args:
            direction: -1 para arriba, 1 para abajo
        """
        
        visible_options = [i for i, opt in enumerate(self.options) if opt.visible and opt.enabled]
        
        if not visible_options:
            return
        
        # Encontrar índice actual en la lista de opciones visibles
        try:
            current_pos = visible_options.index(self.selected_index)
        except ValueError:
            current_pos = 0
        
        # Mover posición
        new_pos = (current_pos + direction) % len(visible_options)
        self.selected_index = visible_options[new_pos]
    
    def _select_current_option(self):
        """Selecciona la opción actual."""
        
        if 0 <= self.selected_index < len(self.options):
            option = self.options[self.selected_index]
            
            if option.enabled and option.visible:
                if option.action:
                    try:
                        option.action()
                    except Exception as e:
                        print(f"Error ejecutando acción de menú: {e}")
                
                if option.submenu:
                    # Aquí se manejaría la transición a submenú
                    pass
    
    def render(self, surface: pygame.Surface, font: pygame.font.Font):
        """
        Renderiza el menú.
        
        Args:
            surface: Superficie donde renderizar
            font: Fuente a usar
        """
        
        if not self.visible:
            return
        
        # Fondo semi-transparente
        overlay = pygame.Surface((Settings.GAME_WIDTH, Settings.GAME_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        surface.blit(overlay, (0, 0))
        
        # Título
        title_surface = font.render(self.title, True, Settings.COLOR_WHITE)
        title_rect = title_surface.get_rect()
        title_rect.center = (Settings.GAME_WIDTH // 2, 40)
        surface.blit(title_surface, title_rect)
        
        # Opciones
        start_y = 80
        option_height = 25
        
        for i, option in enumerate(self.options):
            if not option.visible:
                continue
            
            y = start_y + i * option_height
            
            # Color de la opción
            if i == self.selected_index and option.enabled:
                # Opción seleccionada con pulso
                pulse_intensity = (math.sin(self.selection_pulse) + 1) * 0.5
                color = (
                    int(255 * pulse_intensity + 128 * (1 - pulse_intensity)),
                    int(255 * pulse_intensity + 255 * (1 - pulse_intensity)),
                    int(128 * pulse_intensity + 255 * (1 - pulse_intensity))
                )
            elif option.enabled:
                color = Settings.COLOR_WHITE
            else:
                color = Settings.COLOR_GRAY
            
            # Renderizar texto de la opción
            option_surface = font.render(option.text, True, color)
            option_rect = option_surface.get_rect()
            option_rect.center = (Settings.GAME_WIDTH // 2, y)
            
            # Indicador de selección
            if i == self.selected_index and option.enabled:
                arrow_x = option_rect.left - 20
                arrow_surface = font.render(">", True, color)
                surface.blit(arrow_surface, (arrow_x, y - arrow_surface.get_height() // 2))
            
            surface.blit(option_surface, option_rect)


class MainMenu(Menu):
    """Menú principal del juego."""
    
    def __init__(self, game_instance):
        super().__init__("CHEN TOKA - SINALOA DRAGON")
        
        self.game = game_instance
        
        # Opciones del menú principal
        self.add_option(MenuOption("Nuevo Juego", self._new_game))
        self.add_option(MenuOption("Continuar", self._continue_game))
        self.add_option(MenuOption("Opciones", self._show_options))
        self.add_option(MenuOption("Salir", self._quit_game))
    
    def _new_game(self):
        """Inicia un nuevo juego."""
        print("Iniciando nuevo juego...")
        if hasattr(self.game, '_start_new_game'):
            self.game._start_new_game()
    
    def _continue_game(self):
        """Continúa el juego guardado."""
        print("Cargando juego guardado...")
        # Aquí se implementaría la carga del juego
    
    def _show_options(self):
        """Muestra el menú de opciones."""
        print("Abriendo opciones...")
        from game import GameState
        if hasattr(self.game, 'state'):
            self.game.state = GameState.OPTIONS
    
    def _quit_game(self):
        """Sale del juego."""
        print("Saliendo del juego...")
        # Esto se manejará en el loop principal
        self.game.should_quit = True


class PauseMenu(Menu):
    """Menú de pausa."""
    
    def __init__(self, game_instance):
        super().__init__("PAUSA")
        
        self.game = game_instance
        
        # Opciones del menú de pausa
        self.add_option(MenuOption("Continuar", self._resume_game))
        self.add_option(MenuOption("Opciones", self._show_options))
        self.add_option(MenuOption("Reiniciar Nivel", self._restart_level))
        self.add_option(MenuOption("Menú Principal", self._return_to_main))
        self.add_option(MenuOption("Salir del Juego", self._quit_game))
        
        # Escape para continuar
        self.escape_action = self._resume_game
    
    def _resume_game(self):
        """Reanuda el juego."""
        from game import GameState
        if hasattr(self.game, 'previous_state'):
            self.game.state = self.game.previous_state or GameState.PLAYING
    
    def _show_options(self):
        """Muestra opciones."""
        from game import GameState
        if hasattr(self.game, 'state'):
            self.game.state = GameState.OPTIONS
    
    def _restart_level(self):
        """Reinicia el nivel actual."""
        if hasattr(self.game, '_restart_current_level'):
            self.game._restart_current_level()
    
    def _return_to_main(self):
        """Vuelve al menú principal."""
        from game import GameState
        if hasattr(self.game, 'state'):
            self.game.state = GameState.MAIN_MENU
    
    def _quit_game(self):
        """Sale del juego."""
        self.game.should_quit = True


class OptionsMenu(Menu):
    """Menú de opciones."""
    
    def __init__(self, game_instance):
        super().__init__("OPCIONES")
        
        self.game = game_instance
        self.settings_changed = False
        
        # Opciones disponibles
        self.add_option(MenuOption("Controles", self._show_controls))
        self.add_option(MenuOption("Audio", self._show_audio_options))
        self.add_option(MenuOption("Video", self._show_video_options))
        self.add_option(MenuOption("Debug", self._toggle_debug))
        self.add_option(MenuOption("Volver", self._go_back))
        
        self.escape_action = self._go_back
    
    def _show_controls(self):
        """Muestra opciones de controles."""
        print("Abriendo configuración de controles...")
        # Aquí se abriría el menú de remapeo
    
    def _show_audio_options(self):
        """Muestra opciones de audio."""
        print("Abriendo opciones de audio...")
        # Implementar menú de audio
    
    def _show_video_options(self):
        """Muestra opciones de video."""
        print("Abriendo opciones de video...")
        # Implementar opciones de video
    
    def _toggle_debug(self):
        """Alterna el modo debug."""
        Settings.DEBUG_DRAW_HITBOXES = not Settings.DEBUG_DRAW_HITBOXES
        status = "activado" if Settings.DEBUG_DRAW_HITBOXES else "desactivado"
        print(f"Modo debug {status}")
        
        # Actualizar texto de la opción
        for option in self.options:
            if "Debug" in option.text:
                option.text = f"Debug: {'ON' if Settings.DEBUG_DRAW_HITBOXES else 'OFF'}"
                break
    
    def _go_back(self):
        """Vuelve al menú anterior."""
        from game import GameState
        if hasattr(self.game, 'previous_state'):
            self.game.state = self.game.previous_state or GameState.MAIN_MENU


class ControlsMenu(Menu):
    """Menú de configuración de controles."""
    
    def __init__(self, game_instance):
        super().__init__("CONFIGURACIÓN DE CONTROLES")
        
        self.game = game_instance
        self.remapping_mode = False
        self.remapping_action = None
        
        # Acciones remapeables
        self.remappable_actions = [
            'move_left', 'move_right', 'move_up', 'move_down',
            'jump', 'attack_light', 'attack_heavy', 'roll', 'parry', 'pause'
        ]
        
        # Crear opciones para cada acción
        for action in self.remappable_actions:
            display_name = self._get_action_display_name(action)
            option = MenuOption(f"{display_name}: ?", lambda a=action: self._start_remap(a))
            self.add_option(option)
        
        self.add_option(MenuOption("Resetear a Default", self._reset_controls))
        self.add_option(MenuOption("Volver", self._go_back))
        
        self.escape_action = self._go_back
        
        # Actualizar textos iniciales
        self._update_control_texts()
    
    def _get_action_display_name(self, action: str) -> str:
        """Obtiene el nombre para mostrar de una acción."""
        
        display_names = {
            'move_left': 'Mover Izquierda',
            'move_right': 'Mover Derecha', 
            'move_up': 'Mover Arriba',
            'move_down': 'Mover Abajo',
            'jump': 'Saltar',
            'attack_light': 'Ataque Ligero',
            'attack_heavy': 'Ataque Pesado',
            'roll': 'Rodar',
            'parry': 'Parar',
            'pause': 'Pausa'
        }
        
        return display_names.get(action, action)
    
    def _update_control_texts(self):
        """Actualiza los textos de los controles."""
        
        if not hasattr(self.game, '_input_manager'):
            return
        
        input_manager = self.game._input_manager
        
        for i, action in enumerate(self.remappable_actions):
            if i < len(self.options):
                display_name = self._get_action_display_name(action)
                
                # Obtener teclas actuales
                current_keys = input_manager.get_current_keys_for_action(action)
                keys_text = ", ".join(current_keys[:2])  # Mostrar máximo 2 teclas
                
                self.options[i].text = f"{display_name}: {keys_text}"
    
    def _start_remap(self, action: str):
        """
        Inicia el proceso de remapeo para una acción.
        
        Args:
            action: Acción a remapear
        """
        
        if not self.remapping_mode:
            self.remapping_mode = True
            self.remapping_action = action
            self.can_navigate = False
            
            # Actualizar texto para mostrar que está esperando input
            for option in self.options:
                if action in option.text:
                    display_name = self._get_action_display_name(action)
                    option.text = f"{display_name}: Presiona una tecla..."
                    break
            
            print(f"Remapeando {action}. Presiona una tecla...")
    
    def update(self, dt: float, input_manager):
        """Actualiza el menú de controles con lógica de remapeo."""
        
        if self.remapping_mode:
            # Detectar nueva tecla presionada
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    new_key = pygame.key.name(event.key)
                    
                    # Cancelar con escape
                    if event.key == pygame.K_ESCAPE:
                        self._cancel_remap()
                        return
                    
                    # Aplicar remapeo
                    self._apply_remap(new_key)
                    return
        else:
            # Navegación normal del menú
            super().update(dt, input_manager)
    
    def _apply_remap(self, new_key: str):
        """
        Aplica el remapeo de una tecla.
        
        Args:
            new_key: Nueva tecla asignada
        """
        
        if hasattr(self.game, '_input_manager') and self.remapping_action:
            input_manager = self.game._input_manager
            input_manager.remap_action(self.remapping_action, new_key, 'keyboard')
            
            print(f"Acción {self.remapping_action} remapeada a {new_key}")
        
        self._end_remap()
    
    def _cancel_remap(self):
        """Cancela el remapeo actual."""
        
        print("Remapeo cancelado")
        self._end_remap()
    
    def _end_remap(self):
        """Termina el proceso de remapeo."""
        
        self.remapping_mode = False
        self.remapping_action = None
        self.can_navigate = True
        
        # Actualizar textos de controles
        self._update_control_texts()
    
    def _reset_controls(self):
        """Resetea todos los controles a los valores por defecto."""
        
        if hasattr(self.game, '_input_manager'):
            self.game._input_manager.reset_to_defaults()
            self._update_control_texts()
            print("Controles reseteados a valores por defecto")
    
    def _go_back(self):
        """Vuelve al menú anterior."""
        
        if self.remapping_mode:
            self._cancel_remap()
        else:
            from game import GameState
            self.game.state = GameState.OPTIONS


class GameOverMenu(Menu):
    """Menú de game over."""
    
    def __init__(self, game_instance):
        super().__init__("GAME OVER")
        
        self.game = game_instance
        
        self.add_option(MenuOption("Reintentar", self._retry))
        self.add_option(MenuOption("Menú Principal", self._main_menu))
        self.add_option(MenuOption("Salir", self._quit))
    
    def _retry(self):
        """Reintenta el nivel actual."""
        if hasattr(self.game, '_restart_current_level'):
            self.game._restart_current_level()
    
    def _main_menu(self):
        """Vuelve al menú principal."""
        from game import GameState
        self.game.state = GameState.MAIN_MENU
    
    def _quit(self):
        """Sale del juego."""
        self.game.should_quit = True


class VictoryMenu(Menu):
    """Menú de victoria."""
    
    def __init__(self, game_instance):
        super().__init__("¡VICTORIA!")
        
        self.game = game_instance
        
        self.add_option(MenuOption("Continuar", self._continue))
        self.add_option(MenuOption("Menú Principal", self._main_menu))
    
    def _continue(self):
        """Continúa al siguiente nivel."""
        from game import GameState
        self.game.state = GameState.MAIN_MENU  # Por ahora vuelve al menú
    
    def _main_menu(self):
        """Vuelve al menú principal."""
        from game import GameState
        self.game.state = GameState.MAIN_MENU


class MenuManager:
    """
    Administrador de menús del juego.
    """
    
    def __init__(self, game_instance):
        """
        Inicializa el administrador de menús.
        
        Args:
            game_instance: Instancia del juego principal
        """
        
        self.game = game_instance
        
        # Menús disponibles
        self.main_menu = MainMenu(game_instance)
        self.pause_menu = PauseMenu(game_instance)
        self.options_menu = OptionsMenu(game_instance)
        self.controls_menu = ControlsMenu(game_instance)
        self.game_over_menu = GameOverMenu(game_instance)
        self.victory_menu = VictoryMenu(game_instance)
        
        # Menú actual
        self.current_menu = self.main_menu
        
        print("Administrador de menús inicializado")
    
    def set_current_menu(self, menu_name: str):
        """
        Establece el menú actual.
        
        Args:
            menu_name: Nombre del menú ('main', 'pause', 'options', etc.)
        """
        
        menu_map = {
            'main': self.main_menu,
            'pause': self.pause_menu,
            'options': self.options_menu,
            'controls': self.controls_menu,
            'game_over': self.game_over_menu,
            'victory': self.victory_menu
        }
        
        if menu_name in menu_map:
            self.current_menu = menu_map[menu_name]
            print(f"Menú cambiado a: {menu_name}")
    
    def update(self, dt: float, input_manager):
        """
        Actualiza el menú actual.
        
        Args:
            dt: Delta time en segundos
            input_manager: Administrador de entrada
        """
        
        if self.current_menu:
            self.current_menu.update(dt, input_manager)
    
    def render(self, surface: pygame.Surface, font: pygame.font.Font):
        """
        Renderiza el menú actual.
        
        Args:
            surface: Superficie donde renderizar
            font: Fuente a usar
        """
        
        if self.current_menu:
            self.current_menu.render(surface, font)