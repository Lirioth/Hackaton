"""
Configuración de pytest para el proyecto Chen Toka — Sinaloa Dragon.
"""

import pytest
import sys
import os

# Agregar src al path para todos los tests
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def pytest_configure(config):
    """Configuración inicial de pytest."""
    # Configurar markers personalizados
    config.addinivalue_line("markers", "slow: marca tests como lentos")
    config.addinivalue_line("markers", "integration: tests de integración")
    config.addinivalue_line("markers", "unit: tests unitarios")
    config.addinivalue_line("markers", "pygame: tests que requieren pygame")
    

@pytest.fixture(scope="session")
def pygame_init():
    """Fixture para inicializar pygame una vez por sesión de tests."""
    try:
        import pygame
        pygame.init()
        pygame.display.set_mode((1, 1))  # Ventana mínima para tests
        yield pygame
    except ImportError:
        pytest.skip("pygame no está disponible")
    finally:
        try:
            pygame.quit()
        except:
            pass


@pytest.fixture
def project_root():
    """Fixture que retorna la ruta del directorio raíz del proyecto."""
    return os.path.join(os.path.dirname(__file__), '..')


@pytest.fixture
def src_path():
    """Fixture que retorna la ruta del directorio src."""
    return os.path.join(os.path.dirname(__file__), '..', 'src')


@pytest.fixture
def data_path():
    """Fixture que retorna la ruta del directorio data."""
    return os.path.join(os.path.dirname(__file__), '..', 'data')


@pytest.fixture
def assets_path():
    """Fixture que retorna la ruta del directorio assets."""
    return os.path.join(os.path.dirname(__file__), '..', 'assets')


def pytest_collection_modifyitems(config, items):
    """Modificar la colección de tests para agregar markers automáticamente."""
    for item in items:
        # Marcar tests que requieren pygame
        if "pygame" in item.nodeid.lower() or any("pygame" in str(mark) for mark in item.iter_markers()):
            item.add_marker(pytest.mark.pygame)
        
        # Marcar tests lentos
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Marcar tests de integración vs unitarios
        if "integration" in item.nodeid.lower() or "test_basic.py" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_unit.py" in item.nodeid:
            item.add_marker(pytest.mark.unit)


def pytest_runtest_setup(item):
    """Configuración antes de ejecutar cada test."""
    # Saltar tests de pygame si no está disponible
    if "pygame" in [mark.name for mark in item.iter_markers()]:
        try:
            import pygame
        except ImportError:
            pytest.skip("pygame no está disponible")


def pytest_report_header(config):
    """Información adicional en el header del reporte."""
    return [
        "Chen Toka — Sinaloa Dragon Test Suite",
        f"Python: {sys.version}",
        f"Platform: {sys.platform}",
    ]