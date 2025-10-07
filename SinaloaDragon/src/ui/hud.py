"""
Sistema de HUD para Chen Toka - Sinaloa Dragon

Este módulo maneja toda la interfaz de usuario en pantalla durante el gameplay,
incluyendo barras de vida, contador de monedas, super meter y efectos visuales.
"""

import pygame
import math
from typing import Dict, List, Tuple, Any, Optional
from settings import Settings


class HUDElement:
    """Elemento base del HUD."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        """
        Inicializa un elemento del HUD.
        
        Args:
            x: Posición X
            y: Posición Y  
            width: Ancho del elemento
            height: Alto del elemento
        """
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.rect = pygame.Rect(x, y, width, height)
    
    def update(self, dt: float):
        """
        Actualiza el elemento del HUD.
        
        Args:
            dt: Delta time en segundos
        """
        pass
    
    def render(self, surface: pygame.Surface, font: pygame.font.Font):
        """
        Renderiza el elemento del HUD.
        
        Args:
            surface: Superficie donde renderizar
            font: Fuente a usar
        """
        pass


class HealthBar(HUDElement):
    """Barra de vida del jugador."""
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 120, 16)
        
        self.current_hp = Settings.PLAYER_MAX_HP
        self.max_hp = Settings.PLAYER_MAX_HP
        self.display_hp = float(self.current_hp)  # Para animación suave
        
        # Animación
        self.damage_flash_timer = 0.0
        self.heal_flash_timer = 0.0
        
        # Corazones
        self.heart_size = 12
        self.heart_spacing = 16
        self.hearts_per_row = 5
    
    def set_hp(self, current_hp: int, max_hp: int):
        """
        Actualiza los valores de HP.
        
        Args:
            current_hp: HP actual
            max_hp: HP máximo
        """
        
        old_hp = self.current_hp
        self.current_hp = max(0, min(current_hp, max_hp))
        self.max_hp = max_hp
        
        # Activar efectos
        if self.current_hp < old_hp:
            self.damage_flash_timer = 0.5
        elif self.current_hp > old_hp:
            self.heal_flash_timer = 0.3
    
    def update(self, dt: float):
        """Actualiza la animación de la barra de vida."""
        
        # Suavizar cambios de HP
        hp_diff = self.current_hp - self.display_hp
        if abs(hp_diff) > 0.1:
            self.display_hp += hp_diff * 5.0 * dt
        else:
            self.display_hp = float(self.current_hp)
        
        # Actualizar timers de flash
        self.damage_flash_timer -= dt
        self.heal_flash_timer -= dt
    
    def render(self, surface: pygame.Surface, font: pygame.font.Font):
        """Renderiza la barra de vida como corazones."""
        
        if not self.visible:
            return
        
        # Calcular número de corazones
        hearts_to_show = math.ceil(self.max_hp / Settings.HEART_DISPLAY_VALUE)
        filled_hearts = self.display_hp / Settings.HEART_DISPLAY_VALUE
        
        # Renderizar corazones
        for i in range(hearts_to_show):
            heart_x = self.x + (i % self.hearts_per_row) * self.heart_spacing
            heart_y = self.y + (i // self.hearts_per_row) * self.heart_spacing
            
            # Determinar tipo de corazón
            if i < int(filled_hearts):
                color = Settings.COLOR_HP_FULL
            elif i < filled_hearts:
                # Corazón parcial
                color = Settings.COLOR_HP_FULL
            else:
                color = Settings.COLOR_HP_EMPTY
            
            # Aplicar efectos de flash
            if self.damage_flash_timer > 0 and int(self.damage_flash_timer * 10) % 2:
                color = Settings.COLOR_WHITE
            elif self.heal_flash_timer > 0:
                color = Settings.COLOR_GREEN
            
            # Dibujar corazón como rectángulo con forma simple
            heart_rect = pygame.Rect(heart_x, heart_y, self.heart_size, self.heart_size)
            pygame.draw.rect(surface, color, heart_rect)
            
            # Borde
            pygame.draw.rect(surface, Settings.COLOR_BLACK, heart_rect, 1)
            
            # Si es corazón parcial, mostrar fracción
            if i == int(filled_hearts) and filled_hearts % 1 != 0:
                partial_width = int(self.heart_size * (filled_hearts % 1))
                partial_rect = pygame.Rect(heart_x, heart_y, partial_width, self.heart_size)
                pygame.draw.rect(surface, Settings.COLOR_HP_FULL, partial_rect)


class SuperMeter(HUDElement):
    """Super meter del jugador."""
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 80, 12)
        
        self.current_super = 0
        self.max_super = Settings.SUPER_METER_MAX
        self.display_super = 0.0
        
        # Segmentos
        self.segment_width = 24
        self.segment_height = 8
        self.segment_spacing = 2
        
        # Efectos
        self.gain_flash_timer = 0.0
    
    def set_super(self, current_super: int):
        """
        Actualiza el super meter.
        
        Args:
            current_super: Super meter actual
        """
        
        old_super = self.current_super
        self.current_super = max(0, min(current_super, self.max_super))
        
        if self.current_super > old_super:
            self.gain_flash_timer = 0.4
    
    def update(self, dt: float):
        """Actualiza la animación del super meter."""
        
        # Suavizar cambios
        super_diff = self.current_super - self.display_super
        if abs(super_diff) > 0.1:
            self.display_super += super_diff * 8.0 * dt
        else:
            self.display_super = float(self.current_super)
        
        self.gain_flash_timer -= dt
    
    def render(self, surface: pygame.Surface, font: pygame.font.Font):
        """Renderiza el super meter."""
        
        if not self.visible:
            return
        
        for i in range(self.max_super):
            segment_x = self.x + i * (self.segment_width + self.segment_spacing)
            segment_y = self.y
            
            # Determinar color del segmento
            if i < int(self.display_super):
                color = Settings.COLOR_SUPER_FULL
            elif i < self.display_super:
                # Segmento parcial
                color = Settings.COLOR_SUPER_FULL
            else:
                color = Settings.COLOR_SUPER_EMPTY
            
            # Efecto de flash
            if self.gain_flash_timer > 0 and int(self.gain_flash_timer * 15) % 2:
                color = Settings.COLOR_WHITE
            
            # Dibujar segmento
            segment_rect = pygame.Rect(segment_x, segment_y, self.segment_width, self.segment_height)
            pygame.draw.rect(surface, color, segment_rect)
            pygame.draw.rect(surface, Settings.COLOR_BLACK, segment_rect, 1)
            
            # Relleno parcial
            if i == int(self.display_super) and self.display_super % 1 != 0:
                partial_width = int(self.segment_width * (self.display_super % 1))
                partial_rect = pygame.Rect(segment_x, segment_y, partial_width, self.segment_height)
                pygame.draw.rect(surface, Settings.COLOR_SUPER_FULL, partial_rect)


class ComboCounter(HUDElement):
    """Contador de combo."""
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 80, 20)
        
        self.combo_count = 0
        self.display_combo = 0.0
        self.combo_timer = 0.0
        
        # Efectos
        self.pulse_timer = 0.0
        self.scale_factor = 1.0
    
    def set_combo(self, combo_count: int, combo_timer: float):
        """
        Actualiza el contador de combo.
        
        Args:
            combo_count: Número de hits en el combo
            combo_timer: Tiempo restante del combo
        """
        
        old_combo = self.combo_count
        self.combo_count = max(0, combo_count)
        self.combo_timer = combo_timer
        
        if self.combo_count > old_combo:
            self.pulse_timer = 0.2
    
    def update(self, dt: float):
        """Actualiza la animación del contador."""
        
        # Suavizar cambios
        combo_diff = self.combo_count - self.display_combo
        if abs(combo_diff) > 0.1:
            self.display_combo += combo_diff * 10.0 * dt
        else:
            self.display_combo = float(self.combo_count)
        
        # Efecto de pulso
        if self.pulse_timer > 0:
            self.pulse_timer -= dt
            self.scale_factor = 1.0 + math.sin(self.pulse_timer * 20) * 0.2
        else:
            self.scale_factor = 1.0
    
    def render(self, surface: pygame.Surface, font: pygame.font.Font):
        """Renderiza el contador de combo."""
        
        if not self.visible or self.combo_count <= 0:
            return
        
        # Texto del combo
        combo_text = f"COMBO {int(self.display_combo)}"
        
        # Color según el combo
        if self.combo_count >= 20:
            color = Settings.COLOR_PURPLE
        elif self.combo_count >= 10:
            color = Settings.COLOR_ORANGE
        elif self.combo_count >= 5:
            color = Settings.COLOR_YELLOW
        else:
            color = Settings.COLOR_WHITE
        
        # Renderizar texto con escala
        text_surface = font.render(combo_text, True, color)
        
        if self.scale_factor != 1.0:
            # Escalar texto
            scaled_size = (
                int(text_surface.get_width() * self.scale_factor),
                int(text_surface.get_height() * self.scale_factor)
            )
            text_surface = pygame.transform.scale(text_surface, scaled_size)
        
        # Centrar texto
        text_rect = text_surface.get_rect()
        text_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
        
        surface.blit(text_surface, text_rect)
        
        # Barra de tiempo del combo
        if self.combo_timer > 0:
            bar_width = int(60 * (self.combo_timer / Settings.COMBO_WINDOW))
            bar_rect = pygame.Rect(self.x + 10, self.y + 15, bar_width, 3)
            pygame.draw.rect(surface, color, bar_rect)


class CoinCounter(HUDElement):
    """Contador de monedas."""
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 80, 16)
        
        self.coin_count = 0
        self.display_coins = 0.0
        
        # Efectos
        self.gain_flash_timer = 0.0
    
    def set_coins(self, coin_count: int):
        """
        Actualiza el contador de monedas.
        
        Args:
            coin_count: Número de monedas
        """
        
        old_coins = self.coin_count
        self.coin_count = max(0, coin_count)
        
        if self.coin_count > old_coins:
            self.gain_flash_timer = 0.3
    
    def update(self, dt: float):
        """Actualiza la animación del contador."""
        
        # Suavizar cambios
        coin_diff = self.coin_count - self.display_coins
        if abs(coin_diff) > 0.1:
            self.display_coins += coin_diff * 6.0 * dt
        else:
            self.display_coins = float(self.coin_count)
        
        self.gain_flash_timer -= dt
    
    def render(self, surface: pygame.Surface, font: pygame.font.Font):
        """Renderiza el contador de monedas."""
        
        if not self.visible:
            return
        
        # Icono de moneda (círculo simple)
        coin_x = self.x
        coin_y = self.y + 2
        coin_color = Settings.COLOR_YELLOW
        
        if self.gain_flash_timer > 0 and int(self.gain_flash_timer * 12) % 2:
            coin_color = Settings.COLOR_WHITE
        
        pygame.draw.circle(surface, coin_color, (coin_x + 6, coin_y + 6), 6)
        pygame.draw.circle(surface, Settings.COLOR_BLACK, (coin_x + 6, coin_y + 6), 6, 1)
        
        # Texto del contador
        coin_text = f"{int(self.display_coins)}"
        text_color = coin_color if self.gain_flash_timer > 0 else Settings.COLOR_WHITE
        text_surface = font.render(coin_text, True, text_color)
        
        surface.blit(text_surface, (self.x + 16, self.y))


class DamageNumber:
    """Número de daño flotante."""
    
    def __init__(self, x: float, y: float, damage: int, is_critical: bool = False):
        """
        Inicializa un número de daño.
        
        Args:
            x: Posición X inicial
            y: Posición Y inicial
            damage: Cantidad de daño
            is_critical: Si es un golpe crítico
        """
        
        self.x = float(x)
        self.y = float(y)
        self.damage = damage
        self.is_critical = is_critical
        
        # Movimiento
        self.velocity_x = (pygame.time.get_ticks() % 20 - 10) * 0.5
        self.velocity_y = -60.0  # Movimiento hacia arriba
        
        # Vida
        self.lifetime = 1.5
        self.max_lifetime = 1.5
        
        # Escala
        self.scale = 1.5 if is_critical else 1.0
        
        # Color
        self.color = Settings.COLOR_ORANGE if is_critical else Settings.COLOR_WHITE
    
    def update(self, dt: float):
        """Actualiza el número de daño."""
        
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Aplicar gravedad suave
        self.velocity_y += 30.0 * dt
        
        # Reducir vida
        self.lifetime -= dt
        
        # Fade out
        if self.lifetime < 0.5:
            alpha_factor = self.lifetime / 0.5
            # Nota: Para alpha real necesitaríamos crear surface temporal
    
    def render(self, surface: pygame.Surface, font: pygame.font.Font):
        """Renderiza el número de daño."""
        
        if self.lifetime <= 0:
            return
        
        damage_text = str(self.damage)
        if self.is_critical:
            damage_text = f"CRIT {damage_text}!"
        
        text_surface = font.render(damage_text, True, self.color)
        
        # Aplicar escala si es crítico
        if self.scale != 1.0:
            scaled_size = (
                int(text_surface.get_width() * self.scale),
                int(text_surface.get_height() * self.scale)
            )
            text_surface = pygame.transform.scale(text_surface, scaled_size)
        
        # Centrar texto
        text_rect = text_surface.get_rect()
        text_rect.center = (int(self.x), int(self.y))
        
        surface.blit(text_surface, text_rect)
    
    def is_expired(self) -> bool:
        """Verifica si el número ha expirado."""
        return self.lifetime <= 0


class HUD:
    """
    Sistema principal del HUD.
    """
    
    def __init__(self):
        """Inicializa el HUD."""
        
        # Elementos del HUD
        self.health_bar = HealthBar(10, 10)
        self.super_meter = SuperMeter(Settings.GAME_WIDTH - 90, 10)
        self.combo_counter = ComboCounter(Settings.GAME_WIDTH - 90, 30)
        self.coin_counter = CoinCounter(10, 30)
        
        # Números de daño flotantes
        self.damage_numbers: List[DamageNumber] = []
        
        # Estado del HUD
        self.visible = True
        self.fade_alpha = 255
        
        # Configuración
        self.show_damage_numbers = True
        
        print("HUD inicializado")
    
    def update_player_stats(self, hp: int, max_hp: int, super_meter: int, 
                          combo_count: int, combo_timer: float, coins: int):
        """
        Actualiza las estadísticas del jugador en el HUD.
        
        Args:
            hp: HP actual
            max_hp: HP máximo
            super_meter: Super meter actual
            combo_count: Contador de combo
            combo_timer: Tiempo restante del combo
            coins: Número de monedas
        """
        
        self.health_bar.set_hp(hp, max_hp)
        self.super_meter.set_super(super_meter)
        self.combo_counter.set_combo(combo_count, combo_timer)
        self.coin_counter.set_coins(coins)
    
    def add_damage_number(self, x: float, y: float, damage: int, is_critical: bool = False):
        """
        Añade un número de daño flotante.
        
        Args:
            x: Posición X
            y: Posición Y
            damage: Cantidad de daño
            is_critical: Si es crítico
        """
        
        if self.show_damage_numbers:
            damage_number = DamageNumber(x, y, damage, is_critical)
            self.damage_numbers.append(damage_number)
    
    def update(self, dt: float):
        """
        Actualiza el HUD.
        
        Args:
            dt: Delta time en segundos
        """
        
        if not self.visible:
            return
        
        # Actualizar elementos
        self.health_bar.update(dt)
        self.super_meter.update(dt)
        self.combo_counter.update(dt)
        self.coin_counter.update(dt)
        
        # Actualizar números de daño
        for damage_number in self.damage_numbers[:]:
            damage_number.update(dt)
            
            if damage_number.is_expired():
                self.damage_numbers.remove(damage_number)
    
    def render(self, surface: pygame.Surface, font: pygame.font.Font):
        """
        Renderiza el HUD.
        
        Args:
            surface: Superficie donde renderizar
            font: Fuente a usar
        """
        
        if not self.visible:
            return
        
        # Renderizar elementos principales
        self.health_bar.render(surface, font)
        self.super_meter.render(surface, font)
        self.combo_counter.render(surface, font)
        self.coin_counter.render(surface, font)
        
        # Renderizar números de daño
        for damage_number in self.damage_numbers:
            damage_number.render(surface, font)
        
        # Debug info si está habilitado
        if Settings.DEBUG_SHOW_FPS:
            self._render_debug_info(surface, font)
    
    def _render_debug_info(self, surface: pygame.Surface, font: pygame.font.Font):
        """Renderiza información de debug."""
        
        debug_y = Settings.GAME_HEIGHT - 40
        
        # FPS (se calcula en el game loop principal)
        fps_text = font.render("FPS: 60", True, Settings.COLOR_WHITE)
        surface.blit(fps_text, (10, debug_y))
        
        # Elementos del HUD activos
        hud_elements = len([e for e in [self.health_bar, self.super_meter, self.combo_counter, self.coin_counter] if e.visible])
        elements_text = font.render(f"HUD Elements: {hud_elements}", True, Settings.COLOR_WHITE)
        surface.blit(elements_text, (10, debug_y + 12))
    
    def set_visibility(self, visible: bool):
        """
        Establece la visibilidad del HUD.
        
        Args:
            visible: Si el HUD debe ser visible
        """
        
        self.visible = visible
        
        # También aplicar a elementos individuales
        self.health_bar.visible = visible
        self.super_meter.visible = visible
        self.combo_counter.visible = visible
        self.coin_counter.visible = visible
    
    def toggle_damage_numbers(self):
        """Alterna la visualización de números de daño."""
        
        self.show_damage_numbers = not self.show_damage_numbers
        
        if not self.show_damage_numbers:
            self.damage_numbers.clear()
    
    def clear_damage_numbers(self):
        """Limpia todos los números de daño."""
        
        self.damage_numbers.clear()
    
    def reset(self):
        """Resetea el HUD a su estado inicial."""
        
        self.health_bar.set_hp(Settings.PLAYER_MAX_HP, Settings.PLAYER_MAX_HP)
        self.super_meter.set_super(0)
        self.combo_counter.set_combo(0, 0)
        self.coin_counter.set_coins(0)
        self.clear_damage_numbers()
        
        print("HUD reseteado")