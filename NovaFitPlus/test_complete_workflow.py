#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba integral para verificar la actualización del dashboard
cuando se cambia la ciudad en el perfil
"""

import sys
import os
import time

# Add the parent directory to the path to import the NovaFit Plus modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from novafit_plus.db import upsert_user, get_user, weather_on_date
from novafit_plus.utils import today_iso

# Database path
db_path = "data/novafit_plus.db"

def test_full_city_workflow():
    """Test complete city update workflow like GUI would do"""
    
    print("🧪 Probando flujo completo de actualización de ciudad...")
    
    # Step 1: Get original user data
    original_user = get_user(db_path, "Kevin")
    if not original_user:
        print("❌ Usuario Kevin no encontrado")
        return
        
    original_city = original_user[7]
    print(f"📍 Ciudad original: {original_city}")
    
    # Step 2: Check original weather
    original_weather = weather_on_date(db_path, today_iso(), "Kevin")
    if original_weather:
        print(f"🌤️ Clima original: {original_weather[5]} - {original_weather[4]}°C")
    else:
        print("❌ No hay clima original")
    
    # Step 3: Update to new city (simulating GUI save_profile())
    new_city = "Tokyo"
    print(f"\n🔄 Simulando cambio a {new_city}...")
    
    # Simulate clearing weather cache
    try:
        if os.path.exists("weather_cache.json"):
            os.remove("weather_cache.json")
            print("✅ Cache de clima eliminado")
    except:
        print("⚠️ No se pudo eliminar cache")
    
    # Update user city
    upsert_user(db_path, original_user[1], original_user[2], original_user[3], 
                original_user[4], original_user[5], original_user[6], new_city, original_user[8])
    
    updated_user = get_user(db_path, "Kevin")
    if updated_user and updated_user[7] == new_city:
        print(f"✅ Usuario actualizado a {updated_user[7]}")
        
        # Step 4: Check if weather function returns correct data
        new_weather = weather_on_date(db_path, today_iso(), "Kevin")
        if new_weather:
            print(f"🌤️ Nuevo clima: {new_weather[5]} - {new_weather[4]}°C")
            if new_weather[5] == new_city:
                print("✅ El clima corresponde a la nueva ciudad")
            else:
                print(f"❌ El clima es de {new_weather[5]}, no de {new_city}")
        else:
            print(f"⚠️ No hay clima disponible para {new_city}")
    else:
        print("❌ Fallo en actualización de usuario")
    
    # Step 5: Restore original city
    print(f"\n🔄 Restaurando ciudad original {original_city}...")
    upsert_user(db_path, original_user[1], original_user[2], original_user[3], 
                original_user[4], original_user[5], original_user[6], original_city, original_user[8])
    
    final_user = get_user(db_path, "Kevin")
    if final_user and final_user[7] == original_city:
        print(f"✅ Usuario restaurado a {final_user[7]}")
        
        # Clear cache again for clean state
        try:
            if os.path.exists("weather_cache.json"):
                os.remove("weather_cache.json")
        except:
            pass
    else:
        print("❌ Fallo en restauración de usuario")

def test_refresh_dashboard_logic():
    """Test the logic that refresh_dashboard() uses"""
    
    print("\n🧪 Probando lógica de refresh_dashboard...")
    
    user_name = "Kevin"
    
    # This simulates what refresh_dashboard() does
    wrow = weather_on_date(db_path, today_iso(), user_name)
    print(f"1. weather_on_date() retorna: {wrow}")
    
    # Get current user's city (our fix)
    current_user = get_user(db_path, user_name)
    user_city = current_user[7] if current_user and len(current_user) > 7 else ""
    print(f"2. Ciudad del usuario actual: '{user_city}'")
    
    # Check auto-fetch logic
    if not wrow and user_city:
        print("3. ✅ Debería auto-buscar clima (no hay clima y hay ciudad)")
    elif wrow:
        print("3. ✅ Ya hay clima disponible")
    else:
        print("3. ❌ No buscará clima (no hay ciudad configurada)")

if __name__ == "__main__":
    test_full_city_workflow()
    test_refresh_dashboard_logic()