"""
Administrador de Assets para Chen Toka - Sinaloa Dragon

Este módulo maneja la carga, decodificación y gestión de todos los assets del juego,
incluyendo sprites, sonidos, música y fuentes. Soporta assets embebidos en base64
y archivos externos.
"""

import os
import sys
import pygame
import base64
import io
from typing import Dict, Optional, Any
from settings import Settings


class AssetManager:
    """
    Administrador central de todos los assets del juego.
    """
    
    def __init__(self):
        """Inicializa el administrador de assets."""
        
        self.sprites: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music: Dict[str, str] = {}  # Paths de archivos de música
        self.fonts: Dict[str, pygame.font.Font] = {}
        
        # Assets embebidos en base64 (placeholders)
        self._embedded_assets = self._create_embedded_assets()
        
        # Intentar cargar assets
        self._load_all_assets()
    
    def _create_embedded_assets(self) -> Dict[str, Dict[str, str]]:
        """
        Crea los assets embebidos en base64 como placeholders.
        
        Returns:
            Dict con todos los assets embebidos organizados por tipo
        """
        
        # PNG de 16x16 píxeles simple (sprite del jugador idle)
        player_idle_base64 = (
            "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz"
            "AAALYQAAC2EBqD+naQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFYSURB"
            "VDiNpZM9SwNBEIafgIWFjY2NrYWthZWtjY2lhZ2FpY2NjY2dhZ2FpY2NjY2lhZ2FpY2NjY2dhZ2F"
            "pY2NjY2lhZ2FpY2NjY2dhZ2FpY2NjY2lhZ2FpY2NjY2dhZ2FpY2NjY2lhZ2FpY2NjY2dhZ2FpY2N"
            "jY2lhZ2FpY2NjY2dhZ2FpY2NjY2lhZ2FpY2NjY2dhZ2FpY2NjY2lhQAAAABJRU5ErkJggg=="
        )
        
        # PNG simple para enemigos (16x16)
        enemy_base64 = (
            "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz"
            "AAALYQAAC2EBqD+naQAAABd0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAE5SURB"
            "VDiNrZM7SwNBEIWfBBsrwcLGxsLSwtbCxsrSwtLCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLS"
            "wtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbC"
            "xsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrS"
            "wtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbC"
            "xsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLS"
            "wtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbC"
            "xsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCxsLSwtbCxsrSwtbCAAAArklEQVQ="
        )
        
        # Tileset simple (16x16, stone/ground)
        tileset_base64 = (
            "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz"
            "AAALYQAAC2EBqD+naQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGQSURB"
            "VDiNpZQ9SwNBEIWfgFiIhY2FrYWtrY2VpY2NjY2lhZ2FpY2NjY2dhZ2FpY2NjY2lhZ2FpY2NjY2d"
            "hZ2FpY2NjY2lhZ2FpY2NjY2dhZ2FpY2NjY2lhZ2FpY2NjY2dhZ2FpY2NjY2lhZ2FpY2NjY2dhZ2F"
            "pY2NjY2lhZ2FpY2NjY2dhZ2FpY2NjY2lhZ2FpY2NjY2dhZ2FpY2NjY2lhZ2FpY2NjY2dhZ2FpY2N"
            "jY2lhZ2FpY2NjY2dhZ2FpY2NjY2lhZ2FpY2NjY2dhZ2FpY2NjY2lhQAAAABJRU5ErkJggg=="
        )
        
        # WAV básico (beep corto) - header WAV mínimo
        beep_wav_base64 = (
            "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA="
        )
        
        return {
            'sprites': {
                'player.png': player_idle_base64,
                'enemies.png': enemy_base64,
                'tileset.png': tileset_base64,
                'pickups.png': player_idle_base64  # Reutilizar por simplicidad
            },
            'backgrounds': {
                'cdmx_parallax.png': tileset_base64,
                'guadalajara_parallax.png': tileset_base64,
                'oaxaca_parallax.png': tileset_base64
            },
            'audio': {
                'hit_light.wav': beep_wav_base64,
                'hit_heavy.wav': beep_wav_base64,
                'roll.wav': beep_wav_base64,
                'parry.wav': beep_wav_base64,
                'pickup.wav': beep_wav_base64,
                'ko.wav': beep_wav_base64,
                'metro.wav': beep_wav_base64,
                'rain_loop.wav': beep_wav_base64,
                'stage_loop.ogg': beep_wav_base64,  # Placeholder para OGG
                'boss_loop.ogg': beep_wav_base64
            }
        }
    
    def _load_all_assets(self):
        """Carga todos los assets disponibles."""
        
        print("Cargando assets...")
        
        # Cargar sprites
        self._load_sprites()
        
        # Cargar sonidos
        self._load_sounds()
        
        # Cargar música
        self._load_music()
        
        # Cargar fuentes
        self._load_fonts()
        
        print(f"Assets cargados: {len(self.sprites)} sprites, {len(self.sounds)} sonidos, {len(self.music)} música")
    
    def _load_sprites(self):
        """Carga todos los sprites desde archivos o base64."""
        
        sprite_categories = ['sprites', 'backgrounds']
        
        for category in sprite_categories:
            for filename, base64_data in self._embedded_assets[category].items():
                asset_name = f"{category}_{filename.replace('.png', '')}"
                
                # Intentar cargar desde archivo primero
                file_path = Settings.get_asset_path(f"{category}/{filename}")
                
                sprite = None
                
                if os.path.exists(file_path):
                    try:
                        sprite = pygame.image.load(file_path).convert_alpha()
                        print(f"Sprite cargado desde archivo: {filename}")
                    except Exception as e:
                        print(f"Error cargando sprite desde archivo {filename}: {e}")
                
                # Si no se pudo cargar desde archivo, usar base64
                if sprite is None:
                    try:
                        sprite = self._load_sprite_from_base64(base64_data)
                        print(f"Sprite cargado desde base64: {filename}")
                    except Exception as e:
                        print(f"Error cargando sprite desde base64 {filename}: {e}")
                        # Crear sprite de fallback
                        sprite = self._create_fallback_sprite()
                
                if sprite:
                    self.sprites[asset_name] = sprite
    
    def _load_sounds(self):
        """Carga todos los sonidos desde archivos o base64."""
        
        for filename, base64_data in self._embedded_assets['audio'].items():
            if filename.endswith('.wav'):
                asset_name = f"sfx_{filename.replace('.wav', '')}"
                
                # Intentar cargar desde archivo primero
                file_path = Settings.get_asset_path(f"audio/sfx/{filename}")
                
                sound = None
                
                if os.path.exists(file_path):
                    try:
                        sound = pygame.mixer.Sound(file_path)
                        print(f"Sonido cargado desde archivo: {filename}")
                    except Exception as e:
                        print(f"Error cargando sonido desde archivo {filename}: {e}")
                
                # Si no se pudo cargar desde archivo, usar base64
                if sound is None:
                    try:
                        sound = self._load_sound_from_base64(base64_data)
                        print(f"Sonido cargado desde base64: {filename}")
                    except Exception as e:
                        print(f"Error cargando sonido desde base64 {filename}: {e}")
                        # Crear sonido silencioso de fallback
                        sound = self._create_fallback_sound()
                
                if sound:
                    self.sounds[asset_name] = sound
    
    def _load_music(self):
        """Carga referencias a archivos de música."""
        
        for filename in self._embedded_assets['audio'].keys():
            if filename.endswith('.ogg'):
                asset_name = f"music_{filename.replace('.ogg', '')}"
                
                # Buscar archivo en disco
                file_path = Settings.get_asset_path(f"audio/music/{filename}")
                
                if os.path.exists(file_path):
                    self.music[asset_name] = file_path
                    print(f"Música encontrada: {filename}")
                else:
                    # Para música, no podemos crear fácilmente desde base64
                    # Simplemente registrar como no disponible
                    self.music[asset_name] = None
                    print(f"Música no disponible: {filename}")
    
    def _load_fonts(self):
        """Carga fuentes del sistema o embebidas."""
        
        # Intentar cargar fuente personalizada
        font_path = Settings.get_asset_path("fonts/pixel.ttf")
        
        if os.path.exists(font_path):
            try:
                self.fonts['pixel_small'] = pygame.font.Font(font_path, 12)
                self.fonts['pixel_medium'] = pygame.font.Font(font_path, 16)
                self.fonts['pixel_large'] = pygame.font.Font(font_path, 24)
                print("Fuente personalizada cargada: pixel.ttf")
            except Exception as e:
                print(f"Error cargando fuente personalizada: {e}")
                self._load_default_fonts()
        else:
            print("Fuente personalizada no encontrada, usando fuente del sistema")
            self._load_default_fonts()
    
    def _load_default_fonts(self):
        """Carga fuentes por defecto del sistema."""
        
        try:
            self.fonts['pixel_small'] = pygame.font.Font(None, 16)
            self.fonts['pixel_medium'] = pygame.font.Font(None, 24)
            self.fonts['pixel_large'] = pygame.font.Font(None, 32)
        except Exception as e:
            print(f"Error cargando fuentes del sistema: {e}")
    
    def _load_sprite_from_base64(self, base64_data: str) -> pygame.Surface:
        """
        Carga un sprite desde datos base64.
        
        Args:
            base64_data: String con datos base64 de la imagen
            
        Returns:
            Surface de pygame con la imagen cargada
        """
        
        # Decodificar base64
        image_data = base64.b64decode(base64_data)
        
        # Crear surface desde datos
        image_file = io.BytesIO(image_data)
        surface = pygame.image.load(image_file).convert_alpha()
        
        return surface
    
    def _load_sound_from_base64(self, base64_data: str) -> pygame.mixer.Sound:
        """
        Carga un sonido desde datos base64.
        
        Args:
            base64_data: String con datos base64 del audio
            
        Returns:
            Sound de pygame con el audio cargado
        """
        
        # Decodificar base64
        audio_data = base64.b64decode(base64_data)
        
        # Crear sound desde datos
        audio_file = io.BytesIO(audio_data)
        sound = pygame.mixer.Sound(audio_file)
        
        return sound
    
    def _create_fallback_sprite(self, width: int = 16, height: int = 16) -> pygame.Surface:
        """
        Crea un sprite de fallback cuando falla la carga.
        
        Args:
            width: Ancho del sprite
            height: Alto del sprite
            
        Returns:
            Surface con un rectángulo de color
        """
        
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(Settings.COLOR_PURPLE)  # Color distintivo para fallback
        return surface
    
    def _create_fallback_sound(self) -> pygame.mixer.Sound:
        """
        Crea un sonido de fallback silencioso.
        
        Returns:
            Sound silencioso de pygame
        """
        
        # Crear un buffer silencioso muy corto
        silence_array = pygame.sndarray.make_sound(
            pygame.array.array('i', [0] * 1000)  # 1000 samples de silencio
        )
        return silence_array
    
    # === MÉTODOS PÚBLICOS PARA ACCEDER A ASSETS ===
    
    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """
        Obtiene un sprite por nombre.
        
        Args:
            name: Nombre del sprite (ej: "sprites_player", "backgrounds_cdmx_parallax")
            
        Returns:
            Surface del sprite o None si no existe
        """
        
        return self.sprites.get(name)
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """
        Obtiene un sonido por nombre.
        
        Args:
            name: Nombre del sonido (ej: "sfx_hit_light", "sfx_parry")
            
        Returns:
            Sound del sonido o None si no existe
        """
        
        return self.sounds.get(name)
    
    def get_font(self, size: str = 'medium') -> pygame.font.Font:
        """
        Obtiene una fuente por tamaño.
        
        Args:
            size: Tamaño de la fuente ('small', 'medium', 'large')
            
        Returns:
            Font de pygame
        """
        
        font_name = f'pixel_{size}'
        return self.fonts.get(font_name, pygame.font.Font(None, 24))
    
    def play_sound(self, name: str, volume: float = 1.0):
        """
        Reproduce un sonido.
        
        Args:
            name: Nombre del sonido
            volume: Volumen de reproducción (0.0 - 1.0)
        """
        
        sound = self.get_sound(name)
        if sound:
            try:
                sound.set_volume(volume)
                sound.play()
            except Exception as e:
                print(f"Error reproduciendo sonido {name}: {e}")
    
    def play_music(self, name: str, loop: bool = True, volume: float = 0.6):
        """
        Reproduce música de fondo.
        
        Args:
            name: Nombre de la música
            loop: Si debe reproducirse en bucle
            volume: Volumen de reproducción (0.0 - 1.0)
        """
        
        music_path = self.music.get(name)
        if music_path:
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1 if loop else 0)
                print(f"Reproduciendo música: {name}")
            except Exception as e:
                print(f"Error reproduciendo música {name}: {e}")
        else:
            print(f"Música no encontrada: {name}")
    
    def stop_music(self):
        """Detiene la música actual."""
        
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Error deteniendo música: {e}")
    
    def create_scaled_sprite(self, name: str, scale: int) -> Optional[pygame.Surface]:
        """
        Crea una versión escalada de un sprite.
        
        Args:
            name: Nombre del sprite original
            scale: Factor de escala (entero)
            
        Returns:
            Surface escalada o None si no existe el sprite original
        """
        
        original = self.get_sprite(name)
        if original:
            new_size = (original.get_width() * scale, original.get_height() * scale)
            return pygame.transform.scale(original, new_size)
        return None
    
    def create_colored_sprite(self, name: str, color: tuple) -> Optional[pygame.Surface]:
        """
        Crea una versión recoloreada de un sprite.
        
        Args:
            name: Nombre del sprite original
            color: Color de reemplazo (R, G, B)
            
        Returns:
            Surface recoloreada o None si no existe el sprite original
        """
        
        original = self.get_sprite(name)
        if original:
            colored = original.copy()
            colored.fill(color, special_flags=pygame.BLEND_MULT)
            return colored
        return None