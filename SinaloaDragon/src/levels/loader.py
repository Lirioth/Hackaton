"""
Sistema de Carga de Niveles para Chen Toka - Sinaloa Dragon

Este módulo maneja la carga de niveles desde archivos JSON, incluyendo
plataformas, enemigos, objetos coleccionables y metadatos del nivel.
"""

import json
import pygame
import os
import math
from typing import Dict, List, Any, Tuple, Optional
from settings import Settings


class Platform:
    """Representa una plataforma en el nivel."""
    
    def __init__(self, x: float, y: float, width: float, height: float, 
                 platform_type: str = "solid", properties: Dict = None):
        """
        Inicializa una plataforma.
        
        Args:
            x, y: Posición de la plataforma
            width, height: Dimensiones de la plataforma
            platform_type: Tipo de plataforma ('solid', 'platform', 'destructible')
            properties: Propiedades adicionales
        """
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = platform_type
        self.properties = properties or {}
        
        # Rect para colisiones
        self.rect = pygame.Rect(x, y, width, height)
        
        # Estado
        self.destroyed = False
        self.respawn_timer = 0.0
    
    def update(self, dt: float):
        """
        Actualiza la plataforma.
        
        Args:
            dt: Delta time en segundos
        """
        
        # Manejar respawn de plataformas destructibles
        if self.destroyed and self.type == "destructible":
            self.respawn_timer += dt
            if self.respawn_timer >= self.properties.get('respawn_time', 3.0):
                self.destroyed = False
                self.respawn_timer = 0.0
    
    def destroy(self):
        """Destruye la plataforma si es destructible."""
        
        if self.type == "destructible":
            self.destroyed = True
            self.respawn_timer = 0.0
    
    def can_collide(self) -> bool:
        """Determina si la plataforma puede colisionar."""
        
        return not self.destroyed
    
    def render(self, surface: pygame.Surface, camera_x: float = 0):
        """
        Renderiza la plataforma.
        
        Args:
            surface: Superficie donde renderizar
            camera_x: Offset de la cámara
        """
        
        if self.destroyed:
            return
        
        # Posición en pantalla
        screen_x = self.x - camera_x
        screen_y = self.y
        
        # No renderizar si está fuera de pantalla
        if screen_x + self.width < 0 or screen_x > Settings.GAME_WIDTH:
            return
        
        # Color según tipo
        color_map = {
            'solid': Settings.COLOR_WHITE,
            'platform': Settings.COLOR_YELLOW,
            'destructible': Settings.COLOR_ORANGE
        }
        
        color = color_map.get(self.type, Settings.COLOR_WHITE)
        
        # Renderizar plataforma
        render_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(surface, color, render_rect)
        
        # Borde
        pygame.draw.rect(surface, Settings.COLOR_BLACK, render_rect, 1)


class Collectible:
    """Representa un objeto coleccionable."""
    
    def __init__(self, x: float, y: float, collectible_type: str, value: int = 1, properties: Dict = None):
        """
        Inicializa un coleccionable.
        
        Args:
            x, y: Posición del coleccionable
            collectible_type: Tipo ('coin', 'health', 'powerup')
            value: Valor del coleccionable
            properties: Propiedades adicionales
        """
        
        self.x = x
        self.y = y
        self.type = collectible_type
        self.value = value
        self.properties = properties or {}
        
        # Hitbox
        self.width = 16
        self.height = 16
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Estado
        self.collected = False
        self.animation_time = 0.0
        self.float_offset = 0.0
    
    def update(self, dt: float):
        """
        Actualiza el coleccionable.
        
        Args:
            dt: Delta time
        """
        
        if self.collected:
            return
        
        # Animación de flotación
        self.animation_time += dt * 3.0
        self.float_offset = math.sin(self.animation_time) * 2.0
    
    def collect(self) -> Dict[str, Any]:
        """
        Recolecta el objeto.
        
        Returns:
            Diccionario con información del coleccionable
        """
        
        if self.collected:
            return {}
        
        self.collected = True
        
        return {
            'type': self.type,
            'value': self.value,
            'properties': self.properties
        }
    
    def render(self, surface: pygame.Surface, camera_x: float = 0):
        """
        Renderiza el coleccionable.
        
        Args:
            surface: Superficie donde renderizar
            camera_x: Offset de la cámara
        """
        
        if self.collected:
            return
        
        # Posición en pantalla con flotación
        screen_x = self.x - camera_x
        screen_y = self.y + self.float_offset
        
        # No renderizar si está fuera de pantalla
        if screen_x + self.width < 0 or screen_x > Settings.GAME_WIDTH:
            return
        
        # Color según tipo
        color_map = {
            'coin': Settings.COLOR_YELLOW,
            'health': Settings.COLOR_RED,
            'powerup': Settings.COLOR_BLUE
        }
        
        color = color_map.get(self.type, Settings.COLOR_WHITE)
        
        # Renderizar como círculo
        center = (int(screen_x + self.width // 2), int(screen_y + self.height // 2))
        radius = self.width // 2
        pygame.draw.circle(surface, color, center, radius)
        pygame.draw.circle(surface, Settings.COLOR_BLACK, center, radius, 1)


class EnemySpawn:
    """Representa un punto de spawn de enemigo."""
    
    def __init__(self, x: float, y: float, enemy_type: str, properties: Dict = None):
        """
        Inicializa un spawn de enemigo.
        
        Args:
            x, y: Posición del spawn
            enemy_type: Tipo de enemigo ('maton', 'chacal', 'luchador', 'drone')
            properties: Propiedades adicionales
        """
        
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.properties = properties or {}
        
        # Control de spawn
        self.spawned = False
        self.respawn_on_death = self.properties.get('respawn', False)
        self.spawn_delay = self.properties.get('spawn_delay', 0.0)
        self.spawn_timer = 0.0
    
    def can_spawn(self) -> bool:
        """Determina si puede spawnear un enemigo."""
        
        return not self.spawned and self.spawn_timer <= 0.0
    
    def spawn_enemy(self):
        """Marca que se ha spawneado un enemigo."""
        
        self.spawned = True
    
    def on_enemy_death(self):
        """Llamado cuando el enemigo spawneado muere."""
        
        if self.respawn_on_death:
            self.spawned = False
            self.spawn_timer = self.spawn_delay
    
    def update(self, dt: float):
        """
        Actualiza el spawn.
        
        Args:
            dt: Delta time
        """
        
        if self.spawn_timer > 0.0:
            self.spawn_timer -= dt


class Level:
    """Representa un nivel completo del juego."""
    
    def __init__(self, name: str):
        """
        Inicializa un nivel.
        
        Args:
            name: Nombre del nivel
        """
        
        self.name = name
        self.width = 1920  # Ancho del nivel en píxeles
        self.height = 1080  # Alto del nivel en píxeles
        
        # Metadatos
        self.display_name = ""
        self.description = ""
        self.background_color = Settings.COLOR_SKY_BLUE
        self.background_image = None
        
        # Objetivos del nivel
        self.objectives = []
        self.completion_requirements = {}
        
        # Elementos del nivel
        self.platforms: List[Platform] = []
        self.collectibles: List[Collectible] = []
        self.enemy_spawns: List[EnemySpawn] = []
        
        # Puntos especiales
        self.player_spawn = (100, 100)  # Posición inicial del jugador
        self.exits = []  # Puntos de salida del nivel
        
        # Estado
        self.completed = False
        self.coins_collected = 0
        self.enemies_defeated = 0
        
        print(f"Nivel '{name}' inicializado")
    
    def load_from_json(self, json_data: Dict[str, Any]):
        """
        Carga el nivel desde datos JSON.
        
        Args:
            json_data: Datos del nivel en formato JSON
        """
        
        try:
            # Metadatos
            metadata = json_data.get('metadata', {})
            self.display_name = metadata.get('display_name', self.name)
            self.description = metadata.get('description', '')
            self.width = metadata.get('width', 1920)
            self.height = metadata.get('height', 1080)
            
            # Color de fondo
            bg_color = metadata.get('background_color', [135, 206, 235])
            self.background_color = tuple(bg_color)
            
            # Spawn del jugador
            spawn_data = json_data.get('player_spawn', [100, 100])
            self.player_spawn = (spawn_data[0], spawn_data[1])
            
            # Objetivos
            self.objectives = json_data.get('objectives', [])
            self.completion_requirements = json_data.get('completion_requirements', {})
            
            # Cargar plataformas
            self._load_platforms(json_data.get('platforms', []))
            
            # Cargar coleccionables
            self._load_collectibles(json_data.get('collectibles', []))
            
            # Cargar spawns de enemigos
            self._load_enemy_spawns(json_data.get('enemy_spawns', []))
            
            # Cargar salidas
            self.exits = json_data.get('exits', [])
            
            print(f"Nivel '{self.name}' cargado exitosamente")
            print(f"  - {len(self.platforms)} plataformas")
            print(f"  - {len(self.collectibles)} coleccionables") 
            print(f"  - {len(self.enemy_spawns)} spawns de enemigos")
            
        except Exception as e:
            print(f"Error cargando nivel desde JSON: {e}")
    
    def _load_platforms(self, platforms_data: List[Dict]):
        """Carga las plataformas desde datos JSON."""
        
        self.platforms.clear()
        
        for platform_data in platforms_data:
            platform = Platform(
                x=platform_data['x'],
                y=platform_data['y'],
                width=platform_data['width'],
                height=platform_data['height'],
                platform_type=platform_data.get('type', 'solid'),
                properties=platform_data.get('properties', {})
            )
            self.platforms.append(platform)
    
    def _load_collectibles(self, collectibles_data: List[Dict]):
        """Carga los coleccionables desde datos JSON."""
        
        self.collectibles.clear()
        
        for collectible_data in collectibles_data:
            collectible = Collectible(
                x=collectible_data['x'],
                y=collectible_data['y'],
                collectible_type=collectible_data.get('type', 'coin'),
                value=collectible_data.get('value', 1),
                properties=collectible_data.get('properties', {})
            )
            self.collectibles.append(collectible)
    
    def _load_enemy_spawns(self, spawns_data: List[Dict]):
        """Carga los spawns de enemigos desde datos JSON."""
        
        self.enemy_spawns.clear()
        
        for spawn_data in spawns_data:
            spawn = EnemySpawn(
                x=spawn_data['x'],
                y=spawn_data['y'],
                enemy_type=spawn_data.get('type', 'maton'),
                properties=spawn_data.get('properties', {})
            )
            self.enemy_spawns.append(spawn)
    
    def update(self, dt: float):
        """
        Actualiza el nivel.
        
        Args:
            dt: Delta time en segundos
        """
        
        # Actualizar plataformas
        for platform in self.platforms:
            platform.update(dt)
        
        # Actualizar coleccionables
        for collectible in self.collectibles:
            collectible.update(dt)
        
        # Actualizar spawns de enemigos
        for spawn in self.enemy_spawns:
            spawn.update(dt)
        
        # Verificar condiciones de completado
        self._check_completion()
    
    def _check_completion(self):
        """Verifica si el nivel se ha completado."""
        
        if self.completed:
            return
        
        # Verificar requisitos de completado
        requirements = self.completion_requirements
        
        # Verificar monedas requeridas
        required_coins = requirements.get('coins', 0)
        if required_coins > 0 and self.coins_collected < required_coins:
            return
        
        # Verificar enemigos requeridos
        required_enemies = requirements.get('enemies_defeated', 0)
        if required_enemies > 0 and self.enemies_defeated < required_enemies:
            return
        
        # Si llegamos aquí, el nivel está completado
        self.completed = True
        print(f"¡Nivel '{self.name}' completado!")
    
    def collect_item(self, collectible: Collectible) -> Dict[str, Any]:
        """
        Recolecta un objeto del nivel.
        
        Args:
            collectible: Coleccionable a recoger
            
        Returns:
            Información del objeto recolectado
        """
        
        result = collectible.collect()
        
        if result and result.get('type') == 'coin':
            self.coins_collected += result.get('value', 1)
        
        return result
    
    def on_enemy_defeated(self):
        """Llamado cuando se derrota un enemigo."""
        
        self.enemies_defeated += 1
    
    def get_platforms_in_area(self, x: float, y: float, width: float, height: float) -> List[Platform]:
        """
        Obtiene las plataformas en un área específica.
        
        Args:
            x, y: Posición del área
            width, height: Dimensiones del área
            
        Returns:
            Lista de plataformas en el área
        """
        
        area_rect = pygame.Rect(x, y, width, height)
        result = []
        
        for platform in self.platforms:
            if platform.can_collide() and platform.rect.colliderect(area_rect):
                result.append(platform)
        
        return result
    
    def get_collectibles_in_area(self, x: float, y: float, width: float, height: float) -> List[Collectible]:
        """
        Obtiene los coleccionables en un área específica.
        
        Args:
            x, y: Posición del área
            width, height: Dimensiones del área
            
        Returns:
            Lista de coleccionables en el área
        """
        
        area_rect = pygame.Rect(x, y, width, height)
        result = []
        
        for collectible in self.collectibles:
            if not collectible.collected and collectible.rect.colliderect(area_rect):
                result.append(collectible)
        
        return result
    
    def render(self, surface: pygame.Surface, camera_x: float = 0):
        """
        Renderiza el nivel.
        
        Args:
            surface: Superficie donde renderizar
            camera_x: Offset horizontal de la cámara
        """
        
        # Fondo
        surface.fill(self.background_color)
        
        # Renderizar plataformas
        for platform in self.platforms:
            platform.render(surface, camera_x)
        
        # Renderizar coleccionables
        for collectible in self.collectibles:
            collectible.render(surface, camera_x)
        
        # Debug: mostrar spawns de enemigos
        if Settings.DEBUG_DRAW_HITBOXES:
            for spawn in self.enemy_spawns:
                screen_x = spawn.x - camera_x
                screen_y = spawn.y
                
                if 0 <= screen_x <= Settings.GAME_WIDTH:
                    color = Settings.COLOR_RED if spawn.spawned else Settings.COLOR_GREEN
                    pygame.draw.circle(surface, color, (int(screen_x), int(screen_y)), 8)


class LevelLoader:
    """
    Cargador de niveles del juego.
    """
    
    def __init__(self):
        """Inicializa el cargador de niveles."""
        
        self.levels_path = Settings.LEVELS_PATH
        self.current_level: Optional[Level] = None
        self.available_levels = []
        
        print("Cargador de niveles inicializado")
    
    def scan_available_levels(self):
        """Escanea los niveles disponibles en el directorio de niveles."""
        
        self.available_levels.clear()
        
        if not os.path.exists(self.levels_path):
            print(f"Directorio de niveles no encontrado: {self.levels_path}")
            return
        
        for filename in os.listdir(self.levels_path):
            if filename.endswith('.json'):
                level_name = filename[:-5]  # Remover .json
                self.available_levels.append(level_name)
        
        print(f"Niveles disponibles encontrados: {self.available_levels}")
    
    def load_level(self, level_name: str) -> Optional[Level]:
        """
        Carga un nivel específico.
        
        Args:
            level_name: Nombre del nivel a cargar
            
        Returns:
            Instancia del nivel cargado o None si hay error
        """
        
        level_path = os.path.join(self.levels_path, f"{level_name}.json")
        
        if not os.path.exists(level_path):
            print(f"Archivo de nivel no encontrado: {level_path}")
            return None
        
        try:
            with open(level_path, 'r', encoding='utf-8') as f:
                level_data = json.load(f)
            
            level = Level(level_name)
            level.load_from_json(level_data)
            
            self.current_level = level
            return level
            
        except Exception as e:
            print(f"Error cargando nivel '{level_name}': {e}")
            return None
    
    def get_current_level(self) -> Optional[Level]:
        """
        Obtiene el nivel actualmente cargado.
        
        Returns:
            Nivel actual o None
        """
        
        return self.current_level
    
    def unload_current_level(self):
        """Descarga el nivel actual."""
        
        if self.current_level:
            print(f"Descargando nivel: {self.current_level.name}")
            self.current_level = None
    
    def reload_current_level(self) -> bool:
        """
        Recarga el nivel actual.
        
        Returns:
            True si se recargó exitosamente
        """
        
        if not self.current_level:
            return False
        
        level_name = self.current_level.name
        return self.load_level(level_name) is not None