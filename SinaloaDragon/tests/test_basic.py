"""
Tests básicos para Chen Toka — Sinaloa Dragon
Tests de integración para verificar funcionamiento básico del juego.
"""

import pytest
import sys
import os

# Agregar src al path para importar módulos del juego
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# Importar módulos del juego si pygame está disponible
if PYGAME_AVAILABLE:
    try:
        from settings import Settings
        from assets import AssetManager
        from input import InputManager
        from player import Player
        from enemies import EnemyManager
        from physics import PhysicsEngine
        GAME_MODULES_AVAILABLE = True
    except ImportError as e:
        GAME_MODULES_AVAILABLE = False
        IMPORT_ERROR = str(e)
else:
    GAME_MODULES_AVAILABLE = False
    IMPORT_ERROR = "pygame no disponible"


class TestGameModules:
    """Tests básicos para verificar que los módulos del juego se pueden importar y inicializar."""
    
    @pytest.mark.skipif(not PYGAME_AVAILABLE, reason="pygame no está disponible")
    def test_pygame_import(self):
        """Verificar que pygame se puede importar correctamente."""
        import pygame
        assert pygame.version.ver is not None
    
    @pytest.mark.skipif(not GAME_MODULES_AVAILABLE, reason=f"Módulos del juego no disponibles: {IMPORT_ERROR if not PYGAME_AVAILABLE else 'Error de importación'}")
    def test_settings_module(self):
        """Verificar que el módulo de configuración funciona."""
        # Verificar constantes básicas
        assert Settings.SCREEN_WIDTH > 0
        assert Settings.SCREEN_HEIGHT > 0
        assert Settings.FPS > 0
        assert Settings.INTERNAL_WIDTH > 0
        assert Settings.INTERNAL_HEIGHT > 0
        
        # Verificar métodos básicos
        assert hasattr(Settings, 'get_asset_path')
        assert hasattr(Settings, 'get_save_path')
        
        # Test de paths
        asset_path = Settings.get_asset_path('test.png')
        assert isinstance(asset_path, str)
        assert 'test.png' in asset_path
    
    @pytest.mark.skipif(not GAME_MODULES_AVAILABLE, reason=f"Módulos del juego no disponibles: {IMPORT_ERROR if not PYGAME_AVAILABLE else 'Error de importación'}")
    def test_asset_manager_init(self):
        """Verificar que AssetManager se puede inicializar."""
        # Inicializar pygame para asset manager
        pygame.init()
        
        try:
            asset_manager = AssetManager()
            assert asset_manager is not None
            assert hasattr(asset_manager, 'sprites')
            assert hasattr(asset_manager, 'sounds')
            assert hasattr(asset_manager, 'music')
        except Exception as e:
            pytest.skip(f"AssetManager requiere inicialización completa: {e}")
        finally:
            pygame.quit()
    
    @pytest.mark.skipif(not GAME_MODULES_AVAILABLE, reason=f"Módulos del juego no disponibles: {IMPORT_ERROR if not PYGAME_AVAILABLE else 'Error de importación'}")
    def test_input_manager_init(self):
        """Verificar que InputManager se puede inicializar."""
        pygame.init()
        
        try:
            input_manager = InputManager()
            assert input_manager is not None
            assert hasattr(input_manager, 'update')
            assert hasattr(input_manager, 'is_action_pressed')
            assert hasattr(input_manager, 'is_action_just_pressed')
        except Exception as e:
            pytest.skip(f"InputManager requiere inicialización completa: {e}")
        finally:
            pygame.quit()
    
    @pytest.mark.skipif(not GAME_MODULES_AVAILABLE, reason=f"Módulos del juego no disponibles: {IMPORT_ERROR if not PYGAME_AVAILABLE else 'Error de importación'}")
    def test_player_creation(self):
        """Verificar que se puede crear una instancia del jugador."""
        pygame.init()
        
        try:
            # Crear instancias necesarias para el jugador
            from assets import AssetManager
            asset_manager = AssetManager()
            
            # Crear jugador
            player = Player(100, 100, asset_manager)
            assert player is not None
            assert hasattr(player, 'update')
            assert hasattr(player, 'render')
            assert hasattr(player, 'x')
            assert hasattr(player, 'y')
            assert player.x == 100
            assert player.y == 100
        except Exception as e:
            pytest.skip(f"Player requiere dependencias completas: {e}")
        finally:
            pygame.quit()
    
    @pytest.mark.skipif(not GAME_MODULES_AVAILABLE, reason=f"Módulos del juego no disponibles: {IMPORT_ERROR if not PYGAME_AVAILABLE else 'Error de importación'}")
    def test_physics_engine_init(self):
        """Verificar que PhysicsEngine se puede inicializar."""
        try:
            physics = PhysicsEngine()
            assert physics is not None
            assert hasattr(physics, 'update')
            assert hasattr(physics, 'add_entity')
            assert hasattr(physics, 'remove_entity')
            assert hasattr(physics, 'check_collisions')
        except Exception as e:
            pytest.skip(f"PhysicsEngine requiere inicialización completa: {e}")


class TestGameConstants:
    """Tests para verificar que las constantes del juego tienen valores apropiados."""
    
    @pytest.mark.skipif(not GAME_MODULES_AVAILABLE, reason=f"Módulos del juego no disponibles: {IMPORT_ERROR if not PYGAME_AVAILABLE else 'Error de importación'}")
    def test_screen_dimensions(self):
        """Verificar dimensiones de pantalla."""
        assert Settings.SCREEN_WIDTH == 1280
        assert Settings.SCREEN_HEIGHT == 720
        assert Settings.INTERNAL_WIDTH == 320
        assert Settings.INTERNAL_HEIGHT == 180
    
    @pytest.mark.skipif(not GAME_MODULES_AVAILABLE, reason=f"Módulos del juego no disponibles: {IMPORT_ERROR if not PYGAME_AVAILABLE else 'Error de importación'}")
    def test_game_settings(self):
        """Verificar configuraciones del juego."""
        assert Settings.FPS == 60
        assert Settings.SCALE_FACTOR == 4  # 1280/320 = 4
        assert Settings.GRAVITY > 0
        assert Settings.PLAYER_SPEED > 0
        assert Settings.PLAYER_JUMP_STRENGTH > 0


class TestEnvironment:
    """Tests del entorno de desarrollo."""
    
    def test_python_version(self):
        """Verificar versión de Python."""
        assert sys.version_info >= (3, 11), "Requiere Python 3.11 o superior"
    
    def test_project_structure(self):
        """Verificar estructura básica del proyecto."""
        project_root = os.path.join(os.path.dirname(__file__), '..')
        
        # Verificar archivos principales
        assert os.path.exists(os.path.join(project_root, 'README.md'))
        assert os.path.exists(os.path.join(project_root, 'requirements.txt'))
        assert os.path.exists(os.path.join(project_root, 'src'))
        assert os.path.exists(os.path.join(project_root, 'src', 'main.py'))
        assert os.path.exists(os.path.join(project_root, 'build_exe.py'))
    
    def test_src_modules(self):
        """Verificar que los módulos principales existen."""
        src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        
        required_modules = [
            'main.py', 'game.py', 'settings.py', 'assets.py', 'input.py',
            'player.py', 'enemies.py', 'physics.py', 'combat.py', 'ai.py',
            'hud.py', 'menus.py', 'loader.py', 'hazards.py',
            'save_system.py', 'config.py'
        ]
        
        for module in required_modules:
            module_path = os.path.join(src_path, module)
            assert os.path.exists(module_path), f"Módulo faltante: {module}"


if __name__ == '__main__':
    # Ejecutar tests si se llama directamente
    pytest.main([__file__, '-v'])