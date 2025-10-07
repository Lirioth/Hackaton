"""
Generador de Assets Placeholder con Base64 para Chen Toka - Sinaloa Dragon

Este módulo genera todos los assets placeholder embebidos como datos base64
para sprites, backgrounds, audio y fuentes del juego.
"""

import base64
import io
from PIL import Image, ImageDraw, ImageFont
import wave
import numpy as np
from typing import Dict, Tuple


class AssetGenerator:
    """Generador de assets placeholder embebidos."""
    
    def __init__(self):
        """Inicializa el generador de assets."""
        print("Generador de assets placeholder inicializado")
    
    def generate_all_assets(self) -> Dict[str, str]:
        """
        Genera todos los assets placeholder como base64.
        
        Returns:
            Diccionario con todos los assets en base64
        """
        
        assets = {}
        
        # Generar sprites
        assets.update(self._generate_sprites())
        
        # Generar backgrounds
        assets.update(self._generate_backgrounds())
        
        # Generar audio
        assets.update(self._generate_audio())
        
        # Generar fuentes
        assets.update(self._generate_fonts())
        
        print(f"Generados {len(assets)} assets placeholder")
        return assets
    
    def _generate_sprites(self) -> Dict[str, str]:
        """Genera sprites placeholder para personajes y objetos."""
        
        sprites = {}
        
        # Sprites del jugador Chen Toka
        sprites['player_idle'] = self._create_player_sprite(16, 16, "idle")
        sprites['player_run_1'] = self._create_player_sprite(16, 16, "run1")
        sprites['player_run_2'] = self._create_player_sprite(16, 16, "run2")
        sprites['player_jump'] = self._create_player_sprite(16, 16, "jump")
        sprites['player_attack_1'] = self._create_player_sprite(16, 16, "attack1")
        sprites['player_attack_2'] = self._create_player_sprite(16, 16, "attack2")
        sprites['player_roll'] = self._create_player_sprite(16, 16, "roll")
        sprites['player_parry'] = self._create_player_sprite(16, 16, "parry")
        sprites['player_hurt'] = self._create_player_sprite(16, 16, "hurt")
        sprites['player_ko'] = self._create_player_sprite(16, 16, "ko")
        
        # Sprites de enemigos
        sprites['enemy_maton_idle'] = self._create_enemy_sprite(16, 16, "maton", "idle")
        sprites['enemy_maton_walk'] = self._create_enemy_sprite(16, 16, "maton", "walk")
        sprites['enemy_maton_attack'] = self._create_enemy_sprite(16, 16, "maton", "attack")
        sprites['enemy_chacal_idle'] = self._create_enemy_sprite(16, 16, "chacal", "idle")
        sprites['enemy_chacal_run'] = self._create_enemy_sprite(16, 16, "chacal", "run")
        sprites['enemy_chacal_pounce'] = self._create_enemy_sprite(16, 16, "chacal", "pounce")
        sprites['enemy_luchador_idle'] = self._create_enemy_sprite(20, 20, "luchador", "idle")
        sprites['enemy_luchador_charge'] = self._create_enemy_sprite(20, 20, "luchador", "charge")
        sprites['enemy_luchador_grab'] = self._create_enemy_sprite(20, 20, "luchador", "grab")
        sprites['enemy_drone_idle'] = self._create_enemy_sprite(12, 12, "drone", "idle")
        sprites['enemy_drone_shoot'] = self._create_enemy_sprite(12, 12, "drone", "shoot")
        
        # Objetos coleccionables
        sprites['coin_aztec'] = self._create_collectible_sprite(8, 8, "aztec")
        sprites['coin_tequila'] = self._create_collectible_sprite(8, 8, "tequila")
        sprites['coin_jade'] = self._create_collectible_sprite(8, 8, "jade")
        sprites['heart_life'] = self._create_collectible_sprite(8, 8, "heart")
        sprites['powerup_speed'] = self._create_collectible_sprite(8, 8, "speed")
        sprites['powerup_jump'] = self._create_collectible_sprite(8, 8, "jump")
        sprites['powerup_strength'] = self._create_collectible_sprite(8, 8, "strength")
        
        # Elementos de mundo
        sprites['platform_stone'] = self._create_platform_sprite(32, 16, "stone")
        sprites['platform_wood'] = self._create_platform_sprite(32, 16, "wood")
        sprites['platform_metal'] = self._create_platform_sprite(32, 16, "metal")
        sprites['spikes_up'] = self._create_hazard_sprite(16, 16, "spikes_up")
        sprites['spikes_down'] = self._create_hazard_sprite(16, 16, "spikes_down")
        sprites['lava_surface'] = self._create_hazard_sprite(16, 16, "lava")
        
        # Efectos visuales
        sprites['hit_effect_1'] = self._create_effect_sprite(12, 12, "hit1")
        sprites['hit_effect_2'] = self._create_effect_sprite(12, 12, "hit2")
        sprites['dust_cloud'] = self._create_effect_sprite(10, 8, "dust")
        sprites['parry_spark'] = self._create_effect_sprite(8, 8, "spark")
        
        # Proyectiles
        sprites['projectile_bullet'] = self._create_projectile_sprite(4, 4, "bullet")
        sprites['projectile_fireball'] = self._create_projectile_sprite(6, 6, "fireball")
        
        return sprites
    
    def _create_player_sprite(self, width: int, height: int, pose: str) -> str:
        """Crea sprite del jugador según la pose."""
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Colores del jugador (Chen Toka)
        skin_color = (222, 184, 135)  # Piel
        shirt_color = (34, 139, 34)   # Verde Sinaloa
        pants_color = (25, 25, 112)   # Azul marino
        hair_color = (54, 54, 54)     # Cabello negro
        
        if pose == "idle":
            # Cabeza
            draw.ellipse([5, 2, 11, 8], fill=skin_color)
            # Cabello
            draw.ellipse([4, 1, 12, 6], fill=hair_color)
            # Cuerpo
            draw.rectangle([6, 8, 10, 13], fill=shirt_color)
            # Piernas
            draw.rectangle([6, 13, 8, 16], fill=pants_color)
            draw.rectangle([8, 13, 10, 16], fill=pants_color)
            
        elif pose in ["run1", "run2"]:
            # Pose de correr con ligera inclinación
            draw.ellipse([6, 2, 12, 8], fill=skin_color)
            draw.ellipse([5, 1, 13, 6], fill=hair_color)
            draw.rectangle([7, 8, 11, 13], fill=shirt_color)
            
            if pose == "run1":
                draw.rectangle([6, 13, 8, 16], fill=pants_color)
                draw.rectangle([9, 13, 11, 16], fill=pants_color)
            else:
                draw.rectangle([7, 13, 9, 16], fill=pants_color)
                draw.rectangle([8, 13, 10, 16], fill=pants_color)
                
        elif pose == "jump":
            # Pose de salto - brazos arriba
            draw.ellipse([6, 1, 12, 7], fill=skin_color)
            draw.ellipse([5, 0, 13, 5], fill=hair_color)
            draw.rectangle([7, 7, 11, 12], fill=shirt_color)
            draw.rectangle([7, 12, 9, 15], fill=pants_color)
            draw.rectangle([8, 12, 10, 15], fill=pants_color)
            # Brazos arriba
            draw.rectangle([4, 6, 6, 10], fill=skin_color)
            draw.rectangle([11, 6, 13, 10], fill=skin_color)
            
        elif pose in ["attack1", "attack2"]:
            # Poses de ataque
            draw.ellipse([5, 2, 11, 8], fill=skin_color)
            draw.ellipse([4, 1, 12, 6], fill=hair_color)
            draw.rectangle([6, 8, 10, 13], fill=shirt_color)
            draw.rectangle([6, 13, 8, 16], fill=pants_color)
            draw.rectangle([8, 13, 10, 16], fill=pants_color)
            
            # Brazo extendido atacando
            if pose == "attack1":
                draw.rectangle([11, 8, 15, 10], fill=skin_color)
            else:
                draw.rectangle([1, 8, 5, 10], fill=skin_color)
                
        elif pose == "roll":
            # Pose enrollada
            draw.ellipse([3, 6, 13, 12], fill=shirt_color)
            draw.arc([4, 5, 12, 13], 0, 180, fill=skin_color)
            
        elif pose == "parry":
            # Pose defensiva
            draw.ellipse([5, 2, 11, 8], fill=skin_color)
            draw.ellipse([4, 1, 12, 6], fill=hair_color)
            draw.rectangle([6, 8, 10, 13], fill=shirt_color)
            draw.rectangle([6, 13, 8, 16], fill=pants_color)
            draw.rectangle([8, 13, 10, 16], fill=pants_color)
            # Brazos cruzados
            draw.rectangle([3, 9, 7, 11], fill=skin_color)
            draw.rectangle([9, 9, 13, 11], fill=skin_color)
        
        return self._image_to_base64(img)
    
    def _create_enemy_sprite(self, width: int, height: int, enemy_type: str, pose: str) -> str:
        """Crea sprite de enemigo según tipo y pose."""
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if enemy_type == "maton":
            # Matón - Criminal básico
            body_color = (139, 69, 19)    # Marrón
            clothes_color = (64, 64, 64)  # Gris oscuro
            
            if pose == "idle":
                draw.ellipse([5, 2, 11, 8], fill=(205, 133, 63))  # Cabeza
                draw.rectangle([6, 8, 10, 13], fill=clothes_color)
                draw.rectangle([6, 13, 8, 16], fill=body_color)
                draw.rectangle([8, 13, 10, 16], fill=body_color)
                
        elif enemy_type == "chacal":
            # Chacal - Enemigo rápido
            fur_color = (160, 82, 45)     # Pelaje
            accent_color = (255, 140, 0)  # Naranja
            
            if pose == "idle":
                draw.ellipse([4, 3, 12, 9], fill=fur_color)     # Cabeza
                draw.ellipse([6, 7, 10, 12], fill=fur_color)    # Cuerpo
                draw.rectangle([4, 11, 6, 14], fill=fur_color)  # Patas
                draw.rectangle([10, 11, 12, 14], fill=fur_color)
                # Detalles
                draw.ellipse([6, 4, 8, 6], fill=accent_color)
                draw.ellipse([8, 4, 10, 6], fill=accent_color)
                
        elif enemy_type == "luchador":
            # Luchador - Enemigo fuerte
            skin_color = (222, 184, 135)
            mask_color = (255, 0, 0)      # Máscara roja
            
            if pose == "idle":
                draw.ellipse([6, 2, 14, 10], fill=skin_color)   # Cabeza grande
                draw.ellipse([5, 1, 15, 9], fill=mask_color)    # Máscara
                draw.rectangle([7, 10, 13, 16], fill=(255, 215, 0))  # Torso dorado
                draw.rectangle([6, 16, 8, 20], fill=skin_color) # Piernas
                draw.rectangle([12, 16, 14, 20], fill=skin_color)
                
        elif enemy_type == "drone":
            # Drone - Enemigo volador
            metal_color = (169, 169, 169)
            light_color = (255, 0, 0)     # Luz roja
            
            if pose == "idle":
                draw.ellipse([3, 4, 9, 8], fill=metal_color)    # Cuerpo
                draw.rectangle([1, 5, 3, 7], fill=metal_color)  # Rotor izq
                draw.rectangle([9, 5, 11, 7], fill=metal_color) # Rotor der
                draw.ellipse([5, 5, 7, 7], fill=light_color)   # Luz central
        
        return self._image_to_base64(img)
    
    def _create_collectible_sprite(self, width: int, height: int, item_type: str) -> str:
        """Crea sprite de objeto coleccionable."""
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if item_type == "aztec":
            # Moneda azteca - dorada con símbolo
            draw.ellipse([1, 1, 7, 7], fill=(255, 215, 0))
            draw.ellipse([2, 2, 6, 6], fill=(218, 165, 32))
            draw.line([3, 3, 5, 5], fill=(184, 134, 11), width=1)
            
        elif item_type == "tequila":
            # Tequila dorada - botella
            draw.rectangle([3, 1, 5, 7], fill=(255, 140, 0))
            draw.rectangle([2, 2, 6, 6], fill=(255, 165, 0))
            draw.rectangle([3, 0, 5, 2], fill=(139, 69, 19))
            
        elif item_type == "jade":
            # Jade zapoteca - verde
            draw.ellipse([1, 1, 7, 7], fill=(0, 100, 0))
            draw.ellipse([2, 2, 6, 6], fill=(34, 139, 34))
            draw.ellipse([3, 3, 5, 5], fill=(50, 205, 50))
            
        elif item_type == "heart":
            # Corazón de vida
            draw.ellipse([1, 2, 4, 5], fill=(255, 0, 0))
            draw.ellipse([4, 2, 7, 5], fill=(255, 0, 0))
            draw.polygon([(1, 4), (4, 7), (7, 4)], fill=(255, 0, 0))
            
        elif item_type == "speed":
            # Power-up de velocidad - rayo
            draw.polygon([(2, 1), (6, 3), (4, 4), (6, 7), (2, 5), (4, 4)], fill=(255, 255, 0))
            
        elif item_type == "jump":
            # Power-up de salto - flecha arriba
            draw.polygon([(4, 1), (1, 4), (3, 4), (3, 7), (5, 7), (5, 4), (7, 4)], fill=(0, 255, 255))
            
        elif item_type == "strength":
            # Power-up de fuerza - puño
            draw.ellipse([2, 2, 6, 6], fill=(222, 184, 135))
            draw.rectangle([3, 4, 5, 7], fill=(222, 184, 135))
        
        return self._image_to_base64(img)
    
    def _create_platform_sprite(self, width: int, height: int, material: str) -> str:
        """Crea sprite de plataforma."""
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if material == "stone":
            # Plataforma de piedra
            base_color = (128, 128, 128)
            highlight = (169, 169, 169)
            shadow = (105, 105, 105)
            
            draw.rectangle([0, 0, width, height], fill=base_color)
            draw.rectangle([0, 0, width, 2], fill=highlight)
            draw.rectangle([0, height-2, width, height], fill=shadow)
            
            # Detalles de piedra
            for i in range(0, width, 8):
                draw.line([i, 2, i, height-2], fill=shadow)
                
        elif material == "wood":
            # Plataforma de madera
            base_color = (139, 69, 19)
            highlight = (160, 82, 45)
            shadow = (101, 67, 33)
            
            draw.rectangle([0, 0, width, height], fill=base_color)
            draw.rectangle([0, 0, width, 2], fill=highlight)
            draw.rectangle([0, height-2, width, height], fill=shadow)
            
            # Vetas de madera
            for i in range(0, width, 4):
                draw.line([i, 0, i, height], fill=shadow)
                
        elif material == "metal":
            # Plataforma metálica
            base_color = (169, 169, 169)
            highlight = (192, 192, 192)
            shadow = (128, 128, 128)
            
            draw.rectangle([0, 0, width, height], fill=base_color)
            draw.rectangle([0, 0, width, 2], fill=highlight)
            draw.rectangle([0, height-2, width, height], fill=shadow)
            
            # Remaches
            for i in range(4, width, 8):
                draw.ellipse([i-1, 4, i+1, 6], fill=shadow)
                draw.ellipse([i-1, height-6, i+1, height-4], fill=shadow)
        
        return self._image_to_base64(img)
    
    def _create_hazard_sprite(self, width: int, height: int, hazard_type: str) -> str:
        """Crea sprite de peligro."""
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if hazard_type == "spikes_up":
            # Picos hacia arriba
            base_color = (128, 128, 128)
            spike_color = (169, 169, 169)
            
            # Base
            draw.rectangle([0, height-4, width, height], fill=base_color)
            
            # Picos
            for i in range(0, width, 4):
                draw.polygon([
                    (i, height-4),
                    (i+2, 0),
                    (i+4, height-4)
                ], fill=spike_color)
                
        elif hazard_type == "spikes_down":
            # Picos hacia abajo
            base_color = (128, 128, 128)
            spike_color = (169, 169, 169)
            
            # Base
            draw.rectangle([0, 0, width, 4], fill=base_color)
            
            # Picos
            for i in range(0, width, 4):
                draw.polygon([
                    (i, 4),
                    (i+2, height),
                    (i+4, 4)
                ], fill=spike_color)
                
        elif hazard_type == "lava":
            # Superficie de lava
            lava_color = (255, 69, 0)
            bright_color = (255, 140, 0)
            
            draw.rectangle([0, 0, width, height], fill=lava_color)
            
            # Burbujas y efecto ondulado
            for i in range(0, width, 6):
                y_offset = 2 if i % 12 == 0 else 0
                draw.ellipse([i, y_offset, i+4, y_offset+4], fill=bright_color)
        
        return self._image_to_base64(img)
    
    def _create_effect_sprite(self, width: int, height: int, effect_type: str) -> str:
        """Crea sprite de efecto visual."""
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if effect_type == "hit1":
            # Efecto de golpe - estrellas
            center_x, center_y = width // 2, height // 2
            draw.polygon([
                (center_x, 1),
                (center_x+1, center_y-1),
                (width-1, center_y),
                (center_x+1, center_y+1),
                (center_x, height-1),
                (center_x-1, center_y+1),
                (1, center_y),
                (center_x-1, center_y-1)
            ], fill=(255, 255, 0))
            
        elif effect_type == "hit2":
            # Efecto de golpe - explosión
            draw.ellipse([2, 2, width-2, height-2], fill=(255, 165, 0))
            draw.ellipse([4, 4, width-4, height-4], fill=(255, 255, 0))
            
        elif effect_type == "dust":
            # Nube de polvo
            for i in range(3):
                x = 2 + i * 2
                y = 3 + (i % 2)
                draw.ellipse([x, y, x+3, y+3], fill=(205, 205, 205))
                
        elif effect_type == "spark":
            # Chispa de parry
            draw.polygon([
                (width//2, 0),
                (width//2+1, height//2),
                (width-1, height//2),
                (width//2+1, height//2+1),
                (width//2, height-1),
                (width//2-1, height//2+1),
                (0, height//2),
                (width//2-1, height//2)
            ], fill=(255, 255, 255))
        
        return self._image_to_base64(img)
    
    def _create_projectile_sprite(self, width: int, height: int, projectile_type: str) -> str:
        """Crea sprite de proyectil."""
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if projectile_type == "bullet":
            # Bala simple
            draw.ellipse([0, 0, width, height], fill=(255, 255, 0))
            draw.ellipse([1, 1, width-1, height-1], fill=(255, 215, 0))
            
        elif projectile_type == "fireball":
            # Bola de fuego
            draw.ellipse([0, 0, width, height], fill=(255, 69, 0))
            draw.ellipse([1, 1, width-1, height-1], fill=(255, 140, 0))
            draw.ellipse([2, 2, width-2, height-2], fill=(255, 255, 0))
        
        return self._image_to_base64(img)
    
    def _generate_backgrounds(self) -> Dict[str, str]:
        """Genera backgrounds de parallax para cada ciudad."""
        
        backgrounds = {}
        
        # Background CDMX - Colores de México
        backgrounds['cdmx_sky'] = self._create_gradient_bg(320, 180, 
                                                         (135, 206, 235), (255, 182, 193))
        backgrounds['cdmx_buildings'] = self._create_cityscape_bg(320, 100, 
                                                                (105, 105, 105), "modern")
        backgrounds['cdmx_foreground'] = self._create_street_bg(320, 50, (139, 69, 19))
        
        # Background Guadalajara - Colores coloniales
        backgrounds['guadalajara_sky'] = self._create_gradient_bg(320, 180, 
                                                                (255, 165, 0), (255, 140, 0))
        backgrounds['guadalajara_buildings'] = self._create_cityscape_bg(320, 100, 
                                                                       (160, 82, 45), "colonial")
        backgrounds['guadalajara_foreground'] = self._create_street_bg(320, 50, (205, 133, 63))
        
        # Background Oaxaca - Colores ancestrales
        backgrounds['oaxaca_sky'] = self._create_gradient_bg(320, 180, 
                                                           (139, 69, 19), (160, 82, 45))
        backgrounds['oaxaca_mountains'] = self._create_mountain_bg(320, 80, (101, 67, 33))
        backgrounds['oaxaca_ruins'] = self._create_ruins_bg(320, 100, (128, 128, 128))
        
        return backgrounds
    
    def _create_gradient_bg(self, width: int, height: int, 
                           start_color: Tuple[int, int, int], 
                           end_color: Tuple[int, int, int]) -> str:
        """Crea fondo con gradiente."""
        
        img = Image.new('RGB', (width, height))
        
        for y in range(height):
            # Interpolación lineal entre colores
            ratio = y / height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            
            for x in range(width):
                img.putpixel((x, y), (r, g, b))
        
        return self._image_to_base64(img)
    
    def _create_cityscape_bg(self, width: int, height: int, 
                           base_color: Tuple[int, int, int], style: str) -> str:
        """Crea silueta de ciudad."""
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Generar edificios de diferentes alturas
        building_width = 20
        for x in range(0, width, building_width):
            if style == "modern":
                building_height = 40 + (x % 3) * 20
            else:  # colonial
                building_height = 30 + (x % 4) * 15
            
            y_start = height - building_height
            
            # Edificio principal
            draw.rectangle([x, y_start, x + building_width - 2, height], 
                         fill=base_color)
            
            # Ventanas/detalles
            if style == "modern":
                for wy in range(y_start + 5, height - 5, 8):
                    for wx in range(x + 3, x + building_width - 3, 6):
                        draw.rectangle([wx, wy, wx + 2, wy + 2], 
                                     fill=(255, 255, 0))
            else:  # colonial
                # Arcos y detalles coloniales
                draw.arc([x + 3, y_start + 5, x + building_width - 5, y_start + 15], 
                        0, 180, fill=(255, 255, 255))
        
        return self._image_to_base64(img)
    
    def _create_street_bg(self, width: int, height: int, 
                         base_color: Tuple[int, int, int]) -> str:
        """Crea elementos de calle/suelo."""
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Suelo base
        draw.rectangle([0, 0, width, height], fill=base_color)
        
        # Líneas de perspectiva
        for i in range(0, width, 40):
            draw.line([i, 0, i, height], fill=(105, 105, 105))
        
        return self._image_to_base64(img)
    
    def _create_mountain_bg(self, width: int, height: int, 
                          base_color: Tuple[int, int, int]) -> str:
        """Crea silueta de montañas."""
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Crear perfil montañoso
        points = [(0, height)]
        for x in range(0, width, 20):
            y = height - 30 - (x % 40)
            points.append((x, y))
        points.append((width, height))
        
        draw.polygon(points, fill=base_color)
        
        return self._image_to_base64(img)
    
    def _create_ruins_bg(self, width: int, height: int, 
                        base_color: Tuple[int, int, int]) -> str:
        """Crea ruinas zapotecas."""
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Estructuras piramidales
        for x in range(30, width, 80):
            # Pirámide escalonada
            levels = 3
            level_height = height // levels
            level_width = 40
            
            for level in range(levels):
                y_start = height - (level + 1) * level_height
                x_start = x - level * 5
                x_end = x + level_width + level * 5
                
                draw.rectangle([x_start, y_start, x_end, height - level * level_height], 
                             fill=base_color)
        
        return self._image_to_base64(img)
    
    def _generate_audio(self) -> Dict[str, str]:
        """Genera clips de audio placeholder."""
        
        audio = {}
        
        # Generar sonidos básicos
        audio['hit_light'] = self._create_beep_audio(0.1, 800)
        audio['hit_heavy'] = self._create_beep_audio(0.2, 400)
        audio['jump'] = self._create_sweep_audio(0.15, 400, 800)
        audio['roll'] = self._create_noise_audio(0.3)
        audio['parry'] = self._create_beep_audio(0.1, 1200)
        audio['pickup_coin'] = self._create_ding_audio(0.2, 1000)
        audio['pickup_heart'] = self._create_chord_audio(0.3, [523, 659, 784])
        audio['enemy_hurt'] = self._create_beep_audio(0.15, 200)
        audio['enemy_ko'] = self._create_sweep_audio(0.5, 400, 100)
        audio['level_complete'] = self._create_victory_audio(2.0)
        audio['game_over'] = self._create_sad_audio(1.5)
        
        # Música de fondo (loops simples)
        audio['cdmx_theme'] = self._create_melody_audio(8.0, "cdmx")
        audio['guadalajara_theme'] = self._create_melody_audio(8.0, "guadalajara")
        audio['oaxaca_theme'] = self._create_melody_audio(8.0, "oaxaca")
        audio['menu_theme'] = self._create_melody_audio(4.0, "menu")
        
        return audio
    
    def _create_beep_audio(self, duration: float, frequency: int) -> str:
        """Crea un beep simple."""
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Generar onda senoidal
        audio_data = []
        for i in range(frames):
            value = np.sin(2 * np.pi * frequency * i / sample_rate)
            # Aplicar envelope para evitar clicks
            envelope = 1.0
            if i < 1000:  # Fade in
                envelope = i / 1000.0
            elif i > frames - 1000:  # Fade out
                envelope = (frames - i) / 1000.0
            
            audio_data.append(int(value * envelope * 32767))
        
        return self._audio_to_base64(audio_data, sample_rate)
    
    def _create_sweep_audio(self, duration: float, freq_start: int, freq_end: int) -> str:
        """Crea un sweep de frecuencia."""
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        audio_data = []
        for i in range(frames):
            # Interpolación lineal de frecuencia
            progress = i / frames
            frequency = freq_start + (freq_end - freq_start) * progress
            
            value = np.sin(2 * np.pi * frequency * i / sample_rate)
            envelope = 1.0 - progress * 0.5  # Decay
            
            audio_data.append(int(value * envelope * 32767))
        
        return self._audio_to_base64(audio_data, sample_rate)
    
    def _create_noise_audio(self, duration: float) -> str:
        """Crea ruido filtrado."""
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Ruido blanco filtrado
        audio_data = []
        prev_value = 0
        
        for i in range(frames):
            noise = np.random.random() * 2 - 1
            # Filtro paso bajo simple
            filtered = prev_value * 0.7 + noise * 0.3
            prev_value = filtered
            
            envelope = max(0, 1.0 - i / frames)
            audio_data.append(int(filtered * envelope * 16383))
        
        return self._audio_to_base64(audio_data, sample_rate)
    
    def _create_ding_audio(self, duration: float, frequency: int) -> str:
        """Crea un sonido de ding/campana."""
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        audio_data = []
        for i in range(frames):
            # Mezcla de frecuencias para sonido de campana
            value1 = np.sin(2 * np.pi * frequency * i / sample_rate)
            value2 = np.sin(2 * np.pi * frequency * 2 * i / sample_rate) * 0.3
            value3 = np.sin(2 * np.pi * frequency * 3 * i / sample_rate) * 0.1
            
            value = value1 + value2 + value3
            
            # Envelope exponencial
            envelope = np.exp(-i / (sample_rate * 0.3))
            
            audio_data.append(int(value * envelope * 16383))
        
        return self._audio_to_base64(audio_data, sample_rate)
    
    def _create_chord_audio(self, duration: float, frequencies: list) -> str:
        """Crea un acorde."""
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        audio_data = []
        for i in range(frames):
            value = 0
            for freq in frequencies:
                value += np.sin(2 * np.pi * freq * i / sample_rate) / len(frequencies)
            
            envelope = max(0, 1.0 - i / frames)
            audio_data.append(int(value * envelope * 20000))
        
        return self._audio_to_base64(audio_data, sample_rate)
    
    def _create_victory_audio(self, duration: float) -> str:
        """Crea melodía de victoria."""
        
        # Secuencia de notas victoriosas
        notes = [523, 659, 784, 1047]  # Do, Mi, Sol, Do octava
        note_duration = duration / len(notes)
        
        sample_rate = 22050
        total_frames = int(duration * sample_rate)
        audio_data = []
        
        for note_idx, freq in enumerate(notes):
            note_frames = int(note_duration * sample_rate)
            start_frame = note_idx * note_frames
            
            for i in range(note_frames):
                if start_frame + i >= total_frames:
                    break
                    
                value = np.sin(2 * np.pi * freq * i / sample_rate)
                envelope = 1.0 if i < note_frames * 0.8 else (note_frames - i) / (note_frames * 0.2)
                
                if len(audio_data) <= start_frame + i:
                    audio_data.extend([0] * (start_frame + i - len(audio_data) + 1))
                
                audio_data[start_frame + i] = int(value * envelope * 24000)
        
        return self._audio_to_base64(audio_data, sample_rate)
    
    def _create_sad_audio(self, duration: float) -> str:
        """Crea melodía triste para game over."""
        
        # Secuencia descendente
        notes = [523, 466, 415, 349]  # Do, La#, Sol#, Fa
        note_duration = duration / len(notes)
        
        sample_rate = 22050
        total_frames = int(duration * sample_rate)
        audio_data = []
        
        for note_idx, freq in enumerate(notes):
            note_frames = int(note_duration * sample_rate)
            start_frame = note_idx * note_frames
            
            for i in range(note_frames):
                if start_frame + i >= total_frames:
                    break
                    
                value = np.sin(2 * np.pi * freq * i / sample_rate)
                envelope = max(0, 1.0 - i / note_frames)
                
                if len(audio_data) <= start_frame + i:
                    audio_data.extend([0] * (start_frame + i - len(audio_data) + 1))
                
                audio_data[start_frame + i] = int(value * envelope * 20000)
        
        return self._audio_to_base64(audio_data, sample_rate)
    
    def _create_melody_audio(self, duration: float, theme: str) -> str:
        """Crea melodía temática para cada ciudad."""
        
        sample_rate = 22050
        
        if theme == "cdmx":
            # Melodía moderna urbana
            melody = [523, 659, 784, 659, 523, 440, 523]
        elif theme == "guadalajara":
            # Melodía estilo mariachi
            melody = [523, 523, 659, 659, 784, 659, 523]
        elif theme == "oaxaca":
            # Melodía ancestral/mística
            melody = [349, 415, 466, 415, 349, 311, 349]
        else:  # menu
            # Melodía simple de menú
            melody = [523, 659, 523, 659]
        
        note_duration = duration / len(melody)
        total_frames = int(duration * sample_rate)
        audio_data = [0] * total_frames
        
        for note_idx, freq in enumerate(melody):
            note_frames = int(note_duration * sample_rate)
            start_frame = note_idx * note_frames
            
            for i in range(note_frames):
                if start_frame + i >= total_frames:
                    break
                    
                # Onda con algo de armonía
                value = np.sin(2 * np.pi * freq * i / sample_rate)
                value += np.sin(2 * np.pi * freq * 1.5 * i / sample_rate) * 0.3
                
                # Envelope suave
                envelope = 1.0
                if i < 1000:
                    envelope = i / 1000.0
                elif i > note_frames - 1000:
                    envelope = (note_frames - i) / 1000.0
                
                audio_data[start_frame + i] = int(value * envelope * 16000)
        
        return self._audio_to_base64(audio_data, sample_rate)
    
    def _generate_fonts(self) -> Dict[str, str]:
        """Genera fuentes bitmap placeholder."""
        
        fonts = {}
        
        # Fuente básica 8x8
        fonts['font_small'] = self._create_bitmap_font(8, 8)
        
        # Fuente mediana 12x12
        fonts['font_medium'] = self._create_bitmap_font(12, 12)
        
        # Fuente grande 16x16
        fonts['font_large'] = self._create_bitmap_font(16, 16)
        
        # Fuente para números (monospace)
        fonts['font_numbers'] = self._create_number_font(12, 16)
        
        return fonts
    
    def _create_bitmap_font(self, char_width: int, char_height: int) -> str:
        """Crea fuente bitmap básica."""
        
        # Crear imagen para ASCII básico (32-126)
        chars_per_row = 16
        rows = 6  # Para cubrir ASCII básico
        
        img_width = chars_per_row * char_width
        img_height = rows * char_height
        
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Dibujar caracteres básicos como rectángulos placeholder
        for row in range(rows):
            for col in range(chars_per_row):
                char_code = 32 + row * chars_per_row + col
                if char_code > 126:
                    break
                
                x = col * char_width
                y = row * char_height
                
                # Placeholder: rectángulo blanco para caracteres visibles
                if char_code > 32:  # No dibujar espacio
                    draw.rectangle([x+1, y+1, x+char_width-1, y+char_height-1], 
                                 outline=(255, 255, 255), width=1)
                    
                    # Agregar algunos píxeles internos para simular letra
                    if char_width >= 8:
                        draw.rectangle([x+2, y+3, x+char_width-2, y+5], 
                                     fill=(255, 255, 255))
                        draw.rectangle([x+2, y+char_height//2, x+char_width-2, y+char_height//2+1], 
                                     fill=(255, 255, 255))
        
        return self._image_to_base64(img)
    
    def _create_number_font(self, char_width: int, char_height: int) -> str:
        """Crea fuente específica para números."""
        
        img = Image.new('RGBA', (char_width * 10, char_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Dibujar dígitos 0-9 como rectángulos simples
        for digit in range(10):
            x = digit * char_width
            
            # Marco del número
            draw.rectangle([x+1, 1, x+char_width-1, char_height-1], 
                         outline=(255, 255, 255), width=1)
            
            # Patrones únicos para cada dígito
            if digit in [0, 6, 8, 9]:
                # Números con "agujero"
                draw.rectangle([x+3, 3, x+char_width-3, char_height//2], 
                             outline=(255, 255, 255))
            else:
                # Números sólidos
                draw.rectangle([x+2, 3, x+char_width-2, char_height//2], 
                             fill=(255, 255, 255))
        
        return self._image_to_base64(img)
    
    def _image_to_base64(self, img: Image.Image) -> str:
        """Convierte imagen PIL a base64."""
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def _audio_to_base64(self, audio_data: list, sample_rate: int) -> str:
        """Convierte datos de audio a WAV base64."""
        
        buffer = io.BytesIO()
        
        # Crear archivo WAV
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Convertir a bytes
            audio_bytes = b''
            for sample in audio_data:
                # Clampear valores
                sample = max(-32768, min(32767, int(sample)))
                audio_bytes += sample.to_bytes(2, byteorder='little', signed=True)
            
            wav_file.writeframes(audio_bytes)
        
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')


# Función para generar y guardar todos los assets
def generate_asset_file():
    """Genera archivo con todos los assets embebidos."""
    
    generator = AssetGenerator()
    all_assets = generator.generate_all_assets()
    
    # Crear archivo Python con assets
    asset_code = '''"""
Assets embebidos generados automáticamente para Chen Toka - Sinaloa Dragon
"""

EMBEDDED_ASSETS = {
'''
    
    for asset_name, asset_data in all_assets.items():
        asset_code += f'    "{asset_name}": "{asset_data}",\n'
    
    asset_code += '}\n'
    
    # Guardar archivo
    with open('embedded_assets.py', 'w', encoding='utf-8') as f:
        f.write(asset_code)
    
    print(f"Archivo embedded_assets.py generado con {len(all_assets)} assets")


if __name__ == "__main__":
    # Generar assets si se ejecuta directamente
    try:
        generate_asset_file()
    except ImportError as e:
        print(f"Dependencias faltantes: {e}")
        print("Los assets se generarán en tiempo de ejecución con sprites simples")