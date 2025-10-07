"""
Peligros y Mecánicas Especiales para Chen Toka - Sinaloa Dragon

Este módulo contiene elementos peligrosos del nivel como picos, lava,
plataformas móviles y otros obstáculos que añaden desafío al gameplay.
"""

import pygame
import math
from typing import List, Dict, Any, Optional
from settings import Settings


class Hazard:
    """Clase base para todos los peligros del juego."""
    
    def __init__(self, x: float, y: float, width: float, height: float, hazard_type: str):
        """
        Inicializa un peligro.
        
        Args:
            x, y: Posición del peligro
            width, height: Dimensiones
            hazard_type: Tipo de peligro
        """
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = hazard_type
        
        # Hitbox
        self.rect = pygame.Rect(x, y, width, height)
        
        # Estado
        self.active = True
        self.damage = 1
        
        # Animación
        self.animation_time = 0.0
    
    def update(self, dt: float):
        """
        Actualiza el peligro.
        
        Args:
            dt: Delta time en segundos
        """
        
        self.animation_time += dt
    
    def can_damage(self) -> bool:
        """Determina si el peligro puede causar daño."""
        
        return self.active
    
    def get_damage_amount(self) -> int:
        """Obtiene la cantidad de daño que causa."""
        
        return self.damage if self.can_damage() else 0
    
    def render(self, surface: pygame.Surface, camera_x: float = 0):
        """
        Renderiza el peligro.
        
        Args:
            surface: Superficie donde renderizar
            camera_x: Offset de la cámara
        """
        
        if not self.active:
            return
        
        screen_x = self.x - camera_x
        screen_y = self.y
        
        # No renderizar si está fuera de pantalla
        if screen_x + self.width < 0 or screen_x > Settings.GAME_WIDTH:
            return
        
        # Renderizar como rectángulo rojo por defecto
        render_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(surface, Settings.COLOR_RED, render_rect)


class Spikes(Hazard):
    """Picos que causan daño al contacto."""
    
    def __init__(self, x: float, y: float, width: float, direction: str = "up"):
        """
        Inicializa picos.
        
        Args:
            x, y: Posición
            width: Ancho de la fila de picos
            direction: Dirección de los picos ('up', 'down', 'left', 'right')
        """
        
        height = 16 if direction in ['up', 'down'] else width
        width = width if direction in ['up', 'down'] else 16
        
        super().__init__(x, y, width, height, "spikes")
        
        self.direction = direction
        self.damage = 2  # Los picos causan más daño
    
    def render(self, surface: pygame.Surface, camera_x: float = 0):
        """Renderiza los picos."""
        
        if not self.active:
            return
        
        screen_x = self.x - camera_x
        screen_y = self.y
        
        if screen_x + self.width < 0 or screen_x > Settings.GAME_WIDTH:
            return
        
        # Renderizar base
        base_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(surface, Settings.COLOR_DARK_GRAY, base_rect)
        
        # Renderizar picos
        spike_size = 8
        if self.direction in ['up', 'down']:
            spike_count = max(1, int(self.width // spike_size))
            for i in range(spike_count):
                spike_x = screen_x + i * spike_size
                
                if self.direction == 'up':
                    points = [
                        (spike_x, screen_y + self.height),
                        (spike_x + spike_size, screen_y + self.height),
                        (spike_x + spike_size // 2, screen_y)
                    ]
                else:  # down
                    points = [
                        (spike_x, screen_y),
                        (spike_x + spike_size, screen_y),
                        (spike_x + spike_size // 2, screen_y + self.height)
                    ]
                
                pygame.draw.polygon(surface, Settings.COLOR_RED, points)
        
        else:  # left, right
            spike_count = max(1, int(self.height // spike_size))
            for i in range(spike_count):
                spike_y = screen_y + i * spike_size
                
                if self.direction == 'left':
                    points = [
                        (screen_x + self.width, spike_y),
                        (screen_x + self.width, spike_y + spike_size),
                        (screen_x, spike_y + spike_size // 2)
                    ]
                else:  # right
                    points = [
                        (screen_x, spike_y),
                        (screen_x, spike_y + spike_size),
                        (screen_x + self.width, spike_y + spike_size // 2)
                    ]
                
                pygame.draw.polygon(surface, Settings.COLOR_RED, points)


class Lava(Hazard):
    """Lava que causa daño continuo."""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        """
        Inicializa lava.
        
        Args:
            x, y: Posición
            width, height: Dimensiones
        """
        
        super().__init__(x, y, width, height, "lava")
        
        self.damage = 3  # Daño alto
        self.bubble_timer = 0.0
        self.bubbles = []
    
    def update(self, dt: float):
        """Actualiza la lava con efectos de burbujas."""
        
        super().update(dt)
        
        # Generar burbujas
        self.bubble_timer += dt
        if self.bubble_timer >= 0.5:  # Nueva burbuja cada 0.5 segundos
            self.bubble_timer = 0.0
            
            # Añadir nueva burbuja
            bubble_x = self.x + (len(self.bubbles) * 20) % self.width
            bubble_y = self.y + self.height - 5
            self.bubbles.append({
                'x': bubble_x,
                'y': bubble_y,
                'life': 2.0,
                'size': 3
            })
        
        # Actualizar burbujas existentes
        for bubble in self.bubbles[:]:
            bubble['life'] -= dt
            bubble['y'] -= 20 * dt  # Subir
            bubble['size'] += dt  # Crecer
            
            if bubble['life'] <= 0:
                self.bubbles.remove(bubble)
    
    def render(self, surface: pygame.Surface, camera_x: float = 0):
        """Renderiza la lava con efectos animados."""
        
        if not self.active:
            return
        
        screen_x = self.x - camera_x
        screen_y = self.y
        
        if screen_x + self.width < 0 or screen_x > Settings.GAME_WIDTH:
            return
        
        # Base de lava con variación de color
        intensity = (math.sin(self.animation_time * 3) + 1) * 0.5
        color = (
            255,
            int(100 + 100 * intensity),
            int(50 * intensity)
        )
        
        lava_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(surface, color, lava_rect)
        
        # Superficie ondulada
        wave_points = []
        wave_resolution = 8
        for i in range(0, int(self.width), wave_resolution):
            wave_offset = math.sin((self.animation_time * 2) + (i * 0.1)) * 3
            wave_points.append((screen_x + i, screen_y + wave_offset))
        
        if len(wave_points) > 1:
            # Completar el polígono
            wave_points.append((screen_x + self.width, screen_y))
            wave_points.append((screen_x + self.width, screen_y + self.height))
            wave_points.append((screen_x, screen_y + self.height))
            
            pygame.draw.polygon(surface, color, wave_points)
        
        # Renderizar burbujas
        for bubble in self.bubbles:
            bubble_screen_x = bubble['x'] - camera_x
            bubble_screen_y = bubble['y']
            
            if 0 <= bubble_screen_x <= Settings.GAME_WIDTH:
                alpha = max(0, bubble['life'] / 2.0) * 255
                bubble_color = (*Settings.COLOR_YELLOW, int(alpha))
                
                # Nota: pygame.draw.circle no soporta alpha directamente
                # En una implementación completa, usarías una superficie temporal
                pygame.draw.circle(surface, Settings.COLOR_YELLOW, 
                                 (int(bubble_screen_x), int(bubble_screen_y)), 
                                 int(bubble['size']))


class MovingPlatform:
    """Plataforma móvil que se desplaza entre puntos."""
    
    def __init__(self, x: float, y: float, width: float, height: float, 
                 path_points: List[Dict[str, float]], speed: float = 50.0):
        """
        Inicializa una plataforma móvil.
        
        Args:
            x, y: Posición inicial
            width, height: Dimensiones
            path_points: Lista de puntos por los que se mueve [{'x': float, 'y': float}]
            speed: Velocidad de movimiento
        """
        
        self.start_x = x
        self.start_y = y
        self.width = width
        self.height = height
        self.speed = speed
        
        # Ruta de movimiento
        self.path_points = [{'x': x, 'y': y}] + path_points
        self.current_target = 1 if len(self.path_points) > 1 else 0
        self.reverse_direction = False
        
        # Posición actual
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, width, height)
        
        # Velocidad actual
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        print(f"Plataforma móvil creada con {len(self.path_points)} puntos")
    
    def update(self, dt: float):
        """
        Actualiza el movimiento de la plataforma.
        
        Args:
            dt: Delta time en segundos
        """
        
        if len(self.path_points) < 2:
            return
        
        # Obtener punto objetivo
        target = self.path_points[self.current_target]
        target_x, target_y = target['x'], target['y']
        
        # Calcular dirección hacia el objetivo
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 5.0:  # Llegó al objetivo
            # Mover al siguiente punto
            if not self.reverse_direction:
                self.current_target += 1
                if self.current_target >= len(self.path_points):
                    self.current_target = len(self.path_points) - 2
                    self.reverse_direction = True
            else:
                self.current_target -= 1
                if self.current_target < 0:
                    self.current_target = 1
                    self.reverse_direction = False
        else:
            # Mover hacia el objetivo
            self.vel_x = (dx / distance) * self.speed
            self.vel_y = (dy / distance) * self.speed
            
            self.x += self.vel_x * dt
            self.y += self.vel_y * dt
        
        # Actualizar rect
        self.rect.x = self.x
        self.rect.y = self.y
    
    def get_velocity(self) -> tuple[float, float]:
        """Obtiene la velocidad actual de la plataforma."""
        
        return self.vel_x, self.vel_y
    
    def render(self, surface: pygame.Surface, camera_x: float = 0):
        """
        Renderiza la plataforma móvil.
        
        Args:
            surface: Superficie donde renderizar
            camera_x: Offset de la cámara
        """
        
        screen_x = self.x - camera_x
        screen_y = self.y
        
        if screen_x + self.width < 0 or screen_x > Settings.GAME_WIDTH:
            return
        
        # Renderizar plataforma
        platform_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(surface, Settings.COLOR_BLUE, platform_rect)
        pygame.draw.rect(surface, Settings.COLOR_WHITE, platform_rect, 2)
        
        # Debug: mostrar ruta
        if Settings.DEBUG_DRAW_HITBOXES:
            for i, point in enumerate(self.path_points):
                point_screen_x = point['x'] - camera_x
                point_screen_y = point['y']
                
                if 0 <= point_screen_x <= Settings.GAME_WIDTH:
                    color = Settings.COLOR_GREEN if i == self.current_target else Settings.COLOR_YELLOW
                    pygame.draw.circle(surface, color, 
                                     (int(point_screen_x), int(point_screen_y)), 4)


class DisappearingPlatform:
    """Plataforma que desaparece después de ser pisada."""
    
    def __init__(self, x: float, y: float, width: float, height: float, 
                 disappear_time: float = 1.0, respawn_time: float = 3.0):
        """
        Inicializa una plataforma que desaparece.
        
        Args:
            x, y: Posición
            width, height: Dimensiones
            disappear_time: Tiempo antes de desaparecer
            respawn_time: Tiempo para reaparecer
        """
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.disappear_time = disappear_time
        self.respawn_time = respawn_time
        
        self.rect = pygame.Rect(x, y, width, height)
        
        # Estado
        self.state = "idle"  # "idle", "triggered", "disappearing", "gone", "respawning"
        self.timer = 0.0
        self.triggered = False
        self.flash_timer = 0.0
        self.visible = True
    
    def trigger(self):
        """Activa la plataforma para que comience a desaparecer."""
        
        if self.state == "idle":
            self.state = "triggered"
            self.timer = 0.0
            print("Plataforma activada para desaparecer")
    
    def update(self, dt: float):
        """
        Actualiza la plataforma que desaparece.
        
        Args:
            dt: Delta time en segundos
        """
        
        self.timer += dt
        self.flash_timer += dt
        
        if self.state == "triggered":
            # Parpadear antes de desaparecer
            self.visible = (self.flash_timer % 0.2) < 0.1
            
            if self.timer >= self.disappear_time:
                self.state = "gone"
                self.timer = 0.0
                self.visible = False
        
        elif self.state == "gone":
            if self.timer >= self.respawn_time:
                self.state = "respawning"
                self.timer = 0.0
        
        elif self.state == "respawning":
            # Parpadear al reaparecer
            self.visible = (self.flash_timer % 0.1) < 0.05
            
            if self.timer >= 0.5:  # Medio segundo de respawn
                self.state = "idle"
                self.visible = True
    
    def can_collide(self) -> bool:
        """Determina si la plataforma puede colisionar."""
        
        return self.state in ["idle", "triggered"] and self.visible
    
    def render(self, surface: pygame.Surface, camera_x: float = 0):
        """
        Renderiza la plataforma que desaparece.
        
        Args:
            surface: Superficie donde renderizar
            camera_x: Offset de la cámara
        """
        
        if not self.visible:
            return
        
        screen_x = self.x - camera_x
        screen_y = self.y
        
        if screen_x + self.width < 0 or screen_x > Settings.GAME_WIDTH:
            return
        
        # Color según estado
        if self.state == "triggered":
            color = Settings.COLOR_ORANGE
        elif self.state == "respawning":
            color = Settings.COLOR_LIGHT_GRAY
        else:
            color = Settings.COLOR_PURPLE
        
        platform_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(surface, color, platform_rect)
        pygame.draw.rect(surface, Settings.COLOR_WHITE, platform_rect, 1)


class HazardManager:
    """
    Administrador de todos los peligros y mecánicas especiales del nivel.
    """
    
    def __init__(self):
        """Inicializa el administrador de peligros."""
        
        self.hazards: List[Hazard] = []
        self.moving_platforms: List[MovingPlatform] = []
        self.disappearing_platforms: List[DisappearingPlatform] = []
        
        print("Administrador de peligros inicializado")
    
    def add_hazard(self, hazard: Hazard):
        """Añade un peligro al administrador."""
        
        self.hazards.append(hazard)
    
    def add_moving_platform(self, platform: MovingPlatform):
        """Añade una plataforma móvil."""
        
        self.moving_platforms.append(platform)
    
    def add_disappearing_platform(self, platform: DisappearingPlatform):
        """Añade una plataforma que desaparece."""
        
        self.disappearing_platforms.append(platform)
    
    def clear_all(self):
        """Limpia todos los peligros y plataformas especiales."""
        
        self.hazards.clear()
        self.moving_platforms.clear()
        self.disappearing_platforms.clear()
    
    def update(self, dt: float):
        """
        Actualiza todos los peligros y plataformas especiales.
        
        Args:
            dt: Delta time en segundos
        """
        
        # Actualizar peligros
        for hazard in self.hazards:
            hazard.update(dt)
        
        # Actualizar plataformas móviles
        for platform in self.moving_platforms:
            platform.update(dt)
        
        # Actualizar plataformas que desaparecen
        for platform in self.disappearing_platforms:
            platform.update(dt)
    
    def check_hazard_collisions(self, rect: pygame.Rect) -> List[Hazard]:
        """
        Verifica colisiones con peligros.
        
        Args:
            rect: Rectángulo a verificar
            
        Returns:
            Lista de peligros que colisionan
        """
        
        colliding_hazards = []
        
        for hazard in self.hazards:
            if hazard.can_damage() and hazard.rect.colliderect(rect):
                colliding_hazards.append(hazard)
        
        return colliding_hazards
    
    def get_moving_platforms_in_area(self, x: float, y: float, width: float, height: float) -> List[MovingPlatform]:
        """
        Obtiene plataformas móviles en un área.
        
        Args:
            x, y: Posición del área
            width, height: Dimensiones del área
            
        Returns:
            Lista de plataformas móviles en el área
        """
        
        area_rect = pygame.Rect(x, y, width, height)
        result = []
        
        for platform in self.moving_platforms:
            if platform.rect.colliderect(area_rect):
                result.append(platform)
        
        return result
    
    def get_disappearing_platforms_in_area(self, x: float, y: float, width: float, height: float) -> List[DisappearingPlatform]:
        """
        Obtiene plataformas que desaparecen en un área.
        
        Args:
            x, y: Posición del área
            width, height: Dimensiones del área
            
        Returns:
            Lista de plataformas que desaparecen en el área
        """
        
        area_rect = pygame.Rect(x, y, width, height)
        result = []
        
        for platform in self.disappearing_platforms:
            if platform.can_collide() and platform.rect.colliderect(area_rect):
                result.append(platform)
        
        return result
    
    def render(self, surface: pygame.Surface, camera_x: float = 0):
        """
        Renderiza todos los peligros y plataformas especiales.
        
        Args:
            surface: Superficie donde renderizar
            camera_x: Offset de la cámara
        """
        
        # Renderizar peligros
        for hazard in self.hazards:
            hazard.render(surface, camera_x)
        
        # Renderizar plataformas móviles
        for platform in self.moving_platforms:
            platform.render(surface, camera_x)
        
        # Renderizar plataformas que desaparecen
        for platform in self.disappearing_platforms:
            platform.render(surface, camera_x)