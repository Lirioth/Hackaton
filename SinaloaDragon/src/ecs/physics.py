"""
Sistema de Físicas para Chen Toka - Sinaloa Dragon

Este módulo maneja todas las colisiones, detección de hitboxes,
y sistemas físicos del juego.
"""

import pygame
import math
from typing import List, Tuple, Optional, Dict, Any, Set
from settings import Settings


class CollisionType:
    """Tipos de colisión."""
    NONE = 0
    SOLID = 1
    PLATFORM = 2  # Se puede atravesar desde abajo
    DAMAGE = 3
    TRIGGER = 4


class PhysicsWorld:
    """
    Mundo físico que maneja todas las colisiones y detecciones.
    """
    
    def __init__(self):
        """Inicializa el mundo físico."""
        
        # Entidades registradas
        self.solid_objects: List[pygame.Rect] = []
        self.platforms: List[pygame.Rect] = []
        self.damage_zones: List[pygame.Rect] = []
        self.triggers: List[Dict[str, Any]] = []
        
        # Cache de colisiones para optimización
        self.collision_cache: Dict[str, List[pygame.Rect]] = {}
        self.cache_dirty = True
        
        print("Mundo físico inicializado")
    
    def clear(self):
        """Limpia todas las entidades del mundo físico."""
        
        self.solid_objects.clear()
        self.platforms.clear()
        self.damage_zones.clear()
        self.triggers.clear()
        self.collision_cache.clear()
        self.cache_dirty = True
    
    def add_solid_object(self, rect: pygame.Rect):
        """
        Añade un objeto sólido al mundo.
        
        Args:
            rect: Rectángulo del objeto sólido
        """
        
        self.solid_objects.append(rect)
        self.cache_dirty = True
    
    def add_platform(self, rect: pygame.Rect):
        """
        Añade una plataforma traversable al mundo.
        
        Args:
            rect: Rectángulo de la plataforma
        """
        
        self.platforms.append(rect)
        self.cache_dirty = True
    
    def add_damage_zone(self, rect: pygame.Rect):
        """
        Añade una zona de daño al mundo.
        
        Args:
            rect: Rectángulo de la zona de daño
        """
        
        self.damage_zones.append(rect)
        self.cache_dirty = True
    
    def add_trigger(self, rect: pygame.Rect, trigger_id: str, data: Dict[str, Any] = None):
        """
        Añade un trigger al mundo.
        
        Args:
            rect: Rectángulo del trigger
            trigger_id: ID único del trigger
            data: Datos adicionales del trigger
        """
        
        trigger = {
            'rect': rect,
            'id': trigger_id,
            'data': data or {},
            'activated': False
        }
        self.triggers.append(trigger)
        self.cache_dirty = True
    
    def check_collision(self, rect: pygame.Rect, collision_type: int) -> List[pygame.Rect]:
        """
        Verifica colisiones de un rectángulo con objetos del tipo especificado.
        
        Args:
            rect: Rectángulo a verificar
            collision_type: Tipo de colisión a verificar
            
        Returns:
            Lista de rectángulos con los que colisiona
        """
        
        collisions = []
        
        if collision_type == CollisionType.SOLID:
            for solid in self.solid_objects:
                if rect.colliderect(solid):
                    collisions.append(solid)
        
        elif collision_type == CollisionType.PLATFORM:
            for platform in self.platforms:
                if rect.colliderect(platform):
                    collisions.append(platform)
        
        elif collision_type == CollisionType.DAMAGE:
            for damage_zone in self.damage_zones:
                if rect.colliderect(damage_zone):
                    collisions.append(damage_zone)
        
        return collisions
    
    def check_triggers(self, rect: pygame.Rect) -> List[Dict[str, Any]]:
        """
        Verifica activación de triggers.
        
        Args:
            rect: Rectángulo que puede activar triggers
            
        Returns:
            Lista de triggers activados
        """
        
        activated_triggers = []
        
        for trigger in self.triggers:
            if rect.colliderect(trigger['rect']) and not trigger['activated']:
                trigger['activated'] = True
                activated_triggers.append(trigger)
        
        return activated_triggers
    
    def resolve_collision(self, rect: pygame.Rect, velocity: Tuple[float, float], 
                         collision_type: int) -> Tuple[pygame.Rect, Tuple[float, float], bool]:
        """
        Resuelve colisiones y ajusta posición/velocidad.
        
        Args:
            rect: Rectángulo del objeto
            velocity: Velocidad actual (vx, vy)
            collision_type: Tipo de colisión a resolver
            
        Returns:
            Tupla (nuevo_rect, nueva_velocidad, en_suelo)
        """
        
        new_rect = rect.copy()
        new_velocity = list(velocity)
        on_ground = False
        
        collisions = self.check_collision(new_rect, collision_type)
        
        if not collisions:
            return new_rect, tuple(new_velocity), on_ground
        
        # Resolver colisiones según el tipo
        if collision_type == CollisionType.SOLID:
            new_rect, new_velocity, on_ground = self._resolve_solid_collision(
                new_rect, new_velocity, collisions
            )
        
        elif collision_type == CollisionType.PLATFORM:
            new_rect, new_velocity, on_ground = self._resolve_platform_collision(
                new_rect, new_velocity, collisions
            )
        
        return new_rect, tuple(new_velocity), on_ground
    
    def _resolve_solid_collision(self, rect: pygame.Rect, velocity: List[float], 
                               collisions: List[pygame.Rect]) -> Tuple[pygame.Rect, List[float], bool]:
        """
        Resuelve colisiones con objetos sólidos.
        
        Args:
            rect: Rectángulo del objeto
            velocity: Velocidad actual
            collisions: Lista de objetos sólidos en colisión
            
        Returns:
            Tupla (nuevo_rect, nueva_velocidad, en_suelo)
        """
        
        on_ground = False
        
        for solid in collisions:
            # Calcular overlap en cada eje
            overlap_x = min(rect.right - solid.left, solid.right - rect.left)
            overlap_y = min(rect.bottom - solid.top, solid.bottom - rect.top)
            
            # Resolver el eje con menor overlap primero
            if overlap_x < overlap_y:
                # Colisión horizontal
                if rect.centerx < solid.centerx:
                    # Empujar hacia la izquierda
                    rect.right = solid.left
                else:
                    # Empujar hacia la derecha
                    rect.left = solid.right
                
                velocity[0] = 0  # Detener movimiento horizontal
            else:
                # Colisión vertical
                if rect.centery < solid.centery:
                    # Empujar hacia arriba (aterrizaje)
                    rect.bottom = solid.top
                    on_ground = True
                    velocity[1] = 0  # Detener caída
                else:
                    # Empujar hacia abajo (golpe de cabeza)
                    rect.top = solid.bottom
                    velocity[1] = max(0, velocity[1])  # Solo permitir caída
        
        return rect, velocity, on_ground
    
    def _resolve_platform_collision(self, rect: pygame.Rect, velocity: List[float], 
                                  collisions: List[pygame.Rect]) -> Tuple[pygame.Rect, List[float], bool]:
        """
        Resuelve colisiones con plataformas (solo desde arriba).
        
        Args:
            rect: Rectángulo del objeto
            velocity: Velocidad actual
            collisions: Lista de plataformas en colisión
            
        Returns:
            Tupla (nuevo_rect, nueva_velocidad, en_suelo)
        """
        
        on_ground = False
        
        for platform in collisions:
            # Solo colisionar si viene desde arriba y está cayendo
            if velocity[1] >= 0 and rect.bottom <= platform.top + 10:
                rect.bottom = platform.top
                velocity[1] = 0
                on_ground = True
        
        return rect, velocity, on_ground
    
    def move_and_collide(self, rect: pygame.Rect, velocity: Tuple[float, float], 
                        dt: float) -> Tuple[pygame.Rect, Tuple[float, float], bool]:
        """
        Mueve un objeto y resuelve colisiones en un solo paso.
        
        Args:
            rect: Rectángulo del objeto
            velocity: Velocidad en píxeles por segundo
            dt: Delta time en segundos
            
        Returns:
            Tupla (nuevo_rect, velocidad_final, en_suelo)
        """
        
        # Calcular nueva posición
        new_x = rect.x + velocity[0] * dt
        new_y = rect.y + velocity[1] * dt
        
        new_rect = pygame.Rect(new_x, new_y, rect.width, rect.height)
        final_velocity = list(velocity)
        on_ground = False
        
        # Resolver colisiones con sólidos
        new_rect, final_velocity, ground_collision = self.resolve_collision(
            new_rect, final_velocity, CollisionType.SOLID
        )
        
        if ground_collision:
            on_ground = True
        
        # Resolver colisiones con plataformas
        new_rect, final_velocity, platform_collision = self.resolve_collision(
            new_rect, final_velocity, CollisionType.PLATFORM
        )
        
        if platform_collision:
            on_ground = True
        
        return new_rect, tuple(final_velocity), on_ground
    
    def raycast(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[Tuple[float, float]]:
        """
        Lanza un rayo y encuentra el primer punto de colisión.
        
        Args:
            start: Punto inicial (x, y)
            end: Punto final (x, y)
            
        Returns:
            Punto de colisión o None si no hay colisión
        """
        
        # Implementación simple de raycast usando DDA o similar
        # Por simplicidad, usamos una aproximación por pasos
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return None
        
        # Normalizar dirección
        dir_x = dx / distance
        dir_y = dy / distance
        
        # Avanzar por pasos pequeños
        step_size = 2.0
        steps = int(distance / step_size)
        
        for i in range(steps):
            x = start[0] + dir_x * step_size * i
            y = start[1] + dir_y * step_size * i
            
            # Crear punto como rectángulo pequeño
            point_rect = pygame.Rect(x - 1, y - 1, 2, 2)
            
            # Verificar colisión con sólidos
            if self.check_collision(point_rect, CollisionType.SOLID):
                return (x, y)
        
        return None
    
    def get_ground_height(self, x: float, max_search_distance: float = 100.0) -> Optional[float]:
        """
        Encuentra la altura del suelo en una posición X específica.
        
        Args:
            x: Posición X donde buscar
            max_search_distance: Distancia máxima hacia abajo a buscar
            
        Returns:
            Altura Y del suelo o None si no se encuentra
        """
        
        # Buscar hacia abajo desde arriba de la pantalla
        start_y = -10
        end_y = start_y + max_search_distance
        
        collision_point = self.raycast((x, start_y), (x, end_y))
        
        if collision_point:
            return collision_point[1]
        
        return None


class CombatSystem:
    """
    Sistema de combate que maneja hitboxes, hurtboxes y detección de golpes.
    """
    
    def __init__(self):
        """Inicializa el sistema de combate."""
        
        # Entidades activas en combate
        self.attackers: List[Dict[str, Any]] = []
        self.defenders: List[Dict[str, Any]] = []
        
        # Historial de golpes para evitar múltiples hits
        self.hit_history: Dict[str, Set[str]] = {}
        
        print("Sistema de combate inicializado")
    
    def register_attacker(self, entity_id: str, hitbox: pygame.Rect, 
                         damage: int, knockback: Tuple[float, float] = (0, 0),
                         properties: Dict[str, Any] = None):
        """
        Registra una entidad como atacante.
        
        Args:
            entity_id: ID único de la entidad
            hitbox: Rectángulo del hitbox de ataque
            damage: Daño del ataque
            knockback: Fuerza de knockback (x, y)
            properties: Propiedades adicionales del ataque
        """
        
        attacker = {
            'id': entity_id,
            'hitbox': hitbox,
            'damage': damage,
            'knockback': knockback,
            'properties': properties or {},
            'active': True
        }
        
        self.attackers.append(attacker)
        
        # Inicializar historial de hits
        if entity_id not in self.hit_history:
            self.hit_history[entity_id] = set()
    
    def register_defender(self, entity_id: str, hurtbox: pygame.Rect,
                         on_hit_callback = None, properties: Dict[str, Any] = None):
        """
        Registra una entidad como defendible.
        
        Args:
            entity_id: ID único de la entidad
            hurtbox: Rectángulo del hurtbox
            on_hit_callback: Función a llamar cuando recibe daño
            properties: Propiedades adicionales del defensor
        """
        
        defender = {
            'id': entity_id,
            'hurtbox': hurtbox,
            'on_hit': on_hit_callback,
            'properties': properties or {},
            'active': True
        }
        
        self.defenders.append(defender)
    
    def update(self, dt: float) -> List[Dict[str, Any]]:
        """
        Actualiza el sistema de combate y detecta colisiones.
        
        Args:
            dt: Delta time en segundos
            
        Returns:
            Lista de eventos de hit que ocurrieron
        """
        
        hit_events = []
        
        # Verificar colisiones entre atacantes y defensores
        for attacker in self.attackers:
            if not attacker['active']:
                continue
            
            for defender in self.defenders:
                if not defender['active']:
                    continue
                
                # No atacarse a sí mismo
                if attacker['id'] == defender['id']:
                    continue
                
                # Verificar si ya golpeó a este defensor
                if defender['id'] in self.hit_history[attacker['id']]:
                    continue
                
                # Verificar colisión de hitboxes
                if attacker['hitbox'].colliderect(defender['hurtbox']):
                    # Crear evento de hit
                    hit_event = {
                        'attacker_id': attacker['id'],
                        'defender_id': defender['id'],
                        'damage': attacker['damage'],
                        'knockback': attacker['knockback'],
                        'attacker_props': attacker['properties'],
                        'defender_props': defender['properties'],
                        'hit_point': (
                            (attacker['hitbox'].centerx + defender['hurtbox'].centerx) // 2,
                            (attacker['hitbox'].centery + defender['hurtbox'].centery) // 2
                        )
                    }
                    
                    hit_events.append(hit_event)
                    
                    # Registrar hit para evitar múltiples golpes
                    self.hit_history[attacker['id']].add(defender['id'])
                    
                    # Llamar callback del defensor si existe
                    if defender['on_hit']:
                        try:
                            defender['on_hit'](hit_event)
                        except Exception as e:
                            print(f"Error en callback de hit: {e}")
        
        return hit_events
    
    def clear_attackers(self):
        """Limpia todos los atacantes."""
        
        self.attackers.clear()
    
    def clear_defenders(self):
        """Limpia todos los defensores."""
        
        self.defenders.clear()
    
    def clear_hit_history(self, entity_id: str = None):
        """
        Limpia el historial de hits.
        
        Args:
            entity_id: ID específico a limpiar, o None para limpiar todo
        """
        
        if entity_id:
            if entity_id in self.hit_history:
                self.hit_history[entity_id].clear()
        else:
            self.hit_history.clear()
    
    def deactivate_attacker(self, entity_id: str):
        """
        Desactiva un atacante específico.
        
        Args:
            entity_id: ID del atacante a desactivar
        """
        
        for attacker in self.attackers:
            if attacker['id'] == entity_id:
                attacker['active'] = False
    
    def deactivate_defender(self, entity_id: str):
        """
        Desactiva un defensor específico.
        
        Args:
            entity_id: ID del defensor a desactivar
        """
        
        for defender in self.defenders:
            if defender['id'] == entity_id:
                defender['active'] = False


def calculate_knockback_force(attacker_pos: Tuple[float, float], 
                            defender_pos: Tuple[float, float],
                            force_magnitude: float) -> Tuple[float, float]:
    """
    Calcula la fuerza de knockback basada en posiciones.
    
    Args:
        attacker_pos: Posición del atacante (x, y)
        defender_pos: Posición del defensor (x, y)
        force_magnitude: Magnitud de la fuerza
        
    Returns:
        Tupla (force_x, force_y) con las componentes de la fuerza
    """
    
    dx = defender_pos[0] - attacker_pos[0]
    dy = defender_pos[1] - attacker_pos[1]
    
    distance = math.sqrt(dx * dx + dy * dy)
    
    if distance == 0:
        return (force_magnitude, 0)  # Fuerza hacia la derecha por defecto
    
    # Normalizar y aplicar magnitud
    force_x = (dx / distance) * force_magnitude
    force_y = (dy / distance) * force_magnitude * 0.5  # Menor fuerza vertical
    
    return (force_x, force_y)


def rect_to_dict(rect: pygame.Rect) -> Dict[str, int]:
    """
    Convierte un Rect a diccionario para serialización.
    
    Args:
        rect: Rectángulo de pygame
        
    Returns:
        Diccionario con las propiedades del rectángulo
    """
    
    return {
        'x': rect.x,
        'y': rect.y,
        'width': rect.width,
        'height': rect.height
    }


def dict_to_rect(rect_dict: Dict[str, int]) -> pygame.Rect:
    """
    Convierte un diccionario a Rect.
    
    Args:
        rect_dict: Diccionario con propiedades del rectángulo
        
    Returns:
        Rectángulo de pygame
    """
    
    return pygame.Rect(
        rect_dict['x'],
        rect_dict['y'], 
        rect_dict['width'],
        rect_dict['height']
    )