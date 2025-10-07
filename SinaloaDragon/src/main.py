"""
Chen Toka - Sinaloa Dragon
Punto de entrada principal del juego

Este módulo inicializa pygame, configura la ventana y ejecuta el bucle principal del juego.
"""

import sys
import os
import traceback
import pygame

# Añadir el directorio src al path para importaciones
if hasattr(sys, '_MEIPASS'):
    # Ejecutándose desde PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Ejecutándose desde fuente
    base_path = os.path.dirname(os.path.abspath(__file__))
    
# Asegurar que podemos importar desde src
src_path = os.path.dirname(os.path.abspath(__file__))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from game import Game
    from settings import Settings
except ImportError as e:
    print(f"Error importando módulos del juego: {e}")
    print("Asegúrate de que todos los archivos estén presentes")
    input("Presiona Enter para salir...")
    sys.exit(1)


def main():
    """
    Función principal que inicializa y ejecuta el juego.
    
    Maneja la configuración inicial de pygame, la creación de la ventana
    y el bucle principal del juego.
    """
    try:
        # Inicializar pygame
        pygame.init()
        
        # Intentar inicializar el mixer de audio (puede fallar sin dispositivos de audio)
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("Audio inicializado correctamente")
        except pygame.error as e:
            print(f"Advertencia: No se pudo inicializar el audio: {e}")
            print("El juego continuará sin sonido")
        
        # Configurar la ventana
        pygame.display.set_caption("Chen Toka - Sinaloa Dragon")
        
        # Intentar cargar el icono si existe
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, 'assets', 'icon.ico')
            else:
                icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.ico')
            
            if os.path.exists(icon_path):
                # pygame no puede cargar .ico directamente, necesitaríamos convertir o usar .png
                pass
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")
        
        # Crear la pantalla con la resolución de ventana
        screen = pygame.display.set_mode((Settings.WINDOW_WIDTH, Settings.WINDOW_HEIGHT))
        
        # Crear la superficie de renderizado interno (resolución del juego)
        game_surface = pygame.Surface((Settings.GAME_WIDTH, Settings.GAME_HEIGHT))
        
        # Crear el reloj para controlar FPS
        clock = pygame.time.Clock()
        
        # Crear e inicializar el objeto del juego
        game = Game(game_surface)
        
        print(f"Chen Toka iniciado - Resolución: {Settings.GAME_WIDTH}x{Settings.GAME_HEIGHT} -> {Settings.WINDOW_WIDTH}x{Settings.WINDOW_HEIGHT}")
        print("Controles: WASD/Flechas=Mover, Espacio=Saltar, J=Ataque ligero, K=Ataque pesado, L=Roll, Shift=Parry, Esc=Pausa")
        
        # Bucle principal del juego
        running = True
        dt = 0
        
        while running:
            # Calcular delta time en segundos
            dt = clock.tick(Settings.TARGET_FPS) / 1000.0
            
            # Limitar el delta time para evitar saltos grandes
            dt = min(dt, 1.0 / Settings.TARGET_FPS * 2)
            
            # Manejar eventos de pygame
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    break
            
            if not running:
                break
            
            # Actualizar el juego
            if not game.update(dt, events):
                running = False
                break
            
            # Limpiar la superficie del juego
            game_surface.fill((0, 0, 0))
            
            # Renderizar el juego
            game.render(game_surface)
            
            # Escalar la superficie del juego a la ventana
            scaled_surface = pygame.transform.scale(game_surface, (Settings.WINDOW_WIDTH, Settings.WINDOW_HEIGHT))
            screen.blit(scaled_surface, (0, 0))
            
            # Actualizar la pantalla
            pygame.display.flip()
        
        print("Cerrando Chen Toka...")
        
        # Guardar configuración antes de salir
        game.shutdown()
        
    except Exception as e:
        print(f"Error crítico en el juego: {e}")
        print("Traceback completo:")
        traceback.print_exc()
        input("Presiona Enter para salir...")
        return 1
    
    finally:
        # Asegurar que pygame se cierre correctamente
        try:
            pygame.quit()
        except:
            pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main())