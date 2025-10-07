"""
Script de verificación final para Chen Toka — Sinaloa Dragon.
Verifica que todo esté listo para distribución.
"""

import os
import sys
import json
import ast


def main():
    """Ejecutar verificación completa del proyecto."""
    
    print("🎮 Chen Toka — Sinaloa Dragon - Verificación Final")
    print("=" * 60)
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    checks = [
        check_project_structure,
        check_python_syntax,
        check_requirements,
        check_json_data,
        check_documentation,
        check_build_scripts,
        check_asset_system
    ]
    
    passed = 0
    failed = 0
    
    for check in checks:
        try:
            result = check()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Error en {check.__name__}: {e}")
            failed += 1
        print()
    
    print("📊 Resumen Final:")
    print(f"✅ Verificaciones pasadas: {passed}")
    print(f"❌ Verificaciones fallidas: {failed}")
    print(f"📈 Porcentaje de éxito: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ¡Proyecto listo para distribución!")
        return True
    else:
        print(f"\n⚠️  Proyecto tiene {failed} problemas que necesitan atención.")
        return False


def check_project_structure():
    """Verificar estructura completa del proyecto."""
    print("📁 Verificando estructura del proyecto...")
    
    required_files = [
        'README.md',
        'requirements.txt',
        'LICENSE',
        'setup.cfg',
        '.gitignore',
        'build_exe.py',
        'run_game.py',
        'run_tests.py'
    ]
    
    src_files = [
        'src/main.py',
        'src/game.py', 
        'src/settings.py',
        'src/assets.py',
        'src/input.py',
        'src/player.py',
        'src/enemies.py',
        'src/physics.py',
        'src/combat.py',
        'src/ai.py',
        'src/hud.py',
        'src/menus.py',
        'src/loader.py',
        'src/hazards.py',
        'src/save_system.py',
        'src/config.py',
        'src/generate_assets.py'
    ]
    
    data_files = [
        'data/levels/cdmx_centro.json',
        'data/levels/guadalajara_centro.json',
        'data/levels/oaxaca_monte.json'
    ]
    
    test_files = [
        'tests/test_unit.py',
        'tests/test_basic.py',
        'tests/conftest.py'
    ]
    
    all_files = required_files + src_files + data_files + test_files
    missing_files = []
    
    for file_path in all_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Archivos faltantes ({len(missing_files)}):")
        for file in missing_files:
            print(f"  - {file}")
        return False
    else:
        print(f"✅ Estructura completa ({len(all_files)} archivos)")
        return True


def check_python_syntax():
    """Verificar sintaxis de todos los archivos Python."""
    print("🐍 Verificando sintaxis Python...")
    
    python_files = []
    
    # Recopilar archivos Python
    for root, dirs, files in os.walk('.'):
        # Ignorar directorios virtuales y build
        if any(ignore in root for ignore in ['.venv', 'venv', 'build', 'dist', '__pycache__']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    syntax_errors = []
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                ast.parse(content)
        except SyntaxError as e:
            syntax_errors.append(f"{py_file}: línea {e.lineno}: {e.msg}")
        except Exception as e:
            syntax_errors.append(f"{py_file}: {e}")
    
    if syntax_errors:
        print(f"❌ Errores de sintaxis ({len(syntax_errors)}):")
        for error in syntax_errors:
            print(f"  - {error}")
        return False
    else:
        print(f"✅ Sintaxis correcta ({len(python_files)} archivos)")
        return True


def check_requirements():
    """Verificar archivo requirements.txt."""
    print("📦 Verificando requirements.txt...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt no existe")
        return False
    
    with open('requirements.txt', 'r') as f:
        requirements = f.read().strip().split('\n')
    
    required_packages = ['pygame-ce', 'pygame', 'pyinstaller']
    missing_packages = []
    
    req_text = '\n'.join(requirements).lower()
    
    for package in required_packages:
        if package.lower() not in req_text:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Paquetes faltantes en requirements.txt: {missing_packages}")
        return False
    else:
        print(f"✅ Dependencias correctas ({len(requirements)} paquetes)")
        return True


def check_json_data():
    """Verificar archivos JSON de datos."""
    print("📄 Verificando archivos JSON...")
    
    json_files = []
    
    for root, dirs, files in os.walk('data'):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    
    if not json_files:
        print("⚠️  No se encontraron archivos JSON en data/")
        return True
    
    json_errors = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Verificaciones específicas para niveles
            if 'levels' in json_file:
                required_keys = ['name', 'platforms', 'collectibles', 'enemies', 'spawn_point']
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    json_errors.append(f"{json_file}: claves faltantes: {missing_keys}")
                    
        except json.JSONDecodeError as e:
            json_errors.append(f"{json_file}: JSON inválido: {e}")
        except Exception as e:
            json_errors.append(f"{json_file}: error: {e}")
    
    if json_errors:
        print(f"❌ Errores en JSON ({len(json_errors)}):")
        for error in json_errors:
            print(f"  - {error}")
        return False
    else:
        print(f"✅ Archivos JSON válidos ({len(json_files)} archivos)")
        return True


def check_documentation():
    """Verificar documentación."""
    print("📚 Verificando documentación...")
    
    # Verificar README.md
    if not os.path.exists('README.md'):
        print("❌ README.md no existe")
        return False
    
    with open('README.md', 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    required_sections = [
        'Chen Toka',
        'Sinaloa Dragon',
        'Instalación',
        'Controles',
        'Características',
        'pygame'
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in readme_content:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ Secciones faltantes en README: {missing_sections}")
        return False
    
    # Verificar LICENSE
    if not os.path.exists('LICENSE'):
        print("❌ LICENSE no existe")
        return False
    
    print("✅ Documentación completa")
    return True


def check_build_scripts():
    """Verificar scripts de build."""
    print("🔨 Verificando scripts de build...")
    
    build_scripts = ['build_exe.py', 'run_game.py', 'run_tests.py']
    
    for script in build_scripts:
        if not os.path.exists(script):
            print(f"❌ Script faltante: {script}")
            return False
        
        # Verificar que se puede parsear
        try:
            with open(script, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
        except SyntaxError:
            print(f"❌ Error de sintaxis en {script}")
            return False
    
    print("✅ Scripts de build correctos")
    return True


def check_asset_system():
    """Verificar sistema de assets."""
    print("🎨 Verificando sistema de assets...")
    
    # Verificar que assets.py existe y contiene funciones necesarias
    assets_file = 'src/assets.py'
    if not os.path.exists(assets_file):
        print("❌ src/assets.py no existe")
        return False
    
    with open(assets_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_elements = [
        'class AssetManager',
        'def get_sprite',
        'def get_sound',
        'base64',
        '_embedded_assets'
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Elementos faltantes en assets.py: {missing_elements}")
        return False
    
    # Verificar generate_assets.py
    gen_assets_file = 'src/generate_assets.py'
    if os.path.exists(gen_assets_file):
        try:
            with open(gen_assets_file, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
            print("✅ Sistema de assets completo (con generador)")
        except SyntaxError:
            print("⚠️  generate_assets.py tiene errores de sintaxis")
            return False
    else:
        print("✅ Sistema de assets básico")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)