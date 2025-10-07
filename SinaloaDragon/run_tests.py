"""
Script para ejecutar tests del proyecto Chen Toka — Sinaloa Dragon.
Ejecuta tests con diferentes configuraciones según las dependencias disponibles.
"""

import sys
import os
import subprocess

def main():
    """Ejecutar tests con diferentes configuraciones."""
    
    print("🎮 Chen Toka — Sinaloa Dragon Test Runner")
    print("=" * 50)
    
    # Cambiar al directorio del proyecto
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Verificar dependencias
    pygame_available = check_pygame()
    pytest_available = check_pytest()
    
    print(f"📦 pygame disponible: {'✅' if pygame_available else '❌'}")
    print(f"🧪 pytest disponible: {'✅' if pytest_available else '❌'}")
    print()
    
    if pytest_available:
        run_pytest_tests(pygame_available)
    else:
        run_unittest_tests()
    
    print("\n🏁 Tests completados!")


def check_pygame():
    """Verificar si pygame está disponible."""
    try:
        import pygame
        return True
    except ImportError:
        return False


def check_pytest():
    """Verificar si pytest está disponible."""
    try:
        import pytest
        return True
    except ImportError:
        return False


def run_pytest_tests(pygame_available):
    """Ejecutar tests con pytest."""
    print("🚀 Ejecutando tests con pytest...")
    
    # Configurar argumentos de pytest
    pytest_args = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--durations=10'
    ]
    
    # Si pygame no está disponible, saltar tests que lo requieren
    if not pygame_available:
        pytest_args.extend(['-m', 'not pygame'])
        print("⚠️  Saltando tests que requieren pygame")
    
    # Ejecutar pytest
    try:
        result = subprocess.run(pytest_args, capture_output=True, text=True)
        
        print("📋 Salida de pytest:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Errores/Advertencias:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Todos los tests pasaron!")
        else:
            print(f"❌ Tests fallaron (código: {result.returncode})")
            
    except Exception as e:
        print(f"❌ Error ejecutando pytest: {e}")
        run_unittest_tests()


def run_unittest_tests():
    """Ejecutar tests con unittest como fallback."""
    print("🚀 Ejecutando tests con unittest...")
    
    # Ejecutar tests unitarios que no requieren dependencias externas
    unittest_args = [
        sys.executable, '-m', 'unittest',
        'tests.test_unit',
        '-v'
    ]
    
    try:
        result = subprocess.run(unittest_args, capture_output=True, text=True)
        
        print("📋 Salida de unittest:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Errores/Advertencias:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Tests unitarios pasaron!")
        else:
            print(f"❌ Tests unitarios fallaron (código: {result.returncode})")
            
    except Exception as e:
        print(f"❌ Error ejecutando unittest: {e}")


def run_quick_checks():
    """Ejecutar verificaciones rápidas del proyecto."""
    print("⚡ Ejecutando verificaciones rápidas...")
    
    # Verificar estructura del proyecto
    print("📁 Verificando estructura del proyecto...")
    
    required_files = [
        'README.md',
        'requirements.txt', 
        'LICENSE',
        'setup.cfg',
        'src/main.py',
        'src/game.py',
        'src/settings.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
    else:
        print("✅ Estructura del proyecto OK")
    
    # Verificar sintaxis Python
    print("🐍 Verificando sintaxis Python...")
    python_files = []
    
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    syntax_errors = []
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), py_file, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{py_file}: {e}")
    
    if syntax_errors:
        print("❌ Errores de sintaxis encontrados:")
        for error in syntax_errors:
            print(f"  {error}")
    else:
        print("✅ Sintaxis Python OK")


if __name__ == '__main__':
    # Permitir ejecutar verificaciones rápidas con argumento
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        run_quick_checks()
    else:
        main()