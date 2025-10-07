"""
Sistema de Combate para Chen Toka - Sinaloa Dragon

Este módulo maneja toda la lógica de combate, incluyendo hitboxes,
combos, efectos especiales y damage calculations.
"""

import pygame
import math
from typing import Dict, List, Tuple, Optional, Any
from settings import Settings


class AttackType:
    """Tipos de ataque disponibles."""
    LIGHT = "light"
    HEAVY = "heavy"
    SPECIAL = "special"
    PROJECTILE = "projectile"
    GRAB = "grab"


class CombatEffect:
    """Efectos especiales de combate."""
    NONE = "none"
    KNOCKDOWN = "knockdown"
    STUN = "stun"
    LAUNCHER = "launcher"
    WALL_BOUNCE = "wall_bounce"
    GROUND_BOUNCE = "ground_bounce"


class AttackData:
    """
    Datos de un ataque específico.
    """
    
    def __init__(self, attack_type: str, damage: int, hitbox_size: Tuple[int, int],
                 startup_frames: int, active_frames: int, recovery_frames: int,
                 knockback: Tuple[float, float] = (0, 0), effect: str = CombatEffect.NONE):
        """
        Inicializa los datos de un ataque.
        
        Args:
            attack_type: Tipo de ataque
            damage: Daño base del ataque
            hitbox_size: Tamaño del hitbox (width, height)
            startup_frames: Frames antes de que el ataque sea activo
            active_frames: Frames durante los cuales el ataque puede golpear
            recovery_frames: Frames de recuperación después del ataque
            knockback: Fuerza de knockback (x, y)
            effect: Efecto especial del ataque
        """
        
        self.type = attack_type
        self.damage = damage
        self.hitbox_size = hitbox_size
        self.startup_frames = startup_frames
        self.active_frames = active_frames
        self.recovery_frames = recovery_frames
        self.knockback = knockback
        self.effect = effect
        
        # Frames totales del ataque
        self.total_frames = startup_frames + active_frames + recovery_frames
        
        # Propiedades adicionales
        self.super_cost = 0
        self.builds_meter = 0
        self.can_cancel = False
        self.air_ok = False


class CombatComponent:
    """
    Componente de combate que puede ser attachado a cualquier entidad.
    """
    
    def __init__(self, entity_id: str):
        """
        Inicializa el componente de combate.
        
        Args:
            entity_id: ID único de la entidad
        """
        
        self.entity_id = entity_id
        
        # Estado de combate
        self.is_attacking = False
        self.current_attack = None
        self.attack_frame = 0
        self.attack_timer = 0.0
        
        # Hitboxes activos
        self.active_hitboxes: List[Dict[str, Any]] = []
        self.hurtbox: Optional[pygame.Rect] = None
        
        # Propiedades de daño
        self.damage_multiplier = 1.0
        self.knockback_multiplier = 1.0
        self.invulnerable = False
        self.super_armor = False  # No flinch, pero recibe daño
        
        # Combo system
        self.combo_count = 0
        self.combo_damage = 0
        self.hit_confirm = False
        
        # Efectos activos
        self.active_effects: List[Dict[str, Any]] = []
        
        # Callbacks
        self.on_hit_callback = None
        self.on_deal_damage_callback = None
    
    def start_attack(self, attack_data: AttackData, attacker_rect: pygame.Rect, facing_right: bool):
        """
        Inicia un ataque.
        
        Args:
            attack_data: Datos del ataque a realizar
            attacker_rect: Rectángulo de la entidad atacante
            facing_right: Dirección que mira el atacante
        """
        
        if self.is_attacking:
            return False  # Ya está atacando
        
        self.is_attacking = True
        self.current_attack = attack_data
        self.attack_frame = 0
        self.attack_timer = 0.0
        self.hit_confirm = False
        
        print(f"Entidad {self.entity_id} inicia ataque {attack_data.type}")
        return True
    
    def update(self, dt: float, entity_rect: pygame.Rect, facing_right: bool):
        """
        Actualiza el componente de combate.
        
        Args:
            dt: Delta time en segundos
            entity_rect: Rectángulo de la entidad
            facing_right: Dirección que mira la entidad
        """
        
        # Actualizar ataque activo
        if self.is_attacking and self.current_attack:
            self._update_attack(dt, entity_rect, facing_right)
        
        # Actualizar efectos activos
        self._update_effects(dt)
        
        # Limpiar hitboxes expirados
        self._cleanup_hitboxes()
    
    def _update_attack(self, dt: float, entity_rect: pygame.Rect, facing_right: bool):
        """
        Actualiza el ataque actual.
        
        Args:
            dt: Delta time
            entity_rect: Rectángulo de la entidad
            facing_right: Dirección de la entidad
        """
        
        self.attack_timer += dt
        target_fps = Settings.TARGET_FPS
        frame_duration = 1.0 / target_fps
        
        # Calcular frame actual
        self.attack_frame = int(self.attack_timer / frame_duration)
        
        # Verificar si el ataque terminó
        if self.attack_frame >= self.current_attack.total_frames:
            self._end_attack()
            return
        
        # Verificar si estamos en frames activos
        startup = self.current_attack.startup_frames
        active_end = startup + self.current_attack.active_frames
        
        if startup <= self.attack_frame < active_end:
            # Crear hitbox si no existe
            if not self.active_hitboxes:
                self._create_attack_hitbox(entity_rect, facing_right)
        else:
            # Limpiar hitboxes si salimos de frames activos
            self.active_hitboxes.clear()
    
    def _create_attack_hitbox(self, entity_rect: pygame.Rect, facing_right: bool):
        """
        Crea el hitbox del ataque actual.
        
        Args:
            entity_rect: Rectángulo de la entidad
            facing_right: Dirección de la entidad
        """
        
        if not self.current_attack:
            return
        
        hitbox_width, hitbox_height = self.current_attack.hitbox_size
        
        # Posicionar hitbox según la dirección
        if facing_right:
            hitbox_x = entity_rect.right
        else:
            hitbox_x = entity_rect.left - hitbox_width
        
        hitbox_y = entity_rect.y + (entity_rect.height - hitbox_height) // 2
        
        hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)
        
        # Crear datos del hitbox
        hitbox_data = {
            'rect': hitbox,
            'damage': int(self.current_attack.damage * self.damage_multiplier),
            'knockback': (
                self.current_attack.knockback[0] * self.knockback_multiplier,
                self.current_attack.knockback[1] * self.knockback_multiplier
            ),
            'effect': self.current_attack.effect,
            'attacker_id': self.entity_id,
            'attack_type': self.current_attack.type,
            'frame_created': self.attack_frame
        }
        
        self.active_hitboxes.append(hitbox_data)
    
    def _end_attack(self):
        """Termina el ataque actual."""
        
        self.is_attacking = False
        self.current_attack = None
        self.attack_frame = 0
        self.attack_timer = 0.0
        self.active_hitboxes.clear()
        
        print(f"Entidad {self.entity_id} termina ataque")
    
    def _update_effects(self, dt: float):
        """
        Actualiza efectos activos.
        
        Args:
            dt: Delta time
        """
        
        # Actualizar duración de efectos
        for effect in self.active_effects[:]:
            effect['duration'] -= dt
            
            if effect['duration'] <= 0:
                self._remove_effect(effect)
    
    def _remove_effect(self, effect: Dict[str, Any]):
        """
        Remueve un efecto activo.
        
        Args:
            effect: Efecto a remover
        """
        
        if effect in self.active_effects:
            self.active_effects.remove(effect)
            print(f"Efecto {effect['type']} removido de {self.entity_id}")
    
    def _cleanup_hitboxes(self):
        """Limpia hitboxes que ya no son válidos."""
        
        if not self.is_attacking:
            self.active_hitboxes.clear()
    
    def take_damage(self, damage: int, knockback: Tuple[float, float], 
                   attacker_id: str, attack_type: str, effect: str = CombatEffect.NONE) -> bool:
        """
        Procesa daño recibido.
        
        Args:
            damage: Cantidad de daño
            knockback: Fuerza de knockback (x, y)
            attacker_id: ID del atacante
            attack_type: Tipo de ataque
            effect: Efecto especial
            
        Returns:
            True si el daño fue aplicado, False si fue bloqueado/evitado
        """
        
        # Verificar invulnerabilidad
        if self.invulnerable:
            print(f"Entidad {self.entity_id} evita daño (invulnerable)")
            return False
        
        # Aplicar daño
        final_damage = damage
        
        # Super armor no previene daño, solo flinch
        if self.super_armor:
            knockback = (0, 0)  # Cancelar knockback
            print(f"Entidad {self.entity_id} tiene super armor")
        
        # Actualizar combo si es del mismo atacante
        if hasattr(self, 'last_attacker') and self.last_attacker == attacker_id:
            self.combo_count += 1
            self.combo_damage += final_damage
        else:
            self.combo_count = 1
            self.combo_damage = final_damage
            self.last_attacker = attacker_id
        
        # Aplicar efecto especial
        if effect != CombatEffect.NONE:
            self._apply_effect(effect, 1.0, attacker_id)
        
        # Callback de daño recibido
        if self.on_hit_callback:
            try:
                self.on_hit_callback(final_damage, knockback, attacker_id, attack_type)
            except Exception as e:
                print(f"Error en callback de hit: {e}")
        
        print(f"Entidad {self.entity_id} recibe {final_damage} de daño de {attacker_id}")
        print(f"Combo: {self.combo_count} hits, {self.combo_damage} daño total")
        
        return True
    
    def _apply_effect(self, effect_type: str, duration: float, source_id: str):
        """
        Aplica un efecto especial.
        
        Args:
            effect_type: Tipo de efecto
            duration: Duración en segundos
            source_id: ID de la fuente del efecto
        """
        
        effect_data = {
            'type': effect_type,
            'duration': duration,
            'source': source_id
        }
        
        # Verificar si ya tiene este efecto
        for existing_effect in self.active_effects:
            if existing_effect['type'] == effect_type:
                # Renovar duración del efecto existente
                existing_effect['duration'] = max(existing_effect['duration'], duration)
                return
        
        # Añadir nuevo efecto
        self.active_effects.append(effect_data)
        print(f"Efecto {effect_type} aplicado a {self.entity_id} por {duration}s")
    
    def has_effect(self, effect_type: str) -> bool:
        """
        Verifica si tiene un efecto activo.
        
        Args:
            effect_type: Tipo de efecto a verificar
            
        Returns:
            True si tiene el efecto activo
        """
        
        return any(effect['type'] == effect_type for effect in self.active_effects)
    
    def set_invulnerable(self, duration: float):
        """
        Activa invulnerabilidad temporal.
        
        Args:
            duration: Duración en segundos
        """
        
        self.invulnerable = True
        self._apply_effect("invulnerability", duration, self.entity_id)
    
    def set_super_armor(self, duration: float):
        """
        Activa super armor temporal.
        
        Args:
            duration: Duración en segundos
        """
        
        self.super_armor = True
        self._apply_effect("super_armor", duration, self.entity_id)
    
    def get_active_hitboxes(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los hitboxes activos.
        
        Returns:
            Lista de datos de hitboxes activos
        """
        
        return self.active_hitboxes.copy()
    
    def set_hurtbox(self, rect: pygame.Rect):
        """
        Establece el hurtbox de la entidad.
        
        Args:
            rect: Rectángulo del hurtbox
        """
        
        self.hurtbox = rect
    
    def can_attack(self) -> bool:
        """
        Verifica si puede atacar actualmente.
        
        Returns:
            True si puede atacar
        """
        
        return not self.is_attacking and not self.has_effect(CombatEffect.STUN)
    
    def cancel_attack(self):
        """Cancela el ataque actual si es posible."""
        
        if self.is_attacking and self.current_attack and self.current_attack.can_cancel:
            self._end_attack()
            print(f"Ataque de {self.entity_id} cancelado")
            return True
        
        return False
    
    def reset_combo(self):
        """Resetea el contador de combo."""
        
        self.combo_count = 0
        self.combo_damage = 0
        if hasattr(self, 'last_attacker'):
            delattr(self, 'last_attacker')


class CombatManager:
    """
    Administrador global del sistema de combate.
    """
    
    def __init__(self):
        """Inicializa el administrador de combate."""
        
        # Entidades registradas en combate
        self.combat_entities: Dict[str, CombatComponent] = {}
        
        # Datos de ataques predefinidos
        self.attack_database = self._create_attack_database()
        
        # Efectos visuales activos
        self.visual_effects: List[Dict[str, Any]] = []
        
        print("Administrador de combate inicializado")
    
    def _create_attack_database(self) -> Dict[str, AttackData]:
        """
        Crea la base de datos de ataques predefinidos.
        
        Returns:
            Diccionario con datos de ataques
        """
        
        attacks = {}
        
        # Ataques del jugador
        attacks['player_light_1'] = AttackData(
            AttackType.LIGHT, 8, (24, 16), 4, 6, 8, (50, -20)
        )
        attacks['player_light_2'] = AttackData(
            AttackType.LIGHT, 10, (28, 18), 3, 8, 6, (60, -15)
        )
        attacks['player_light_3'] = AttackData(
            AttackType.LIGHT, 12, (32, 20), 5, 10, 12, (80, -40), CombatEffect.LAUNCHER
        )
        attacks['player_heavy'] = AttackData(
            AttackType.HEAVY, 20, (36, 24), 8, 12, 15, (120, -60), CombatEffect.KNOCKDOWN
        )
        
        # Ataques de enemigos
        attacks['maton_punch'] = AttackData(
            AttackType.HEAVY, Settings.MATON_ATTACK_DAMAGE, (30, 20), 15, 8, 20, (100, -30)
        )
        attacks['chacal_knife'] = AttackData(
            AttackType.PROJECTILE, Settings.CHACAL_KNIFE_DAMAGE, (6, 6), 2, 60, 5, (40, -10)
        )
        attacks['luchador_grab'] = AttackData(
            AttackType.GRAB, Settings.LUCHADOR_GRAB_DAMAGE, (24, 28), 6, 10, 12, (150, -50), CombatEffect.STUN
        )
        attacks['drone_laser'] = AttackData(
            AttackType.PROJECTILE, Settings.DRONE_LASER_DAMAGE, (4, 4), 3, 30, 8, (30, 0)
        )
        
        return attacks
    
    def register_entity(self, entity_id: str) -> CombatComponent:
        """
        Registra una entidad en el sistema de combate.
        
        Args:
            entity_id: ID único de la entidad
            
        Returns:
            Componente de combate creado
        """
        
        if entity_id in self.combat_entities:
            return self.combat_entities[entity_id]
        
        combat_component = CombatComponent(entity_id)
        self.combat_entities[entity_id] = combat_component
        
        print(f"Entidad {entity_id} registrada en combate")
        return combat_component
    
    def unregister_entity(self, entity_id: str):
        """
        Desregistra una entidad del sistema de combate.
        
        Args:
            entity_id: ID de la entidad a desregistrar
        """
        
        if entity_id in self.combat_entities:
            del self.combat_entities[entity_id]
            print(f"Entidad {entity_id} desregistrada del combate")
    
    def update(self, dt: float) -> List[Dict[str, Any]]:
        """
        Actualiza el sistema de combate global.
        
        Args:
            dt: Delta time en segundos
            
        Returns:
            Lista de eventos de hit que ocurrieron
        """
        
        hit_events = []
        
        # Obtener todos los hitboxes y hurtboxes activos
        active_hitboxes = []
        active_hurtboxes = []
        
        for entity_id, combat_comp in self.combat_entities.items():
            # Recopilar hitboxes
            for hitbox_data in combat_comp.get_active_hitboxes():
                active_hitboxes.append(hitbox_data)
            
            # Recopilar hurtboxes
            if combat_comp.hurtbox:
                hurtbox_data = {
                    'rect': combat_comp.hurtbox,
                    'entity_id': entity_id,
                    'component': combat_comp
                }
                active_hurtboxes.append(hurtbox_data)
        
        # Detectar colisiones entre hitboxes y hurtboxes
        for hitbox_data in active_hitboxes:
            for hurtbox_data in active_hurtboxes:
                # No atacarse a sí mismo
                if hitbox_data['attacker_id'] == hurtbox_data['entity_id']:
                    continue
                
                # Verificar colisión
                if hitbox_data['rect'].colliderect(hurtbox_data['rect']):
                    # Procesar hit
                    defender_comp = hurtbox_data['component']
                    
                    success = defender_comp.take_damage(
                        hitbox_data['damage'],
                        hitbox_data['knockback'],
                        hitbox_data['attacker_id'],
                        hitbox_data['attack_type'],
                        hitbox_data['effect']
                    )
                    
                    if success:
                        # Crear evento de hit
                        hit_event = {
                            'attacker_id': hitbox_data['attacker_id'],
                            'defender_id': hurtbox_data['entity_id'],
                            'damage': hitbox_data['damage'],
                            'knockback': hitbox_data['knockback'],
                            'effect': hitbox_data['effect'],
                            'hit_point': (
                                (hitbox_data['rect'].centerx + hurtbox_data['rect'].centerx) // 2,
                                (hitbox_data['rect'].centery + hurtbox_data['rect'].centery) // 2
                            )
                        }
                        
                        hit_events.append(hit_event)
                        
                        # Marcar hit confirm para el atacante
                        if hitbox_data['attacker_id'] in self.combat_entities:
                            attacker_comp = self.combat_entities[hitbox_data['attacker_id']]
                            attacker_comp.hit_confirm = True
        
        # Actualizar efectos visuales
        self._update_visual_effects(dt)
        
        return hit_events
    
    def _update_visual_effects(self, dt: float):
        """
        Actualiza efectos visuales de combate.
        
        Args:
            dt: Delta time
        """
        
        # Actualizar y limpiar efectos expirados
        for effect in self.visual_effects[:]:
            effect['duration'] -= dt
            
            if effect['duration'] <= 0:
                self.visual_effects.remove(effect)
    
    def create_attack(self, entity_id: str, attack_name: str, entity_rect: pygame.Rect, facing_right: bool) -> bool:
        """
        Crea un ataque para una entidad.
        
        Args:
            entity_id: ID de la entidad atacante
            attack_name: Nombre del ataque en la base de datos
            entity_rect: Rectángulo de la entidad
            facing_right: Dirección de la entidad
            
        Returns:
            True si el ataque fue creado exitosamente
        """
        
        if entity_id not in self.combat_entities:
            return False
        
        if attack_name not in self.attack_database:
            print(f"Ataque {attack_name} no encontrado en la base de datos")
            return False
        
        combat_comp = self.combat_entities[entity_id]
        attack_data = self.attack_database[attack_name]
        
        return combat_comp.start_attack(attack_data, entity_rect, facing_right)
    
    def add_visual_effect(self, effect_type: str, position: Tuple[int, int], duration: float):
        """
        Añade un efecto visual.
        
        Args:
            effect_type: Tipo de efecto visual
            position: Posición del efecto (x, y)
            duration: Duración en segundos
        """
        
        effect = {
            'type': effect_type,
            'position': position,
            'duration': duration,
            'start_time': duration
        }
        
        self.visual_effects.append(effect)
    
    def get_visual_effects(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los efectos visuales activos.
        
        Returns:
            Lista de efectos visuales
        """
        
        return self.visual_effects.copy()
    
    def clear_all(self):
        """Limpia todo el estado del combate."""
        
        self.combat_entities.clear()
        self.visual_effects.clear()
        print("Sistema de combate limpiado")