"""
Tests para módulos individuales del juego Chen Toka — Sinaloa Dragon.
Tests unitarios que no requieren pygame inicializado.
"""

import unittest
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestGameLogic(unittest.TestCase):
    """Tests de lógica del juego que no requieren pygame."""
    
    def test_import_structure(self):
        """Verificar que la estructura de imports es correcta."""
        # Test básico de estructura de archivos
        src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        self.assertTrue(os.path.exists(src_dir))
        
        # Verificar archivos principales
        main_file = os.path.join(src_dir, 'main.py')
        self.assertTrue(os.path.exists(main_file))
        
        game_file = os.path.join(src_dir, 'game.py')
        self.assertTrue(os.path.exists(game_file))
    
    def test_constants_sanity(self):
        """Tests básicos de constantes sin importar módulos complejos."""
        # Verificar que los archivos contienen constantes esperadas
        settings_file = os.path.join(os.path.dirname(__file__), '..', 'src', 'settings.py')
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('SCREEN_WIDTH', content)
                self.assertIn('SCREEN_HEIGHT', content)
                self.assertIn('FPS', content)
    
    def test_project_files_exist(self):
        """Verificar que todos los archivos del proyecto existen."""
        project_root = os.path.join(os.path.dirname(__file__), '..')
        
        # Archivos de configuración
        self.assertTrue(os.path.exists(os.path.join(project_root, 'README.md')))
        self.assertTrue(os.path.exists(os.path.join(project_root, 'requirements.txt')))
        self.assertTrue(os.path.exists(os.path.join(project_root, 'LICENSE')))
        self.assertTrue(os.path.exists(os.path.join(project_root, 'setup.cfg')))
        
        # Scripts de build
        self.assertTrue(os.path.exists(os.path.join(project_root, 'build_exe.py')))
        self.assertTrue(os.path.exists(os.path.join(project_root, 'run_game.py')))
        
        # Directorio src
        src_dir = os.path.join(project_root, 'src')
        self.assertTrue(os.path.exists(src_dir))
        
        # Módulos principales
        core_modules = [
            'main.py', 'game.py', 'settings.py', 'assets.py', 'input.py'
        ]
        
        for module in core_modules:
            module_path = os.path.join(src_dir, module)
            self.assertTrue(os.path.exists(module_path), f"Falta módulo: {module}")
        
        # Módulos ECS
        ecs_modules = [
            'player.py', 'enemies.py', 'physics.py', 'combat.py', 'ai.py'
        ]
        
        for module in ecs_modules:
            module_path = os.path.join(src_dir, module)
            self.assertTrue(os.path.exists(module_path), f"Falta módulo ECS: {module}")
        
        # Módulos UI
        ui_modules = [
            'hud.py', 'menus.py'
        ]
        
        for module in ui_modules:
            module_path = os.path.join(src_dir, module)
            self.assertTrue(os.path.exists(module_path), f"Falta módulo UI: {module}")
        
        # Módulos de sistema
        system_modules = [
            'loader.py', 'hazards.py', 'save_system.py', 'config.py'
        ]
        
        for module in system_modules:
            module_path = os.path.join(src_dir, module)
            self.assertTrue(os.path.exists(module_path), f"Falta módulo de sistema: {module}")
    
    def test_data_files_exist(self):
        """Verificar que los archivos de datos del juego existen."""
        project_root = os.path.join(os.path.dirname(__file__), '..')
        data_dir = os.path.join(project_root, 'data')
        
        if os.path.exists(data_dir):
            # Verificar archivos de niveles
            level_files = [
                'cdmx_centro.json',
                'guadalajara_centro.json', 
                'oaxaca_monte.json'
            ]
            
            for level_file in level_files:
                level_path = os.path.join(data_dir, 'levels', level_file)
                if os.path.exists(level_path):
                    # Verificar que es JSON válido
                    import json
                    with open(level_path, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            self.assertIsInstance(data, dict)
                            self.assertIn('name', data)
                            self.assertIn('platforms', data)
                        except json.JSONDecodeError:
                            self.fail(f"Archivo JSON inválido: {level_file}")
    
    def test_readme_content(self):
        """Verificar contenido básico del README."""
        readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
        
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Verificar secciones importantes
                self.assertIn('Chen Toka', content)
                self.assertIn('Sinaloa Dragon', content)
                self.assertIn('Instalación', content)
                self.assertIn('Controles', content)
                self.assertIn('pygame', content)
    
    def test_requirements_format(self):
        """Verificar formato del archivo requirements.txt."""
        req_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
        
        if os.path.exists(req_path):
            with open(req_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # Verificar que contiene pygame
                pygame_found = False
                for line in lines:
                    if 'pygame' in line.lower():
                        pygame_found = True
                        break
                
                self.assertTrue(pygame_found, "requirements.txt debe contener pygame")


class TestCodeQuality(unittest.TestCase):
    """Tests básicos de calidad de código."""
    
    def test_python_syntax(self):
        """Verificar que todos los archivos Python tienen sintaxis válida."""
        src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        
        if os.path.exists(src_dir):
            import ast
            
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            try:
                                content = f.read()
                                ast.parse(content)
                            except SyntaxError as e:
                                self.fail(f"Error de sintaxis en {file}: {e}")
    
    def test_encoding_headers(self):
        """Verificar que los archivos Python tienen encoding UTF-8."""
        src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        
        if os.path.exists(src_dir):
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            try:
                                # Solo verificar que se puede leer como UTF-8
                                content = f.read()
                                # Verificar que no hay caracteres problemáticos
                                content.encode('utf-8')
                            except UnicodeDecodeError:
                                self.fail(f"Problema de encoding en {file}")


if __name__ == '__main__':
    unittest.main()