"""
Sistema de Guardado para Chen Toka - Sinaloa Dragon

Este módulo maneja el guardado y carga de progreso del juego,
incluyendo configuraciones, estadísticas y estado del jugador.
"""

import json
import os
import time
import hashlib
from typing import Dict, Any, Optional, List
from settings import Settings


class SaveData:
    """Estructura de datos de guardado del juego."""
    
    def __init__(self):
        """Inicializa los datos de guardado con valores por defecto."""
        
        # Información general
        self.version = Settings.GAME_VERSION
        self.created_timestamp = time.time()
        self.last_saved_timestamp = time.time()
        self.total_playtime = 0.0  # en segundos
        
        # Progreso del juego
        self.current_level = "cdmx_centro"
        self.levels_unlocked = ["cdmx_centro"]
        self.levels_completed = []
        self.current_city = "cdmx"
        
        # Estado del jugador
        self.player_health = Settings.PLAYER_MAX_HEALTH
        self.player_lives = Settings.PLAYER_LIVES
        self.super_meter = 0
        self.coins_collected = 0
        self.total_coins_collected = 0
        
        # Estadísticas
        self.enemies_defeated = 0
        self.total_enemies_defeated = 0
        self.deaths = 0
        self.jumps_made = 0
        self.attacks_performed = 0
        self.combos_executed = 0
        self.highest_combo = 0
        self.distance_traveled = 0.0
        
        # Desbloqueables y logros
        self.achievements_unlocked = []
        self.special_abilities_unlocked = []
        self.skins_unlocked = ["default"]
        self.current_skin = "default"
        
        # Configuraciones de juego
        self.difficulty = "normal"
        self.audio_enabled = True
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.debug_mode = False
        
        # Controles personalizados
        self.custom_controls = {}
        
        # Estadísticas por nivel
        self.level_stats = {}
        
        print("Datos de guardado inicializados")
    
    def update_playtime(self, session_time: float):
        """
        Actualiza el tiempo total de juego.
        
        Args:
            session_time: Tiempo de la sesión actual en segundos
        """
        
        self.total_playtime += session_time
        self.last_saved_timestamp = time.time()
    
    def unlock_level(self, level_name: str):
        """
        Desbloquea un nivel.
        
        Args:
            level_name: Nombre del nivel a desbloquear
        """
        
        if level_name not in self.levels_unlocked:
            self.levels_unlocked.append(level_name)
            print(f"Nivel desbloqueado: {level_name}")
    
    def complete_level(self, level_name: str, stats: Dict[str, Any]):
        """
        Marca un nivel como completado y actualiza estadísticas.
        
        Args:
            level_name: Nombre del nivel completado
            stats: Estadísticas del nivel
        """
        
        if level_name not in self.levels_completed:
            self.levels_completed.append(level_name)
            print(f"Nivel completado: {level_name}")
        
        # Actualizar estadísticas del nivel
        self.level_stats[level_name] = {
            'completion_time': stats.get('completion_time', 0),
            'coins_collected': stats.get('coins_collected', 0),
            'enemies_defeated': stats.get('enemies_defeated', 0),
            'deaths': stats.get('deaths', 0),
            'best_combo': stats.get('best_combo', 0),
            'completed_timestamp': time.time()
        }
        
        # Actualizar estadísticas totales
        self.total_coins_collected += stats.get('coins_collected', 0)
        self.total_enemies_defeated += stats.get('enemies_defeated', 0)
        
        # Verificar desbloqueables
        self._check_unlockables()
    
    def unlock_achievement(self, achievement_id: str):
        """
        Desbloquea un logro.
        
        Args:
            achievement_id: ID del logro a desbloquear
        """
        
        if achievement_id not in self.achievements_unlocked:
            self.achievements_unlocked.append(achievement_id)
            print(f"¡Logro desbloqueado: {achievement_id}!")
    
    def _check_unlockables(self):
        """Verifica y desbloquea contenido basado en progreso."""
        
        # Desbloqueables por niveles completados
        completed_count = len(self.levels_completed)
        
        if completed_count >= 1:
            self.unlock_achievement("first_level_complete")
            if "guadalajara_centro" not in self.levels_unlocked:
                self.unlock_level("guadalajara_centro")
        
        if completed_count >= 2:
            self.unlock_achievement("second_level_complete")
            if "oaxaca_monte" not in self.levels_unlocked:
                self.unlock_level("oaxaca_monte")
        
        if completed_count >= 3:
            self.unlock_achievement("all_levels_complete")
            if "master_skin" not in self.skins_unlocked:
                self.skins_unlocked.append("master_skin")
        
        # Desbloqueables por monedas
        if self.total_coins_collected >= 25:
            self.unlock_achievement("coin_collector")
        
        if self.total_coins_collected >= 60:
            self.unlock_achievement("coin_master")
            if "golden_skin" not in self.skins_unlocked:
                self.skins_unlocked.append("golden_skin")
        
        # Desbloqueables por combos
        if self.highest_combo >= 10:
            self.unlock_achievement("combo_fighter")
        
        if self.highest_combo >= 25:
            self.unlock_achievement("combo_master")
            if "combo_boost" not in self.special_abilities_unlocked:
                self.special_abilities_unlocked.append("combo_boost")
        
        # Desbloqueables por enemigos derrotados
        if self.total_enemies_defeated >= 50:
            self.unlock_achievement("enemy_slayer")
        
        if self.total_enemies_defeated >= 100:
            self.unlock_achievement("dragon_warrior")
            if "warrior_skin" not in self.skins_unlocked:
                self.skins_unlocked.append("warrior_skin")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte los datos de guardado a diccionario.
        
        Returns:
            Diccionario con todos los datos de guardado
        """
        
        return {
            'version': self.version,
            'created_timestamp': self.created_timestamp,
            'last_saved_timestamp': self.last_saved_timestamp,
            'total_playtime': self.total_playtime,
            'current_level': self.current_level,
            'levels_unlocked': self.levels_unlocked,
            'levels_completed': self.levels_completed,
            'current_city': self.current_city,
            'player_health': self.player_health,
            'player_lives': self.player_lives,
            'super_meter': self.super_meter,
            'coins_collected': self.coins_collected,
            'total_coins_collected': self.total_coins_collected,
            'enemies_defeated': self.enemies_defeated,
            'total_enemies_defeated': self.total_enemies_defeated,
            'deaths': self.deaths,
            'jumps_made': self.jumps_made,
            'attacks_performed': self.attacks_performed,
            'combos_executed': self.combos_executed,
            'highest_combo': self.highest_combo,
            'distance_traveled': self.distance_traveled,
            'achievements_unlocked': self.achievements_unlocked,
            'special_abilities_unlocked': self.special_abilities_unlocked,
            'skins_unlocked': self.skins_unlocked,
            'current_skin': self.current_skin,
            'difficulty': self.difficulty,
            'audio_enabled': self.audio_enabled,
            'music_volume': self.music_volume,
            'sfx_volume': self.sfx_volume,
            'debug_mode': self.debug_mode,
            'custom_controls': self.custom_controls,
            'level_stats': self.level_stats
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """
        Carga datos desde un diccionario.
        
        Args:
            data: Diccionario con datos de guardado
        """
        
        # Cargar datos básicos
        self.version = data.get('version', Settings.GAME_VERSION)
        self.created_timestamp = data.get('created_timestamp', time.time())
        self.last_saved_timestamp = data.get('last_saved_timestamp', time.time())
        self.total_playtime = data.get('total_playtime', 0.0)
        
        # Progreso del juego
        self.current_level = data.get('current_level', "cdmx_centro")
        self.levels_unlocked = data.get('levels_unlocked', ["cdmx_centro"])
        self.levels_completed = data.get('levels_completed', [])
        self.current_city = data.get('current_city', "cdmx")
        
        # Estado del jugador
        self.player_health = data.get('player_health', Settings.PLAYER_MAX_HEALTH)
        self.player_lives = data.get('player_lives', Settings.PLAYER_LIVES)
        self.super_meter = data.get('super_meter', 0)
        self.coins_collected = data.get('coins_collected', 0)
        self.total_coins_collected = data.get('total_coins_collected', 0)
        
        # Estadísticas
        self.enemies_defeated = data.get('enemies_defeated', 0)
        self.total_enemies_defeated = data.get('total_enemies_defeated', 0)
        self.deaths = data.get('deaths', 0)
        self.jumps_made = data.get('jumps_made', 0)
        self.attacks_performed = data.get('attacks_performed', 0)
        self.combos_executed = data.get('combos_executed', 0)
        self.highest_combo = data.get('highest_combo', 0)
        self.distance_traveled = data.get('distance_traveled', 0.0)
        
        # Desbloqueables
        self.achievements_unlocked = data.get('achievements_unlocked', [])
        self.special_abilities_unlocked = data.get('special_abilities_unlocked', [])
        self.skins_unlocked = data.get('skins_unlocked', ["default"])
        self.current_skin = data.get('current_skin', "default")
        
        # Configuraciones
        self.difficulty = data.get('difficulty', "normal")
        self.audio_enabled = data.get('audio_enabled', True)
        self.music_volume = data.get('music_volume', 0.7)
        self.sfx_volume = data.get('sfx_volume', 0.8)
        self.debug_mode = data.get('debug_mode', False)
        self.custom_controls = data.get('custom_controls', {})
        self.level_stats = data.get('level_stats', {})
        
        print("Datos de guardado cargados desde diccionario")


class SaveSystem:
    """
    Sistema principal de guardado y carga del juego.
    """
    
    def __init__(self, save_directory: str = None):
        """
        Inicializa el sistema de guardado.
        
        Args:
            save_directory: Directorio donde guardar los archivos
        """
        
        self.save_directory = save_directory or Settings.SAVE_DIRECTORY
        self.save_file = os.path.join(self.save_directory, "save_game.json")
        self.backup_file = os.path.join(self.save_directory, "save_game_backup.json")
        self.config_file = os.path.join(self.save_directory, "config.json")
        
        # Datos actuales
        self.save_data = SaveData()
        self.session_start_time = time.time()
        
        # Crear directorio si no existe
        self._ensure_save_directory()
        
        print(f"Sistema de guardado inicializado en: {self.save_directory}")
    
    def _ensure_save_directory(self):
        """Asegura que el directorio de guardado existe."""
        
        try:
            os.makedirs(self.save_directory, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorio de guardado: {e}")
    
    def _calculate_checksum(self, data: str) -> str:
        """
        Calcula checksum para verificar integridad de datos.
        
        Args:
            data: Datos en formato string
            
        Returns:
            Checksum MD5
        """
        
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    def save_game(self, force_backup: bool = False) -> bool:
        """
        Guarda el juego actual.
        
        Args:
            force_backup: Si crear backup independientemente
            
        Returns:
            True si el guardado fue exitoso
        """
        
        try:
            # Actualizar tiempo de sesión
            session_time = time.time() - self.session_start_time
            self.save_data.update_playtime(session_time)
            self.session_start_time = time.time()
            
            # Preparar datos para guardar
            save_dict = self.save_data.to_dict()
            json_data = json.dumps(save_dict, indent=2, ensure_ascii=False)
            
            # Calcular checksum
            checksum = self._calculate_checksum(json_data)
            
            # Estructura final con checksum
            final_data = {
                'checksum': checksum,
                'data': save_dict
            }
            
            # Crear backup si existe archivo previo o se fuerza
            if os.path.exists(self.save_file) or force_backup:
                self._create_backup()
            
            # Guardar archivo principal
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=2, ensure_ascii=False)
            
            print(f"Juego guardado exitosamente en: {self.save_file}")
            return True
            
        except Exception as e:
            print(f"Error guardando el juego: {e}")
            return False
    
    def load_game(self) -> bool:
        """
        Carga el juego guardado.
        
        Returns:
            True si la carga fue exitosa
        """
        
        # Intentar cargar archivo principal
        if self._load_from_file(self.save_file):
            return True
        
        # Si falla, intentar backup
        print("Archivo principal corrupto, intentando backup...")
        if self._load_from_file(self.backup_file):
            print("Juego cargado desde backup")
            # Restaurar archivo principal desde backup
            self.save_game()
            return True
        
        print("No se pudo cargar ningún archivo de guardado")
        return False
    
    def _load_from_file(self, file_path: str) -> bool:
        """
        Carga datos desde un archivo específico.
        
        Args:
            file_path: Ruta del archivo a cargar
            
        Returns:
            True si la carga fue exitosa
        """
        
        try:
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            # Verificar estructura
            if 'data' not in file_data:
                print(f"Estructura de archivo inválida: {file_path}")
                return False
            
            save_dict = file_data['data']
            
            # Verificar checksum si existe
            if 'checksum' in file_data:
                json_data = json.dumps(save_dict, indent=2, ensure_ascii=False)
                expected_checksum = self._calculate_checksum(json_data)
                
                if file_data['checksum'] != expected_checksum:
                    print(f"Checksum inválido en: {file_path}")
                    return False
            
            # Cargar datos
            self.save_data.from_dict(save_dict)
            self.session_start_time = time.time()
            
            print(f"Juego cargado exitosamente desde: {file_path}")
            return True
            
        except Exception as e:
            print(f"Error cargando desde {file_path}: {e}")
            return False
    
    def _create_backup(self):
        """Crea una copia de seguridad del archivo actual."""
        
        try:
            if os.path.exists(self.save_file):
                import shutil
                shutil.copy2(self.save_file, self.backup_file)
                print("Backup creado exitosamente")
        except Exception as e:
            print(f"Error creando backup: {e}")
    
    def delete_save(self) -> bool:
        """
        Elimina todos los archivos de guardado.
        
        Returns:
            True si la eliminación fue exitosa
        """
        
        try:
            files_to_delete = [self.save_file, self.backup_file]
            
            for file_path in files_to_delete:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Archivo eliminado: {file_path}")
            
            # Reinicializar datos
            self.save_data = SaveData()
            self.session_start_time = time.time()
            
            print("Datos de guardado eliminados y reinicializados")
            return True
            
        except Exception as e:
            print(f"Error eliminando archivos de guardado: {e}")
            return False
    
    def has_save_file(self) -> bool:
        """
        Verifica si existe un archivo de guardado.
        
        Returns:
            True si existe archivo de guardado
        """
        
        return os.path.exists(self.save_file) or os.path.exists(self.backup_file)
    
    def get_save_info(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene información básica del archivo de guardado.
        
        Returns:
            Diccionario con información o None si no existe
        """
        
        if not self.has_save_file():
            return None
        
        try:
            file_to_check = self.save_file if os.path.exists(self.save_file) else self.backup_file
            
            with open(file_to_check, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            save_dict = file_data.get('data', {})
            
            return {
                'current_level': save_dict.get('current_level', 'Desconocido'),
                'total_playtime': save_dict.get('total_playtime', 0),
                'levels_completed': len(save_dict.get('levels_completed', [])),
                'total_coins': save_dict.get('total_coins_collected', 0),
                'last_saved': save_dict.get('last_saved_timestamp', 0)
            }
            
        except Exception as e:
            print(f"Error obteniendo información de guardado: {e}")
            return None
    
    def export_save(self, export_path: str) -> bool:
        """
        Exporta el guardado a un archivo específico.
        
        Args:
            export_path: Ruta donde exportar
            
        Returns:
            True si la exportación fue exitosa
        """
        
        try:
            if not os.path.exists(self.save_file):
                print("No hay archivo de guardado para exportar")
                return False
            
            import shutil
            shutil.copy2(self.save_file, export_path)
            
            print(f"Guardado exportado a: {export_path}")
            return True
            
        except Exception as e:
            print(f"Error exportando guardado: {e}")
            return False
    
    def import_save(self, import_path: str) -> bool:
        """
        Importa un guardado desde un archivo específico.
        
        Args:
            import_path: Ruta del archivo a importar
            
        Returns:
            True si la importación fue exitosa
        """
        
        try:
            if not os.path.exists(import_path):
                print(f"Archivo de importación no encontrado: {import_path}")
                return False
            
            # Crear backup del guardado actual si existe
            if os.path.exists(self.save_file):
                self._create_backup()
            
            # Intentar cargar el archivo importado
            if self._load_from_file(import_path):
                # Si la carga es exitosa, guardar como archivo principal
                self.save_game()
                print(f"Guardado importado exitosamente desde: {import_path}")
                return True
            else:
                print("Error validando archivo importado")
                return False
                
        except Exception as e:
            print(f"Error importando guardado: {e}")
            return False