"""
Sistema de Enemigos para Chen Toka - Sinaloa Dragon

Este módulo contiene todas las clases de enemigos con sus comportamientos
específicos, incluyendo IA, ataques y patrones de movimiento.
"""

import pygame
import math
import random
from typing import Tuple, Optional
from settings import Settings


class EnemyState:
    """Estados posibles de los enemigos."""
    IDLE = "idle"
    PATROLLING = "patrolling"
    CHASING = "chasing"
    ATTACKING = "attacking"
    HURT = "hurt"
    DEAD = "dead"
    STUNNED = "stunned"


class Enemy:
    """Clase base para todos los enemigos."""
    
    def __init__(self, x: float, y: float, enemy_type: str):
        """
        Inicializa un enemigo base.
        
        Args:
            x: Posición inicial X
            y: Posición inicial Y
            enemy_type: Tipo de enemigo
        """
        
        self.x = float(x)
        self.y = float(y)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        self.enemy_type = enemy_type
        self.state = EnemyState.IDLE
        self.state_timer = 0.0
        
        # Estadísticas básicas (se sobrescriben en subclases)
        self.hp = 20
        self.max_hp = 20
        self.speed = 50.0
        self.damage = 10
        
        # Hitbox
        self.width = 16
        self.height = 16
        
        # Comportamiento
        self.facing_right = True
        self.detection_range = 80.0
        self.attack_range = 24.0
        self.patrol_distance = 64.0
        self.patrol_center_x = x
        
        # Timers
        self.attack_cooldown = 0.0
        self.hurt_timer = 0.0
        self.stun_timer = 0.0
        
        # Animación
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.2
        
        # IA
        self.target_player = None
        self.last_known_player_x = 0
        
        print(f"Enemigo {enemy_type} creado en ({x}, {y})")
    
    def update(self, dt: float, player, level_data=None):
        """
        Actualiza el enemigo cada frame.
        
        Args:
            dt: Delta time en segundos
            player: Referencia al jugador
            level_data: Datos del nivel (opcional)
        """
        
        # Actualizar timers
        self._update_timers(dt)
        
        # Procesar IA si no está muerto o stunned
        if self.state not in [EnemyState.DEAD, EnemyState.STUNNED, EnemyState.HURT]:
            self._update_ai(dt, player)
        
        # Actualizar físicas
        self._update_physics(dt)
        
        # Actualizar animación
        self._update_animation(dt)
    
    def _update_timers(self, dt: float):
        """Actualiza todos los timers del enemigo."""
        
        self.state_timer += dt
        self.attack_cooldown -= dt
        self.hurt_timer -= dt
        self.stun_timer -= dt
        self.animation_timer += dt
        
        # Transiciones automáticas de estado
        if self.state == EnemyState.HURT and self.hurt_timer <= 0:
            self.state = EnemyState.IDLE
            self.state_timer = 0.0
        
        if self.state == EnemyState.STUNNED and self.stun_timer <= 0:
            self.state = EnemyState.IDLE
            self.state_timer = 0.0
    
    def _update_ai(self, dt: float, player):
        """
        Actualiza la IA del enemigo (implementación base).
        
        Args:
            dt: Delta time
            player: Referencia al jugador
        """
        
        if not player or not player.is_alive():
            return
        
        # Calcular distancia al jugador
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Determinar comportamiento según distancia
        if distance <= self.attack_range and self.attack_cooldown <= 0:
            self._start_attack()
        elif distance <= self.detection_range:
            self._start_chase(player)
        else:
            self._start_patrol()
    
    def _start_attack(self):
        """Inicia un ataque."""
        
        self.state = EnemyState.ATTACKING
        self.state_timer = 0.0
        self.velocity_x = 0  # Detenerse al atacar
    
    def _start_chase(self, player):
        """
        Inicia la persecución del jugador.
        
        Args:
            player: Referencia al jugador
        """
        
        self.state = EnemyState.CHASING
        self.target_player = player
        self.last_known_player_x = player.x
        
        # Mover hacia el jugador
        if player.x > self.x:
            self.velocity_x = self.speed
            self.facing_right = True
        else:
            self.velocity_x = -self.speed
            self.facing_right = False
    
    def _start_patrol(self):
        """Inicia el patrullaje."""
        
        self.state = EnemyState.PATROLLING
        
        # Patrullar alrededor del punto central
        distance_from_center = abs(self.x - self.patrol_center_x)
        
        if distance_from_center >= self.patrol_distance:
            # Regresar al centro
            if self.x > self.patrol_center_x:
                self.velocity_x = -self.speed * 0.5
                self.facing_right = False
            else:
                self.velocity_x = self.speed * 0.5
                self.facing_right = True
        else:
            # Moverse aleatoriamente
            if random.random() < 0.01:  # 1% chance por frame de cambiar dirección
                self.facing_right = not self.facing_right
            
            if self.facing_right:
                self.velocity_x = self.speed * 0.3
            else:
                self.velocity_x = -self.speed * 0.3
    
    def _update_physics(self, dt: float):
        """
        Actualiza las físicas básicas del enemigo.
        
        Args:
            dt: Delta time en segundos
        """
        
        # Aplicar gravedad
        self.velocity_y += Settings.GRAVITY * dt
        
        # Limitar velocidad de caída
        if self.velocity_y > Settings.MAX_FALL_SPEED:
            self.velocity_y = Settings.MAX_FALL_SPEED
        
        # Actualizar posición
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Colisión básica con el suelo
        ground_y = 156  # Altura del suelo (placeholder)
        if self.y + self.height >= ground_y:
            self.y = ground_y - self.height
            self.velocity_y = 0
    
    def _update_animation(self, dt: float):
        """Actualiza la animación del enemigo."""
        
        if self.animation_timer >= self.animation_speed:
            self.animation_frame += 1
            self.animation_timer = 0.0
            
            # Número de frames por estado
            frame_counts = {
                EnemyState.IDLE: 2,
                EnemyState.PATROLLING: 4,
                EnemyState.CHASING: 4,
                EnemyState.ATTACKING: 3,
                EnemyState.HURT: 1,
                EnemyState.DEAD: 1,
                EnemyState.STUNNED: 2
            }
            
            max_frames = frame_counts.get(self.state, 1)
            
            if self.animation_frame >= max_frames:
                if self.state in [EnemyState.IDLE, EnemyState.PATROLLING, EnemyState.CHASING, EnemyState.STUNNED]:
                    self.animation_frame = 0  # Loop
                else:
                    self.animation_frame = max_frames - 1  # Hold
    
    def take_damage(self, damage: int, force_x: float = 0, force_y: float = 0, stun_duration: float = 0):
        """
        El enemigo recibe daño.
        
        Args:
            damage: Cantidad de daño
            force_x: Fuerza horizontal del knockback
            force_y: Fuerza vertical del knockback
            stun_duration: Duración del stun en segundos
        """
        
        if self.state == EnemyState.DEAD:
            return
        
        # Aplicar daño
        self.hp -= damage
        print(f"Enemigo {self.enemy_type} recibe {damage} de daño. HP: {self.hp}/{self.max_hp}")
        
        # Aplicar knockback
        self.velocity_x += force_x
        self.velocity_y += force_y
        
        # Determinar nuevo estado
        if self.hp <= 0:
            self.state = EnemyState.DEAD
            self.velocity_x = 0
            print(f"Enemigo {self.enemy_type} eliminado!")
        elif stun_duration > 0:
            self.state = EnemyState.STUNNED
            self.stun_timer = stun_duration
        else:
            self.state = EnemyState.HURT
            self.hurt_timer = 0.3
        
        self.state_timer = 0.0
    
    def get_hitbox(self) -> pygame.Rect:
        """Obtiene el hitbox del enemigo."""
        
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_attack_hitbox(self) -> Optional[pygame.Rect]:
        """Obtiene el hitbox de ataque si está atacando."""
        
        if self.state != EnemyState.ATTACKING:
            return None
        
        # Hitbox básico de ataque
        attack_width = 20
        attack_height = 16
        
        if self.facing_right:
            attack_x = self.x + self.width
        else:
            attack_x = self.x - attack_width
        
        attack_y = self.y
        
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def is_alive(self) -> bool:
        """Verifica si el enemigo está vivo."""
        
        return self.hp > 0 and self.state != EnemyState.DEAD


class Maton(Enemy):
    """
    Matón - Enemigo lento y fuerte con ataques telegrafados.
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "maton")
        
        # Estadísticas específicas
        self.hp = Settings.MATON_HP
        self.max_hp = Settings.MATON_HP
        self.speed = Settings.MATON_SPEED
        self.damage = Settings.MATON_ATTACK_DAMAGE
        
        # Comportamiento específico
        self.attack_range = 30.0
        self.attack_windup_duration = Settings.MATON_ATTACK_WINDUP
        self.attack_windup_timer = 0.0
        self.is_winding_up = False
        
        # Hitbox más grande
        self.width = 20
        self.height = 24
    
    def _start_attack(self):
        """Inicia un ataque con windup."""
        
        if not self.is_winding_up:
            self.is_winding_up = True
            self.attack_windup_timer = self.attack_windup_duration
            print("Matón prepara ataque...")
        
        if self.attack_windup_timer <= 0:
            self.state = EnemyState.ATTACKING
            self.state_timer = 0.0
            self.attack_cooldown = 2.0  # Cooldown largo
            self.is_winding_up = False
            self.velocity_x = 0
            print("¡Matón ataca!")
    
    def _update_timers(self, dt: float):
        """Actualiza timers incluyendo el windup."""
        
        super()._update_timers(dt)
        
        if self.is_winding_up:
            self.attack_windup_timer -= dt
            if self.attack_windup_timer <= 0:
                self._start_attack()


class Chacal(Enemy):
    """
    Chacal - Lanzador de cuchillos con ataques a distancia.
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "chacal")
        
        # Estadísticas específicas
        self.hp = Settings.CHACAL_HP
        self.max_hp = Settings.CHACAL_HP
        self.speed = Settings.CHACAL_SPEED
        self.damage = Settings.CHACAL_KNIFE_DAMAGE
        
        # Comportamiento específico
        self.attack_range = 100.0  # Rango largo para lanzar cuchillos
        self.throw_interval = Settings.CHACAL_THROW_INTERVAL
        self.last_throw_time = 0.0
        
        # Lista de proyectiles lanzados
        self.knives = []
    
    def update(self, dt: float, player, level_data=None):
        """Actualiza el Chacal y sus proyectiles."""
        
        super().update(dt, player, level_data)
        
        # Actualizar cuchillos
        for knife in self.knives[:]:  # Copia para poder modificar durante iteración
            knife.update(dt)
            
            # Remover cuchillos que salieron de pantalla o expiraron
            if (knife.x < -20 or knife.x > Settings.GAME_WIDTH + 20 or 
                knife.y > Settings.GAME_HEIGHT + 20 or knife.lifetime <= 0):
                self.knives.remove(knife)
    
    def _start_attack(self):
        """Lanza un cuchillo."""
        
        if self.target_player:
            # Calcular dirección hacia el jugador
            dx = self.target_player.x - self.x
            dy = self.target_player.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                # Normalizar dirección
                dir_x = dx / distance
                dir_y = dy / distance
                
                # Crear cuchillo
                knife = ChacalKnife(self.x + self.width // 2, self.y + self.height // 2, 
                                  dir_x, dir_y, self.damage)
                self.knives.append(knife)
                
                self.attack_cooldown = self.throw_interval
                print("Chacal lanza cuchillo!")


class ChacalKnife:
    """Proyectil del Chacal."""
    
    def __init__(self, x: float, y: float, dir_x: float, dir_y: float, damage: int):
        self.x = float(x)
        self.y = float(y)
        self.velocity_x = dir_x * 200.0  # Velocidad del cuchillo
        self.velocity_y = dir_y * 200.0
        self.damage = damage
        self.lifetime = 3.0  # Tiempo de vida en segundos
        
        # Hitbox pequeña
        self.width = 4
        self.height = 4
    
    def update(self, dt: float):
        """Actualiza el proyectil."""
        
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.lifetime -= dt
    
    def get_hitbox(self) -> pygame.Rect:
        """Obtiene el hitbox del cuchillo."""
        
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Luchador(Enemy):
    """
    Luchador - Enemigo con ataques de agarre y movimientos especiales.
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "luchador")
        
        # Estadísticas específicas
        self.hp = Settings.LUCHADOR_HP
        self.max_hp = Settings.LUCHADOR_HP
        self.speed = Settings.LUCHADOR_SPEED
        self.damage = Settings.LUCHADOR_GRAB_DAMAGE
        
        # Comportamiento específico
        self.attack_range = 25.0
        self.lunge_distance = Settings.LUCHADOR_LUNGE_DISTANCE
        self.is_lunging = False
        self.lunge_timer = 0.0
        self.lunge_duration = 0.5
        
        # Hitbox más grande
        self.width = 18
        self.height = 26
    
    def _start_attack(self):
        """Inicia un lunge attack."""
        
        if not self.is_lunging and self.target_player:
            self.is_lunging = True
            self.lunge_timer = self.lunge_duration
            self.state = EnemyState.ATTACKING
            self.state_timer = 0.0
            
            # Calcular dirección del lunge
            if self.target_player.x > self.x:
                self.velocity_x = self.lunge_distance / self.lunge_duration
                self.facing_right = True
            else:
                self.velocity_x = -self.lunge_distance / self.lunge_duration
                self.facing_right = False
            
            self.attack_cooldown = 3.0  # Cooldown largo
            print("¡Luchador hace lunge attack!")
    
    def _update_timers(self, dt: float):
        """Actualiza timers incluyendo el lunge."""
        
        super()._update_timers(dt)
        
        if self.is_lunging:
            self.lunge_timer -= dt
            if self.lunge_timer <= 0:
                self.is_lunging = False
                self.velocity_x = 0


class Drone(Enemy):
    """
    Dron de Seguridad - Enemigo volador con patrón de patrulla aérea.
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "drone")
        
        # Estadísticas específicas
        self.hp = Settings.DRONE_HP
        self.max_hp = Settings.DRONE_HP
        self.speed = Settings.DRONE_SPEED
        self.damage = Settings.DRONE_LASER_DAMAGE
        
        # Comportamiento específico
        self.hover_height = y  # Altura de vuelo
        self.patrol_distance = Settings.DRONE_PATROL_DISTANCE
        self.detection_range = 60.0
        self.attack_range = 80.0
        
        # Vuelo
        self.can_fly = True
        self.hover_amplitude = 8.0  # Amplitud del movimiento de hover
        self.hover_frequency = 2.0  # Frecuencia del hover
        
        # Hitbox voladora
        self.width = 14
        self.height = 10
    
    def _update_physics(self, dt: float):
        """Física especial para vuelo."""
        
        # Los drones no son afectados por gravedad
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Hover effect
        hover_offset = math.sin(self.state_timer * self.hover_frequency) * self.hover_amplitude
        target_y = self.hover_height + hover_offset
        
        # Suave movimiento hacia la altura objetivo
        y_diff = target_y - self.y
        self.velocity_y = y_diff * 2.0  # Factor de corrección
    
    def _start_attack(self):
        """Dispara láser hacia el jugador."""
        
        self.state = EnemyState.ATTACKING
        self.state_timer = 0.0
        self.attack_cooldown = 1.5
        self.velocity_x = 0  # Detenerse para disparar
        
        print("Dron dispara láser!")
    
    def _start_patrol(self):
        """Patrulla aérea."""
        
        self.state = EnemyState.PATROLLING
        
        # Patrullar horizontalmente
        distance_from_center = abs(self.x - self.patrol_center_x)
        
        if distance_from_center >= self.patrol_distance:
            # Regresar al centro
            if self.x > self.patrol_center_x:
                self.velocity_x = -self.speed
                self.facing_right = False
            else:
                self.velocity_x = self.speed
                self.facing_right = True
        else:
            # Continuar en la dirección actual
            if self.facing_right:
                self.velocity_x = self.speed
            else:
                self.velocity_x = -self.speed