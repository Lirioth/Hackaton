"""
Script para ejecutar el juego Chen Toka — Sinaloa Dragon.
Launcher principal del juego con verificaciones de dependencias.
"""

import sys
import os
import subprocess


def main():
    """Ejecutar el juego con verificaciones previas."""
    
    print("🎮 Chen Toka — Sinaloa Dragon")
    print("=" * 40)
    
    # Cambiar al directorio del proyecto
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Agregar src al path
    src_path = os.path.join(project_root, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Verificar dependencias
    if not check_dependencies():
        return False
    
    # Ejecutar el juego
    try:
        print("🚀 Iniciando juego...")
        from main import main as game_main
        game_main()
        
    except ImportError as e:
        print(f"❌ Error importando módulos del juego: {e}")
        print("💡 Asegúrate de que todos los archivos estén en src/")
        return False
        
    except Exception as e:
        print(f"❌ Error ejecutando el juego: {e}")
        return False
    
    return True


def check_dependencies():
    """Verificar que las dependencias estén instaladas."""
    
    print("📦 Verificando dependencias...")
    
    # Verificar pygame
    try:
        import pygame
        print(f"✅ pygame {pygame.version.ver}")
    except ImportError:
        print("❌ pygame no está instalado")
        print("💡 Ejecuta: pip install pygame")
        return False
    
    # Verificar pygame-ce (opcional)
    try:
        import pygame_ce
        print(f"✅ pygame-ce disponible")
    except ImportError:
        print("⚠️  pygame-ce no disponible (opcional)")
    
    return True


def check_project_structure():
    """Verificar estructura básica del proyecto."""
    
    print("📁 Verificando estructura del proyecto...")
    
    required_files = [
        'src/main.py',
        'src/game.py',
        'src/settings.py',
        'src/assets.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {missing_files}")
        return False
    
    print("✅ Estructura del proyecto OK")
    return True


def install_dependencies():
    """Instalar dependencias automáticamente."""
    
    print("🔧 Instalando dependencias...")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            'pygame', '--only-binary=all'
        ])
        print("✅ pygame instalado")
        
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            'pygame-ce', '--only-binary=all'
        ])
        print("✅ pygame-ce instalado")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False


if __name__ == '__main__':
    # Permitir instalación automática con argumento
    if len(sys.argv) > 1 and sys.argv[1] == '--install':
        install_dependencies()
        sys.exit(0)
    
    # Verificar estructura del proyecto
    if not check_project_structure():
        print("\n💡 Parece que faltan archivos del proyecto.")
        print("   Asegúrate de estar en el directorio correcto.")
        sys.exit(1)
    
    # Ejecutar juego
    success = main()
    
    if not success:
        print("\n💡 Consejos para solucionar problemas:")
        print("   - Ejecuta: python run_game.py --install")
        print("   - Verifica que estés en el directorio correcto")
        print("   - Revisa que todos los archivos estén en src/")
        sys.exit(1)
    
    print("\n👋 ¡Gracias por jugar!")