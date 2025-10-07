"""
Sistema de Input para Chen Toka - Sinaloa Dragon

Este módulo maneja todas las entradas del usuario, incluyendo teclado y gamepad,
con soporte para remapeo de controles y configuración personalizable.
"""

import pygame
from typing import Dict, List, Tuple, Any, Optional
from settings import Settings


class InputManager:
    """
    Administrador central de todas las entradas del usuario.
    """
    
    def __init__(self):
        """Inicializa el administrador de input."""
        
        # Mapeo de acciones a teclas/botones
        self.keyboard_mapping: Dict[str, List[int]] = {}
        self.gamepad_mapping: Dict[str, List[int]] = {}
        
        # Estado actual de las entradas
        self.current_keys: Dict[int, bool] = {}
        self.previous_keys: Dict[int, bool] = {}
        self.current_gamepad: Dict[int, bool] = {}
        self.previous_gamepad: Dict[int, bool] = {}
        
        # Gamepad conectado
        self.joystick: Optional[pygame.joystick.Joystick] = None
        self.gamepad_connected = False
        
        # Buffer de entrada para timing perfecto
        self.input_buffer: Dict[str, float] = {}
        self.buffer_duration = 0.1  # 100ms de buffer
        
        # Estado del mouse (opcional)
        self.mouse_pos = (0, 0)
        self.mouse_buttons = (False, False, False)
        
        # Cargar mapeo por defecto
        self._load_default_mapping()
        
        # Detectar gamepads
        self._detect_gamepad()
    
    def _load_default_mapping(self):
        """Carga el mapeo de controles por defecto."""
        
        # Convertir configuración de strings a key codes
        for action, key_names in Settings.DEFAULT_KEYBOARD_MAPPING.items():
            self.keyboard_mapping[action] = []
            for key_name in key_names:
                key_code = self._get_key_code(key_name)
                if key_code is not None:
                    self.keyboard_mapping[action].append(key_code)
        
        # Cargar mapeo de gamepad por defecto
        self.gamepad_mapping = Settings.DEFAULT_GAMEPAD_MAPPING.copy()
        
        print("Mapeo de controles por defecto cargado")
    
    def _get_key_code(self, key_name: str) -> Optional[int]:
        """
        Convierte un nombre de tecla a su código pygame.
        
        Args:
            key_name: Nombre de la tecla (ej: 'a', 'space', 'left')
            
        Returns:
            Código de la tecla o None si no se encuentra
        """
        
        # Mapeo de nombres comunes a códigos pygame
        key_map = {
            'a': pygame.K_a, 'b': pygame.K_b, 'c': pygame.K_c, 'd': pygame.K_d,
            'e': pygame.K_e, 'f': pygame.K_f, 'g': pygame.K_g, 'h': pygame.K_h,
            'i': pygame.K_i, 'j': pygame.K_j, 'k': pygame.K_k, 'l': pygame.K_l,
            'm': pygame.K_m, 'n': pygame.K_n, 'o': pygame.K_o, 'p': pygame.K_p,
            'q': pygame.K_q, 'r': pygame.K_r, 's': pygame.K_s, 't': pygame.K_t,
            'u': pygame.K_u, 'v': pygame.K_v, 'w': pygame.K_w, 'x': pygame.K_x,
            'y': pygame.K_y, 'z': pygame.K_z,
            
            '0': pygame.K_0, '1': pygame.K_1, '2': pygame.K_2, '3': pygame.K_3,
            '4': pygame.K_4, '5': pygame.K_5, '6': pygame.K_6, '7': pygame.K_7,
            '8': pygame.K_8, '9': pygame.K_9,
            
            'space': pygame.K_SPACE, 'return': pygame.K_RETURN, 'enter': pygame.K_RETURN,
            'escape': pygame.K_ESCAPE, 'esc': pygame.K_ESCAPE,
            'tab': pygame.K_TAB, 'backspace': pygame.K_BACKSPACE,
            'delete': pygame.K_DELETE, 'home': pygame.K_HOME, 'end': pygame.K_END,
            'pageup': pygame.K_PAGEUP, 'pagedown': pygame.K_PAGEDOWN,
            
            'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
            'up': pygame.K_UP, 'down': pygame.K_DOWN,
            
            'lshift': pygame.K_LSHIFT, 'rshift': pygame.K_RSHIFT,
            'lctrl': pygame.K_LCTRL, 'rctrl': pygame.K_RCTRL,
            'lalt': pygame.K_LALT, 'ralt': pygame.K_RALT,
            
            'f1': pygame.K_F1, 'f2': pygame.K_F2, 'f3': pygame.K_F3, 'f4': pygame.K_F4,
            'f5': pygame.K_F5, 'f6': pygame.K_F6, 'f7': pygame.K_F7, 'f8': pygame.K_F8,
            'f9': pygame.K_F9, 'f10': pygame.K_F10, 'f11': pygame.K_F11, 'f12': pygame.K_F12
        }
        
        return key_map.get(key_name.lower())
    
    def _detect_gamepad(self):
        """Detecta y configura el primer gamepad disponible."""
        
        try:
            pygame.joystick.init()
            
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.gamepad_connected = True
                print(f"Gamepad detectado: {self.joystick.get_name()}")
            else:
                print("No se detectaron gamepads")
                self.gamepad_connected = False
                
        except Exception as e:
            print(f"Error detectando gamepad: {e}")
            self.gamepad_connected = False
    
    def update(self, events: List[pygame.event.Event]):
        """
        Actualiza el estado de todas las entradas.
        
        Args:
            events: Lista de eventos de pygame del frame actual
        """
        
        # Guardar estado anterior
        self.previous_keys = self.current_keys.copy()
        self.previous_gamepad = self.current_gamepad.copy()
        
        # Actualizar estado del teclado
        keys = pygame.key.get_pressed()
        self.current_keys = {i: keys[i] for i in range(len(keys))}
        
        # Actualizar estado del gamepad
        if self.gamepad_connected and self.joystick:
            try:
                # Actualizar botones del gamepad
                for i in range(self.joystick.get_numbuttons()):
                    self.current_gamepad[i] = self.joystick.get_button(i)
                
                # Manejar sticks analógicos como botones direccionales
                axis_x = self.joystick.get_axis(0)  # Stick izquierdo X
                axis_y = self.joystick.get_axis(1)  # Stick izquierdo Y
                
                # Convertir analog a digital con zona muerta
                deadzone = 0.3
                self.current_gamepad[-1] = axis_x < -deadzone  # Izquierda
                self.current_gamepad[1] = axis_x > deadzone     # Derecha
                self.current_gamepad[-2] = axis_y < -deadzone  # Arriba
                self.current_gamepad[2] = axis_y > deadzone     # Abajo
                
            except Exception as e:
                print(f"Error leyendo gamepad: {e}")
                self.gamepad_connected = False
        
        # Actualizar estado del mouse
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_buttons = pygame.mouse.get_pressed()
        
        # Procesar eventos especiales
        for event in events:
            if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                # Reconectar gamepad si fue desconectado
                if not self.gamepad_connected:
                    self._detect_gamepad()
        
        # Actualizar buffer de entrada
        self._update_input_buffer()
    
    def _update_input_buffer(self):
        """Actualiza el buffer de entrada para acciones que se presionaron recientemente."""
        
        import time
        current_time = time.time()
        
        # Limpiar entradas expiradas del buffer
        expired_actions = []
        for action, timestamp in self.input_buffer.items():
            if current_time - timestamp > self.buffer_duration:
                expired_actions.append(action)
        
        for action in expired_actions:
            del self.input_buffer[action]
        
        # Agregar nuevas entradas al buffer
        for action in self.keyboard_mapping.keys():
            if self.is_just_pressed(action):
                self.input_buffer[action] = current_time
    
    def is_pressed(self, action: str) -> bool:
        """
        Verifica si una acción está siendo presionada actualmente.
        
        Args:
            action: Nombre de la acción (ej: 'jump', 'attack_light')
            
        Returns:
            True si la acción está siendo presionada
        """
        
        # Verificar teclado
        for key_code in self.keyboard_mapping.get(action, []):
            if self.current_keys.get(key_code, False):
                return True
        
        # Verificar gamepad
        if self.gamepad_connected:
            for button_code in self.gamepad_mapping.get(action, []):
                if self.current_gamepad.get(button_code, False):
                    return True
        
        return False
    
    def is_just_pressed(self, action: str) -> bool:
        """
        Verifica si una acción fue presionada en este frame.
        
        Args:
            action: Nombre de la acción
            
        Returns:
            True si la acción fue presionada este frame
        """
        
        # Verificar teclado
        for key_code in self.keyboard_mapping.get(action, []):
            current = self.current_keys.get(key_code, False)
            previous = self.previous_keys.get(key_code, False)
            if current and not previous:
                return True
        
        # Verificar gamepad
        if self.gamepad_connected:
            for button_code in self.gamepad_mapping.get(action, []):
                current = self.current_gamepad.get(button_code, False)
                previous = self.previous_gamepad.get(button_code, False)
                if current and not previous:
                    return True
        
        return False
    
    def is_just_released(self, action: str) -> bool:
        """
        Verifica si una acción fue liberada en este frame.
        
        Args:
            action: Nombre de la acción
            
        Returns:
            True si la acción fue liberada este frame
        """
        
        # Verificar teclado
        for key_code in self.keyboard_mapping.get(action, []):
            current = self.current_keys.get(key_code, False)
            previous = self.previous_keys.get(key_code, False)
            if not current and previous:
                return True
        
        # Verificar gamepad
        if self.gamepad_connected:
            for button_code in self.gamepad_mapping.get(action, []):
                current = self.current_gamepad.get(button_code, False)
                previous = self.previous_gamepad.get(button_code, False)
                if not current and previous:
                    return True
        
        return False
    
    def was_pressed_recently(self, action: str) -> bool:
        """
        Verifica si una acción fue presionada recientemente (dentro del buffer).
        
        Args:
            action: Nombre de la acción
            
        Returns:
            True si la acción está en el buffer de entrada
        """
        
        return action in self.input_buffer
    
    def get_movement_vector(self) -> Tuple[float, float]:
        """
        Obtiene el vector de movimiento basado en las entradas direccionales.
        
        Returns:
            Tupla (x, y) con valores entre -1 y 1
        """
        
        x = 0.0
        y = 0.0
        
        if self.is_pressed('move_left'):
            x -= 1.0
        if self.is_pressed('move_right'):
            x += 1.0
        if self.is_pressed('move_up'):
            y -= 1.0
        if self.is_pressed('move_down'):
            y += 1.0
        
        # Si hay gamepad conectado, usar también input analógico
        if self.gamepad_connected and self.joystick:
            try:
                axis_x = self.joystick.get_axis(0)
                axis_y = self.joystick.get_axis(1)
                
                # Aplicar zona muerta
                deadzone = 0.2
                if abs(axis_x) > deadzone:
                    x = axis_x
                if abs(axis_y) > deadzone:
                    y = axis_y
                    
            except Exception:
                pass
        
        # Normalizar si es necesario (para movimiento diagonal)
        import math
        length = math.sqrt(x * x + y * y)
        if length > 1.0:
            x /= length
            y /= length
        
        return (x, y)
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Obtiene la posición actual del mouse.
        
        Returns:
            Tupla (x, y) con la posición del mouse
        """
        
        return self.mouse_pos
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        """
        Verifica si un botón del mouse está presionado.
        
        Args:
            button: Número del botón (0=izquierdo, 1=medio, 2=derecho)
            
        Returns:
            True si el botón está presionado
        """
        
        if 0 <= button < len(self.mouse_buttons):
            return self.mouse_buttons[button]
        return False
    
    def remap_action(self, action: str, new_key: str, input_type: str = 'keyboard'):
        """
        Remapea una acción a una nueva tecla o botón.
        
        Args:
            action: Nombre de la acción a remapear
            new_key: Nueva tecla o botón
            input_type: Tipo de entrada ('keyboard' o 'gamepad')
        """
        
        if input_type == 'keyboard':
            key_code = self._get_key_code(new_key)
            if key_code is not None:
                self.keyboard_mapping[action] = [key_code]
                print(f"Acción '{action}' remapeada a tecla '{new_key}'")
            else:
                print(f"Tecla '{new_key}' no reconocida")
        
        elif input_type == 'gamepad':
            try:
                button_code = int(new_key)
                self.gamepad_mapping[action] = [button_code]
                print(f"Acción '{action}' remapeada a botón de gamepad {button_code}")
            except ValueError:
                print(f"Botón de gamepad '{new_key}' no válido")
    
    def load_from_config(self, config_data: Dict[str, Any]):
        """
        Carga la configuración de controles desde un diccionario.
        
        Args:
            config_data: Diccionario con la configuración de controles
        """
        
        try:
            # Cargar mapeo de teclado
            if 'keyboard' in config_data:
                for action, keys in config_data['keyboard'].items():
                    self.keyboard_mapping[action] = []
                    for key_name in keys:
                        key_code = self._get_key_code(key_name)
                        if key_code is not None:
                            self.keyboard_mapping[action].append(key_code)
            
            # Cargar mapeo de gamepad
            if 'gamepad' in config_data:
                self.gamepad_mapping = config_data['gamepad'].copy()
            
            print("Configuración de controles cargada desde config")
            
        except Exception as e:
            print(f"Error cargando configuración de controles: {e}")
            self._load_default_mapping()
    
    def get_config_data(self) -> Dict[str, Any]:
        """
        Obtiene la configuración actual de controles para guardar.
        
        Returns:
            Diccionario con la configuración actual
        """
        
        # Convertir códigos de tecla de vuelta a nombres
        keyboard_config = {}
        for action, key_codes in self.keyboard_mapping.items():
            keyboard_config[action] = []
            for key_code in key_codes:
                # Buscar el nombre de la tecla
                key_name = pygame.key.name(key_code)
                keyboard_config[action].append(key_name)
        
        return {
            'keyboard': keyboard_config,
            'gamepad': self.gamepad_mapping.copy()
        }
    
    def reset_to_defaults(self):
        """Resetea todos los controles a los valores por defecto."""
        
        print("Reseteando controles a valores por defecto")
        self._load_default_mapping()
    
    def get_action_display_name(self, action: str) -> str:
        """
        Obtiene el nombre para mostrar de una acción.
        
        Args:
            action: Nombre interno de la acción
            
        Returns:
            Nombre legible para el usuario
        """
        
        display_names = {
            'move_left': 'Mover Izquierda',
            'move_right': 'Mover Derecha',
            'move_up': 'Mover Arriba',
            'move_down': 'Mover Abajo',
            'jump': 'Saltar',
            'attack_light': 'Ataque Ligero',
            'attack_heavy': 'Ataque Pesado',
            'roll': 'Rodar/Esquivar',
            'parry': 'Parry',
            'pause': 'Pausa',
            'confirm': 'Confirmar',
            'cancel': 'Cancelar'
        }
        
        return display_names.get(action, action.replace('_', ' ').title())
    
    def get_current_keys_for_action(self, action: str) -> List[str]:
        """
        Obtiene las teclas actuales asignadas a una acción.
        
        Args:
            action: Nombre de la acción
            
        Returns:
            Lista de nombres de teclas asignadas
        """
        
        key_names = []
        
        # Agregar teclas de teclado
        for key_code in self.keyboard_mapping.get(action, []):
            key_name = pygame.key.name(key_code)
            key_names.append(key_name)
        
        # Agregar botones de gamepad
        for button_code in self.gamepad_mapping.get(action, []):
            if button_code >= 0:
                key_names.append(f"Gamepad {button_code}")
            else:
                # Botones especiales del stick analógico
                direction_names = {-1: "Stick Izq", 1: "Stick Der", -2: "Stick Arr", 2: "Stick Aba"}
                key_names.append(direction_names.get(button_code, f"Gamepad {button_code}"))
        
        return key_names if key_names else ["Sin asignar"]