"""
Sistema de IA para Chen Toka - Sinaloa Dragon

Este módulo contiene las máquinas de estado finito para el comportamiento
de los enemigos y NPCs del juego.
"""

import math
import random
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from settings import Settings


class AIState(Enum):
    """Estados básicos de IA."""
    IDLE = "idle"
    PATROL = "patrol"
    ALERT = "alert"
    CHASE = "chase"
    ATTACK = "attack"
    FLEE = "flee"
    STUNNED = "stunned"
    DEAD = "dead"


class AICondition:
    """Condiciones para transiciones de estado."""
    
    @staticmethod
    def player_in_range(ai_entity, player, range_distance: float) -> bool:
        """Verifica si el jugador está dentro del rango."""
        if not player:
            return False
        
        dx = player.x - ai_entity.x
        dy = player.y - ai_entity.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        return distance <= range_distance
    
    @staticmethod
    def player_visible(ai_entity, player, physics_world=None) -> bool:
        """Verifica si el jugador es visible (line of sight)."""
        if not player:
            return False
        
        # Verificación básica de distancia
        if not AICondition.player_in_range(ai_entity, player, ai_entity.detection_range):
            return False
        
        # Si hay mundo físico, verificar raycast
        if physics_world:
            start_pos = (ai_entity.x + ai_entity.width // 2, ai_entity.y + ai_entity.height // 2)
            end_pos = (player.x + player.width // 2, player.y + player.height // 2)
            
            collision_point = physics_world.raycast(start_pos, end_pos)
            return collision_point is None  # No hay obstáculos
        
        return True  # Sin verificación de obstáculos
    
    @staticmethod
    def health_low(ai_entity, threshold: float = 0.3) -> bool:
        """Verifica si la salud está baja."""
        if not hasattr(ai_entity, 'hp') or not hasattr(ai_entity, 'max_hp'):
            return False
        
        return (ai_entity.hp / ai_entity.max_hp) <= threshold
    
    @staticmethod
    def timer_expired(ai_entity, timer_name: str) -> bool:
        """Verifica si un timer específico ha expirado."""
        timer_value = getattr(ai_entity, timer_name, 0)
        return timer_value <= 0
    
    @staticmethod
    def random_chance(probability: float) -> bool:
        """Retorna True con una probabilidad dada."""
        return random.random() < probability


class AITransition:
    """Transición entre estados de IA."""
    
    def __init__(self, from_state: AIState, to_state: AIState, 
                 condition: Callable, priority: int = 0):
        """
        Inicializa una transición.
        
        Args:
            from_state: Estado origen
            to_state: Estado destino
            condition: Función de condición que retorna bool
            priority: Prioridad de la transición (mayor = más prioritario)
        """
        
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition
        self.priority = priority


class AIBehavior:
    """Comportamiento específico para un estado de IA."""
    
    def __init__(self, state: AIState, update_func: Callable):
        """
        Inicializa un comportamiento.
        
        Args:
            state: Estado al que pertenece
            update_func: Función que se ejecuta cada frame en este estado
        """
        
        self.state = state
        self.update_func = update_func


class FiniteStateMachine:
    """
    Máquina de estados finito para IA.
    """
    
    def __init__(self, initial_state: AIState):
        """
        Inicializa la FSM.
        
        Args:
            initial_state: Estado inicial
        """
        
        self.current_state = initial_state
        self.previous_state = initial_state
        self.state_timer = 0.0
        
        # Transiciones y comportamientos
        self.transitions: List[AITransition] = []
        self.behaviors: Dict[AIState, AIBehavior] = {}
        
        # Datos compartidos entre estados
        self.blackboard: Dict[str, Any] = {}
    
    def add_transition(self, transition: AITransition):
        """
        Añade una transición a la FSM.
        
        Args:
            transition: Transición a añadir
        """
        
        self.transitions.append(transition)
        # Ordenar por prioridad (mayor prioridad primero)
        self.transitions.sort(key=lambda t: t.priority, reverse=True)
    
    def add_behavior(self, behavior: AIBehavior):
        """
        Añade un comportamiento a la FSM.
        
        Args:
            behavior: Comportamiento a añadir
        """
        
        self.behaviors[behavior.state] = behavior
    
    def update(self, dt: float, ai_entity, context: Dict[str, Any]):
        """
        Actualiza la FSM.
        
        Args:
            dt: Delta time en segundos
            ai_entity: Entidad que posee esta IA
            context: Contexto del juego (player, physics_world, etc.)
        """
        
        self.state_timer += dt
        
        # Verificar transiciones
        for transition in self.transitions:
            if transition.from_state == self.current_state:
                try:
                    # Evaluar condición con contexto
                    if transition.condition(ai_entity, context, self):
                        self._change_state(transition.to_state)
                        break
                except Exception as e:
                    print(f"Error evaluando transición de IA: {e}")
        
        # Ejecutar comportamiento del estado actual
        if self.current_state in self.behaviors:
            try:
                self.behaviors[self.current_state].update_func(dt, ai_entity, context, self)
            except Exception as e:
                print(f"Error ejecutando comportamiento de IA: {e}")
    
    def _change_state(self, new_state: AIState):
        """
        Cambia al nuevo estado.
        
        Args:
            new_state: Nuevo estado
        """
        
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_timer = 0.0
            
            # Limpiar datos temporales del blackboard
            temp_keys = [key for key in self.blackboard.keys() if key.startswith('temp_')]
            for key in temp_keys:
                del self.blackboard[key]
    
    def get_state_time(self) -> float:
        """Obtiene el tiempo en el estado actual."""
        return self.state_timer
    
    def set_blackboard_value(self, key: str, value: Any):
        """
        Establece un valor en el blackboard.
        
        Args:
            key: Clave del valor
            value: Valor a establecer
        """
        
        self.blackboard[key] = value
    
    def get_blackboard_value(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor del blackboard.
        
        Args:
            key: Clave del valor
            default: Valor por defecto
            
        Returns:
            Valor almacenado o default
        """
        
        return self.blackboard.get(key, default)


class CommonAIBehaviors:
    """Comportamientos comunes de IA reutilizables."""
    
    @staticmethod
    def idle_behavior(dt: float, ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine):
        """Comportamiento de idle básico."""
        
        # Detenerse
        ai_entity.velocity_x = 0
        
        # Ocasionalmente cambiar dirección
        if fsm.get_state_time() > 2.0 and AICondition.random_chance(0.3):
            ai_entity.facing_right = not ai_entity.facing_right
    
    @staticmethod
    def patrol_behavior(dt: float, ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine):
        """Comportamiento de patrulla básico."""
        
        # Obtener centro de patrulla
        patrol_center = fsm.get_blackboard_value('patrol_center', ai_entity.x)
        patrol_distance = getattr(ai_entity, 'patrol_distance', 64.0)
        speed = getattr(ai_entity, 'speed', 50.0) * 0.5  # Velocidad reducida
        
        # Calcular distancia del centro
        distance_from_center = abs(ai_entity.x - patrol_center)
        
        if distance_from_center >= patrol_distance:
            # Regresar al centro
            if ai_entity.x > patrol_center:
                ai_entity.velocity_x = -speed
                ai_entity.facing_right = False
            else:
                ai_entity.velocity_x = speed
                ai_entity.facing_right = True
        else:
            # Continuar en la dirección actual o cambiar aleatoriamente
            if fsm.get_state_time() > 3.0 and AICondition.random_chance(0.2):
                ai_entity.facing_right = not ai_entity.facing_right
                fsm.set_blackboard_value('temp_timer', 0.0)
            
            if ai_entity.facing_right:
                ai_entity.velocity_x = speed
            else:
                ai_entity.velocity_x = -speed
    
    @staticmethod
    def chase_behavior(dt: float, ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine):
        """Comportamiento de persecución."""
        
        player = context.get('player')
        if not player:
            return
        
        speed = getattr(ai_entity, 'speed', 50.0)
        
        # Mover hacia el jugador
        if player.x > ai_entity.x:
            ai_entity.velocity_x = speed
            ai_entity.facing_right = True
        else:
            ai_entity.velocity_x = -speed
            ai_entity.facing_right = False
        
        # Actualizar última posición conocida
        fsm.set_blackboard_value('last_player_x', player.x)
        fsm.set_blackboard_value('last_player_y', player.y)
    
    @staticmethod
    def attack_behavior(dt: float, ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine):
        """Comportamiento de ataque."""
        
        # Detenerse para atacar
        ai_entity.velocity_x = 0
        
        # Verificar si ya está atacando
        if not getattr(ai_entity, 'is_attacking', False):
            # Iniciar ataque según el tipo de enemigo
            enemy_type = getattr(ai_entity, 'enemy_type', 'unknown')
            
            if enemy_type == 'maton':
                # Ataque lento pero fuerte
                if not getattr(ai_entity, 'is_winding_up', False):
                    ai_entity.is_winding_up = True
                    ai_entity.attack_windup_timer = Settings.MATON_ATTACK_WINDUP
            
            elif enemy_type == 'chacal':
                # Ataque a distancia
                if hasattr(ai_entity, '_start_attack'):
                    ai_entity._start_attack()
            
            elif enemy_type == 'luchador':
                # Ataque de agarre
                if hasattr(ai_entity, '_start_attack'):
                    ai_entity._start_attack()
            
            elif enemy_type == 'drone':
                # Ataque láser
                if hasattr(ai_entity, '_start_attack'):
                    ai_entity._start_attack()
    
    @staticmethod
    def flee_behavior(dt: float, ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine):
        """Comportamiento de huida."""
        
        player = context.get('player')
        if not player:
            return
        
        speed = getattr(ai_entity, 'speed', 50.0) * 1.2  # Velocidad aumentada
        
        # Huir del jugador
        if player.x > ai_entity.x:
            ai_entity.velocity_x = -speed
            ai_entity.facing_right = False
        else:
            ai_entity.velocity_x = speed
            ai_entity.facing_right = True
    
    @staticmethod
    def stunned_behavior(dt: float, ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine):
        """Comportamiento de stun."""
        
        # No hacer nada, detenerse
        ai_entity.velocity_x = 0


class AIConditions:
    """Condiciones específicas para transiciones de IA."""
    
    @staticmethod
    def player_detected(ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine) -> bool:
        """Detecta al jugador."""
        player = context.get('player')
        physics_world = context.get('physics_world')
        
        return AICondition.player_visible(ai_entity, player, physics_world)
    
    @staticmethod
    def player_in_attack_range(ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine) -> bool:
        """Jugador en rango de ataque."""
        player = context.get('player')
        attack_range = getattr(ai_entity, 'attack_range', 24.0)
        
        return AICondition.player_in_range(ai_entity, player, attack_range)
    
    @staticmethod
    def player_lost(ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine) -> bool:
        """Perdió al jugador."""
        player = context.get('player')
        physics_world = context.get('physics_world')
        detection_range = getattr(ai_entity, 'detection_range', 80.0)
        
        return not AICondition.player_in_range(ai_entity, player, detection_range * 1.5)
    
    @staticmethod
    def attack_finished(ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine) -> bool:
        """Ataque terminado."""
        return not getattr(ai_entity, 'is_attacking', False)
    
    @staticmethod
    def should_flee(ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine) -> bool:
        """Debería huir."""
        return AICondition.health_low(ai_entity, 0.2)
    
    @staticmethod
    def stun_expired(ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine) -> bool:
        """Stun expirado."""
        return AICondition.timer_expired(ai_entity, 'stun_timer')


def create_basic_enemy_ai(enemy_type: str) -> FiniteStateMachine:
    """
    Crea una FSM básica para un enemigo.
    
    Args:
        enemy_type: Tipo de enemigo
        
    Returns:
        FSM configurada para el enemigo
    """
    
    fsm = FiniteStateMachine(AIState.IDLE)
    
    # Añadir comportamientos
    fsm.add_behavior(AIBehavior(AIState.IDLE, CommonAIBehaviors.idle_behavior))
    fsm.add_behavior(AIBehavior(AIState.PATROL, CommonAIBehaviors.patrol_behavior))
    fsm.add_behavior(AIBehavior(AIState.CHASE, CommonAIBehaviors.chase_behavior))
    fsm.add_behavior(AIBehavior(AIState.ATTACK, CommonAIBehaviors.attack_behavior))
    fsm.add_behavior(AIBehavior(AIState.FLEE, CommonAIBehaviors.flee_behavior))
    fsm.add_behavior(AIBehavior(AIState.STUNNED, CommonAIBehaviors.stunned_behavior))
    
    # Transiciones comunes
    # Detectar jugador -> Chase
    fsm.add_transition(AITransition(
        AIState.IDLE, AIState.CHASE,
        AIConditions.player_detected, priority=5
    ))
    fsm.add_transition(AITransition(
        AIState.PATROL, AIState.CHASE,
        AIConditions.player_detected, priority=5
    ))
    
    # En rango de ataque -> Attack
    fsm.add_transition(AITransition(
        AIState.CHASE, AIState.ATTACK,
        AIConditions.player_in_attack_range, priority=8
    ))
    
    # Perder jugador -> Patrol
    fsm.add_transition(AITransition(
        AIState.CHASE, AIState.PATROL,
        AIConditions.player_lost, priority=3
    ))
    
    # Ataque terminado -> Chase o Patrol
    fsm.add_transition(AITransition(
        AIState.ATTACK, AIState.CHASE,
        lambda e, c, f: AIConditions.attack_finished(e, c, f) and AIConditions.player_detected(e, c, f),
        priority=6
    ))
    fsm.add_transition(AITransition(
        AIState.ATTACK, AIState.PATROL,
        lambda e, c, f: AIConditions.attack_finished(e, c, f) and not AIConditions.player_detected(e, c, f),
        priority=4
    ))
    
    # Salud baja -> Flee
    fsm.add_transition(AITransition(
        AIState.CHASE, AIState.FLEE,
        AIConditions.should_flee, priority=7
    ))
    fsm.add_transition(AITransition(
        AIState.ATTACK, AIState.FLEE,
        AIConditions.should_flee, priority=7
    ))
    
    # Stun expired -> Idle
    fsm.add_transition(AITransition(
        AIState.STUNNED, AIState.IDLE,
        AIConditions.stun_expired, priority=9
    ))
    
    # Transiciones específicas por tipo de enemigo
    if enemy_type == 'maton':
        # Matón es más agresivo, menos probable que huya
        pass
    
    elif enemy_type == 'chacal':
        # Chacal mantiene distancia
        fsm.add_transition(AITransition(
            AIState.CHASE, AIState.ATTACK,
            lambda e, c, f: AICondition.player_in_range(e, c.get('player'), 100.0),
            priority=6
        ))
    
    elif enemy_type == 'drone':
        # Dron patrulla aérea
        fsm.add_behavior(AIBehavior(AIState.PATROL, lambda dt, e, c, f: drone_patrol_behavior(dt, e, c, f)))
    
    return fsm


def drone_patrol_behavior(dt: float, ai_entity, context: Dict[str, Any], fsm: FiniteStateMachine):
    """Comportamiento específico de patrulla del dron."""
    
    # Usar comportamiento de patrulla básico pero mantener altura
    CommonAIBehaviors.patrol_behavior(dt, ai_entity, context, fsm)
    
    # Mantener altura de vuelo
    if hasattr(ai_entity, 'hover_height'):
        target_y = ai_entity.hover_height
        y_diff = target_y - ai_entity.y
        ai_entity.velocity_y = y_diff * 2.0


class AIManager:
    """
    Administrador global de IA.
    """
    
    def __init__(self):
        """Inicializa el administrador de IA."""
        
        self.ai_entities: Dict[str, FiniteStateMachine] = {}
        print("Administrador de IA inicializado")
    
    def register_entity(self, entity_id: str, enemy_type: str) -> FiniteStateMachine:
        """
        Registra una entidad en el sistema de IA.
        
        Args:
            entity_id: ID único de la entidad
            enemy_type: Tipo de enemigo
            
        Returns:
            FSM creada para la entidad
        """
        
        fsm = create_basic_enemy_ai(enemy_type)
        self.ai_entities[entity_id] = fsm
        
        print(f"IA registrada para entidad {entity_id} (tipo: {enemy_type})")
        return fsm
    
    def unregister_entity(self, entity_id: str):
        """
        Desregistra una entidad del sistema de IA.
        
        Args:
            entity_id: ID de la entidad
        """
        
        if entity_id in self.ai_entities:
            del self.ai_entities[entity_id]
            print(f"IA desregistrada para entidad {entity_id}")
    
    def update_all(self, dt: float, entities: Dict[str, Any], context: Dict[str, Any]):
        """
        Actualiza todas las IA registradas.
        
        Args:
            dt: Delta time en segundos
            entities: Diccionario de entidades del juego
            context: Contexto del juego
        """
        
        for entity_id, fsm in self.ai_entities.items():
            if entity_id in entities:
                entity = entities[entity_id]
                if hasattr(entity, 'is_alive') and entity.is_alive():
                    fsm.update(dt, entity, context)
    
    def clear_all(self):
        """Limpia todas las IA."""
        
        self.ai_entities.clear()
        print("Sistema de IA limpiado")