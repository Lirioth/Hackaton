"""
Componente del Jugador para Chen Toka - Sinaloa Dragon

Este módulo implementa toda la lógica del personaje jugador, incluyendo
movimiento, combate, habilidades especiales y mecánicas avanzadas.
"""

import pygame
import math
from typing import Tuple, Optional, Set
from settings import Settings


class PlayerState:
    """Estados posibles del jugador."""
    IDLE = "idle"
    RUNNING = "running"
    JUMPING = "jumping"
    FALLING = "falling"
    ROLLING = "rolling"
    ATTACKING = "attacking"
    HURT = "hurt"
    DEAD = "dead"


class Player:
    """
    Clase principal del jugador Chen Toka.
    """
    
    def __init__(self, x: float, y: float):
        """
        Inicializa el jugador.
        
        Args:
            x: Posición inicial X
            y: Posición inicial Y
        """
        
        # Posición y movimiento
        self.x = float(x)
        self.y = float(y)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.facing_right = True
        
        # Hitbox y renderizado
        self.width = 16
        self.height = 24
        self.render_offset_x = 0
        self.render_offset_y = 0
        
        # Estado del jugador
        self.state = PlayerState.IDLE
        self.previous_state = PlayerState.IDLE
        self.state_timer = 0.0
        
        # Estadísticas de salud y combate
        self.hp = Settings.PLAYER_MAX_HP
        self.max_hp = Settings.PLAYER_MAX_HP
        self.super_meter = 0
        self.combo_count = 0
        self.combo_timer = 0.0
        
        # Mecánicas de salto y movimiento
        self.on_ground = False
        self.can_double_jump = True
        self.has_double_jumped = False
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        
        # Mecánicas de combate
        self.attack_combo_stage = 0
        self.attack_timer = 0.0
        self.can_attack = True
        self.parry_timer = 0.0
        self.parry_window_active = False
        
        # Invencibilidad y efectos
        self.invulnerable = False
        self.invulnerability_timer = 0.0
        self.hit_stun_timer = 0.0
        
        # Roll/esquive
        self.roll_timer = 0.0
        self.roll_direction = 1
        
        # Habilidades desbloqueadas
        self.unlocked_skills: Set[str] = set()
        
        # Animación
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.1  # Tiempo por frame
        
        print(f"Jugador Chen Toka creado en ({x}, {y})")
    
    def update(self, dt: float, input_manager, level_data=None):
        """
        Actualiza el jugador cada frame.
        
        Args:
            dt: Delta time en segundos
            input_manager: Administrador de entrada
            level_data: Datos del nivel actual (opcional)
        """
        
        # Actualizar timers
        self._update_timers(dt)
        
        # Procesar input solo si no está en hit-stun
        if self.hit_stun_timer <= 0:
            self._process_input(input_manager, dt)
        
        # Actualizar físicas
        self._update_physics(dt)
        
        # Actualizar estado
        self._update_state(dt)
        
        # Actualizar animación
        self._update_animation(dt)
        
        # Aplicar límites del mundo
        self._apply_world_bounds()
        
        # Actualizar combo
        self._update_combo(dt)
    
    def _update_timers(self, dt: float):
        """Actualiza todos los timers del jugador."""
        
        self.state_timer += dt
        self.coyote_timer -= dt
        self.jump_buffer_timer -= dt
        self.attack_timer -= dt
        self.combo_timer -= dt
        self.parry_timer -= dt
        self.invulnerability_timer -= dt
        self.hit_stun_timer -= dt
        self.roll_timer -= dt
        self.animation_timer += dt
        
        # Actualizar estados booleanos basados en timers
        self.invulnerable = self.invulnerability_timer > 0
        self.parry_window_active = self.parry_timer > 0
        
        # Resetear ataque si terminó el timer
        if self.attack_timer <= 0 and self.state == PlayerState.ATTACKING:
            self.can_attack = True
            self.attack_combo_stage = 0
    
    def _process_input(self, input_manager, dt: float):
        """
        Procesa la entrada del usuario.
        
        Args:
            input_manager: Administrador de entrada
            dt: Delta time
        """
        
        # Obtener vector de movimiento
        move_x, move_y = input_manager.get_movement_vector()
        
        # Movimiento horizontal
        if abs(move_x) > 0.1:
            self._handle_horizontal_movement(move_x)
        else:
            self._apply_friction()
        
        # Salto
        if input_manager.is_just_pressed('jump') or input_manager.was_pressed_recently('jump'):
            self._handle_jump_input()
        
        # Ataques
        if input_manager.is_just_pressed('attack_light'):
            self._handle_light_attack()
        
        if input_manager.is_just_pressed('attack_heavy'):
            self._handle_heavy_attack()
        
        # Roll/esquive
        if input_manager.is_just_pressed('roll'):
            self._handle_roll()
        
        # Parry
        if input_manager.is_just_pressed('parry'):
            self._handle_parry()
        
        # Movimiento hacia abajo (para atravesar plataformas)
        if input_manager.is_pressed('move_down') and self.on_ground:
            self._handle_drop_down()
    
    def _handle_horizontal_movement(self, move_x: float):
        """
        Maneja el movimiento horizontal.
        
        Args:
            move_x: Input horizontal (-1 a 1)
        """
        
        # No moverse durante roll o ciertos estados
        if self.state == PlayerState.ROLLING or self.state == PlayerState.HURT:
            return
        
        # Actualizar dirección
        if move_x > 0:
            self.facing_right = True
        elif move_x < 0:
            self.facing_right = False
        
        # Aplicar aceleración
        target_velocity = move_x * Settings.PLAYER_SPEED
        acceleration = 800.0  # Aceleración horizontal
        
        if abs(target_velocity) > abs(self.velocity_x):
            # Acelerar hacia la velocidad objetivo
            if target_velocity > self.velocity_x:
                self.velocity_x = min(self.velocity_x + acceleration * (1/60), target_velocity)
            else:
                self.velocity_x = max(self.velocity_x - acceleration * (1/60), target_velocity)
        else:
            # Decelerar hacia la velocidad objetivo
            self.velocity_x = target_velocity
    
    def _apply_friction(self):
        """Aplica fricción al movimiento horizontal."""
        
        if self.state != PlayerState.ROLLING:
            friction = 600.0  # Fricción horizontal
            
            if self.velocity_x > 0:
                self.velocity_x = max(0, self.velocity_x - friction * (1/60))
            elif self.velocity_x < 0:
                self.velocity_x = min(0, self.velocity_x + friction * (1/60))
    
    def _handle_jump_input(self):
        """Maneja la entrada de salto."""
        
        # No saltar durante roll o hurt
        if self.state == PlayerState.ROLLING or self.state == PlayerState.HURT:
            return
        
        # Salto normal desde el suelo o coyote time
        if self.on_ground or self.coyote_timer > 0:
            self._perform_jump(Settings.PLAYER_JUMP_FORCE)
            self.can_double_jump = True
            self.has_double_jumped = False
            self.coyote_timer = 0
            
        # Doble salto
        elif self.can_double_jump and not self.has_double_jumped and "double_jump" in self.unlocked_skills:
            self._perform_jump(Settings.PLAYER_DOUBLE_JUMP_FORCE)
            self.has_double_jumped = True
            self.can_double_jump = False
        
        # Limpiar buffer de salto
        self.jump_buffer_timer = 0
    
    def _perform_jump(self, force: float):
        """
        Realiza un salto con la fuerza especificada.
        
        Args:
            force: Fuerza del salto en píxeles por segundo
        """
        
        self.velocity_y = -force
        self.on_ground = False
        self.state = PlayerState.JUMPING
        self.state_timer = 0.0
        
        # Reproducir sonido de salto (placeholder)
        print("¡Salto!")
    
    def _handle_light_attack(self):
        """Maneja el ataque ligero."""
        
        if not self.can_attack or self.state == PlayerState.ROLLING or self.state == PlayerState.HURT:
            return
        
        # Iniciar o continuar combo
        if self.attack_combo_stage < Settings.MAX_COMBO_COUNT:
            self.attack_combo_stage += 1
            self.attack_timer = 0.3  # Duración de la animación de ataque
            self.can_attack = False
            self.state = PlayerState.ATTACKING
            self.state_timer = 0.0
            
            # Incrementar combo
            if self.combo_timer > 0:
                self.combo_count += 1
            else:
                self.combo_count = 1
            
            self.combo_timer = Settings.COMBO_WINDOW
            
            print(f"Ataque ligero {self.attack_combo_stage} - Combo: {self.combo_count}")
    
    def _handle_heavy_attack(self):
        """Maneja el ataque pesado."""
        
        if not self.can_attack or self.state == PlayerState.ROLLING or self.state == PlayerState.HURT:
            return
        
        # Ataque pesado consume super meter
        if self.super_meter > 0:
            self.super_meter -= 1
            self.attack_timer = 0.5  # Duración más larga
            self.can_attack = False
            self.state = PlayerState.ATTACKING
            self.state_timer = 0.0
            
            # Mayor daño y combo
            self.combo_count += 2
            self.combo_timer = Settings.COMBO_WINDOW
            
            print(f"Ataque pesado - Super: {self.super_meter} - Combo: {self.combo_count}")
    
    def _handle_roll(self):
        """Maneja el roll/esquive."""
        
        if self.state == PlayerState.ROLLING or self.state == PlayerState.HURT:
            return
        
        # Verificar si tiene la habilidad
        if "dash" not in self.unlocked_skills:
            return
        
        # Iniciar roll
        self.state = PlayerState.ROLLING
        self.state_timer = 0.0
        self.roll_timer = Settings.PLAYER_ROLL_DURATION
        self.roll_direction = 1 if self.facing_right else -1
        
        # Aplicar velocidad de roll
        self.velocity_x = self.roll_direction * Settings.PLAYER_ROLL_SPEED
        
        # Activar invencibilidad
        self.invulnerability_timer = Settings.PLAYER_ROLL_DURATION
        
        print("¡Roll!")
    
    def _handle_parry(self):
        """Maneja el parry."""
        
        if self.state == PlayerState.ROLLING or self.state == PlayerState.HURT:
            return
        
        # Activar ventana de parry
        self.parry_timer = Settings.PARRY_WINDOW
        self.parry_window_active = True
        
        print("Intentando parry...")
    
    def _handle_drop_down(self):
        """Maneja el atravesar plataformas hacia abajo."""
        
        if self.on_ground:
            # Aquí se implementaría la lógica para atravesar plataformas
            # Por ahora, simplemente aplicar un pequeño impulso hacia abajo
            self.velocity_y += 50
            self.on_ground = False
            print("Atravesando plataforma")
    
    def _update_physics(self, dt: float):
        """
        Actualiza las físicas del jugador.
        
        Args:
            dt: Delta time en segundos
        """
        
        # Aplicar gravedad si no está en el suelo
        if not self.on_ground:
            self.velocity_y += Settings.GRAVITY * dt
            
            # Limitar velocidad de caída
            if self.velocity_y > Settings.MAX_FALL_SPEED:
                self.velocity_y = Settings.MAX_FALL_SPEED
        
        # Actualizar posición
        old_x = self.x
        old_y = self.y
        
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Colisiones básicas con el "suelo" (placeholder)
        ground_y = 156  # Altura aproximada del suelo en la pantalla
        
        if self.y + self.height >= ground_y:
            self.y = ground_y - self.height
            self.velocity_y = 0
            
            if not self.on_ground:
                # Aterrizar
                self.on_ground = True
                self.can_double_jump = True
                self.has_double_jumped = False
                print("Aterrizaje")
        else:
            # Activar coyote time al salir del suelo
            if self.on_ground:
                self.coyote_timer = Settings.COYOTE_TIME
            
            self.on_ground = False
    
    def _update_state(self, dt: float):
        """
        Actualiza el estado del jugador.
        
        Args:
            dt: Delta time en segundos
        """
        
        self.previous_state = self.state
        
        # Transiciones de estado
        if self.state == PlayerState.ROLLING:
            if self.roll_timer <= 0:
                self._transition_to_idle_or_movement()
        
        elif self.state == PlayerState.ATTACKING:
            if self.attack_timer <= 0:
                self._transition_to_idle_or_movement()
        
        elif self.state == PlayerState.HURT:
            if self.hit_stun_timer <= 0:
                self._transition_to_idle_or_movement()
        
        elif self.state == PlayerState.JUMPING:
            if self.velocity_y > 0:
                self.state = PlayerState.FALLING
        
        elif self.state == PlayerState.FALLING:
            if self.on_ground:
                self._transition_to_idle_or_movement()
        
        elif self.state in [PlayerState.IDLE, PlayerState.RUNNING]:
            if not self.on_ground:
                if self.velocity_y < 0:
                    self.state = PlayerState.JUMPING
                else:
                    self.state = PlayerState.FALLING
            elif abs(self.velocity_x) > 10:
                self.state = PlayerState.RUNNING
            else:
                self.state = PlayerState.IDLE
    
    def _transition_to_idle_or_movement(self):
        """Transiciona a idle o running según la velocidad."""
        
        if abs(self.velocity_x) > 10:
            self.state = PlayerState.RUNNING
        else:
            self.state = PlayerState.IDLE
        
        self.state_timer = 0.0
    
    def _update_animation(self, dt: float):
        """
        Actualiza la animación del jugador.
        
        Args:
            dt: Delta time en segundos
        """
        
        # Actualizar frame de animación
        if self.animation_timer >= self.animation_speed:
            self.animation_frame += 1
            self.animation_timer = 0.0
            
            # Determinar número de frames según el estado
            frame_counts = {
                PlayerState.IDLE: 4,
                PlayerState.RUNNING: 6,
                PlayerState.JUMPING: 1,
                PlayerState.FALLING: 1,
                PlayerState.ROLLING: 4,
                PlayerState.ATTACKING: 3,
                PlayerState.HURT: 2,
                PlayerState.DEAD: 1
            }
            
            max_frames = frame_counts.get(self.state, 1)
            
            if self.animation_frame >= max_frames:
                if self.state in [PlayerState.IDLE, PlayerState.RUNNING, PlayerState.ROLLING]:
                    self.animation_frame = 0  # Loop
                else:
                    self.animation_frame = max_frames - 1  # Hold last frame
    
    def _update_combo(self, dt: float):
        """Actualiza el sistema de combo."""
        
        if self.combo_timer <= 0 and self.combo_count > 0:
            # Combo expirado
            if self.combo_count >= 10:
                # Combo grande, ganar super meter
                self.super_meter = min(self.super_meter + 1, Settings.SUPER_METER_MAX)
                print(f"¡Combo de {self.combo_count}! +1 Super meter")
            
            self.combo_count = 0
    
    def _apply_world_bounds(self):
        """Aplica límites del mundo al jugador."""
        
        # Límites horizontales básicos
        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
        elif self.x + self.width > Settings.GAME_WIDTH:
            self.x = Settings.GAME_WIDTH - self.width
            self.velocity_x = 0
        
        # Si cae fuera del mundo, recibir daño
        if self.y > Settings.GAME_HEIGHT + 100:
            self.take_damage(10, force_x=0, force_y=0)
            self.y = 100  # Resetear posición
            self.velocity_y = 0
    
    def take_damage(self, damage: int, force_x: float = 0, force_y: float = 0):
        """
        El jugador recibe daño.
        
        Args:
            damage: Cantidad de daño
            force_x: Fuerza horizontal del knockback
            force_y: Fuerza vertical del knockback
        """
        
        # No recibir daño si es invulnerable
        if self.invulnerable:
            return
        
        # Verificar parry exitoso
        if self.parry_window_active:
            print("¡PARRY EXITOSO!")
            self.parry_timer = 0
            self.super_meter = min(self.super_meter + 1, Settings.SUPER_METER_MAX)
            # Trigger hit-stop aquí si hubiera referencia al juego
            return
        
        # Aplicar daño
        self.hp -= damage
        print(f"Chen Toka recibe {damage} de daño. HP: {self.hp}/{self.max_hp}")
        
        # Aplicar knockback
        self.velocity_x += force_x
        self.velocity_y += force_y
        
        # Activar invencibilidad y hit-stun
        self.invulnerability_timer = Settings.HURT_IFRAMES_DURATION
        self.hit_stun_timer = 0.3
        
        # Cambiar estado
        if self.hp <= 0:
            self.state = PlayerState.DEAD
            self.velocity_x = 0
            print("Chen Toka ha sido derrotado!")
        else:
            self.state = PlayerState.HURT
        
        self.state_timer = 0.0
        
        # Resetear combo
        self.combo_count = 0
        self.combo_timer = 0
    
    def heal(self, amount: int):
        """
        Cura al jugador.
        
        Args:
            amount: Cantidad de curación
        """
        
        old_hp = self.hp
        self.hp = min(self.hp + amount, self.max_hp)
        healed = self.hp - old_hp
        
        if healed > 0:
            print(f"Chen Toka se cura {healed} HP. HP: {self.hp}/{self.max_hp}")
    
    def add_super(self, amount: int = 1):
        """
        Añade super meter.
        
        Args:
            amount: Cantidad de super meter a añadir
        """
        
        old_super = self.super_meter
        self.super_meter = min(self.super_meter + amount, Settings.SUPER_METER_MAX)
        added = self.super_meter - old_super
        
        if added > 0:
            print(f"Chen Toka gana {added} super meter. Super: {self.super_meter}/{Settings.SUPER_METER_MAX}")
    
    def unlock_skill(self, skill_name: str):
        """
        Desbloquea una habilidad.
        
        Args:
            skill_name: Nombre de la habilidad ("dash", "double_jump", "aerial_recover", "super")
        """
        
        if skill_name not in self.unlocked_skills:
            self.unlocked_skills.add(skill_name)
            print(f"¡Habilidad desbloqueada: {skill_name}!")
    
    def get_hitbox(self) -> pygame.Rect:
        """
        Obtiene el hitbox del jugador.
        
        Returns:
            Rect con la hitbox del jugador
        """
        
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_attack_hitbox(self) -> Optional[pygame.Rect]:
        """
        Obtiene el hitbox de ataque si está atacando.
        
        Returns:
            Rect con la hitbox de ataque o None si no está atacando
        """
        
        if self.state != PlayerState.ATTACKING:
            return None
        
        # Crear hitbox de ataque en frente del jugador
        attack_width = 20
        attack_height = 16
        
        if self.facing_right:
            attack_x = self.x + self.width
        else:
            attack_x = self.x - attack_width
        
        attack_y = self.y + 4
        
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def get_render_position(self) -> Tuple[int, int]:
        """
        Obtiene la posición de renderizado con offset.
        
        Returns:
            Tupla (x, y) para renderizado
        """
        
        # Aplicar shake de invencibilidad
        offset_x = self.render_offset_x
        offset_y = self.render_offset_y
        
        if self.invulnerable and int(self.invulnerability_timer * 20) % 2:
            # Parpadeo durante invencibilidad
            offset_x += 1
        
        return (int(self.x + offset_x), int(self.y + offset_y))
    
    def is_alive(self) -> bool:
        """
        Verifica si el jugador está vivo.
        
        Returns:
            True si el jugador está vivo
        """
        
        return self.hp > 0 and self.state != PlayerState.DEAD