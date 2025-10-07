#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script final para simular exactamente el proceso de save_profile() de la GUI
"""

import sys
import os
import threading
import time

# Add the parent directory to the path to import the NovaFit Plus modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from novafit_plus.db import upsert_user, get_user, weather_on_date
from novafit_plus.utils import today_iso

# Database path
db_path = "data/novafit_plus.db"

def simulate_save_profile():
    """Simulate exactly what save_profile() does when changing city"""
    
    print("🔄 Simulando save_profile() completo...")
    
    # Step 1: Get original user data
    original_user = get_user(db_path, "Kevin")
    if not original_user:
        print("❌ Usuario Kevin no encontrado")
        return
        
    original_city = original_user[7]
    new_city = "Madrid"  # City to change to
    
    print(f"📍 Ciudad original: {original_city}")
    print(f"📍 Nueva ciudad: {new_city}")
    
    # Step 2: Clear weather cache (like GUI does)
    try:
        if os.path.exists("weather_cache.json"):
            os.remove("weather_cache.json")
            print("✅ Cache de clima eliminado")
    except:
        print("⚠️ No se pudo eliminar cache")
    
    # Step 3: Update user (like GUI upsert_user call)
    upsert_user(db_path, original_user[1], original_user[2], original_user[3], 
                original_user[4], original_user[5], original_user[6], new_city, original_user[8])
    
    print("✅ Usuario actualizado en DB")
    
    # Step 4: Simulate first refresh_dashboard() call (immediate)
    print("\n🔄 Primera llamada a refresh_dashboard()...")
    user_name = "Kevin"
    wrow = weather_on_date(db_path, today_iso(), user_name)
    
    # Get current user's city for weather fetching (our fix)
    current_user = get_user(db_path, user_name)
    user_city = current_user[7] if current_user and len(current_user) > 7 else ""
    
    print(f"   - User: {user_name}")
    print(f"   - City: '{user_city}'")
    print(f"   - Weather data: {wrow is not None}")
    
    if wrow:
        print(f"   - Weather: {wrow[5]} - {wrow[4]}°C")
    
    # Step 5: Simulate background weather fetch (if no weather for new city)
    if not wrow and user_city:
        print(f"\n🌐 Debería buscar clima para {user_city} en background...")
        print("   (En la GUI esto dispararía fetch_today_weather)")
    elif wrow and wrow[5] != new_city:
        print(f"\n⚠️  PROBLEMA: El clima es de {wrow[5]}, no de {new_city}")
        print("   Esto explicaría por qué el dashboard no se actualiza")
    elif wrow and wrow[5] == new_city:
        print(f"\n✅ ¡Perfecto! El clima ya corresponde a {new_city}")
    
    # Step 6: Restore original city
    print(f"\n🔄 Restaurando ciudad original {original_city}...")
    upsert_user(db_path, original_user[1], original_user[2], original_user[3], 
                original_user[4], original_user[5], original_user[6], original_city, original_user[8])
    
    # Clear cache again
    try:
        if os.path.exists("weather_cache.json"):
            os.remove("weather_cache.json")
    except:
        pass
    
    print("✅ Usuario restaurado")

def check_weather_data_availability():
    """Check what weather data is available in the database"""
    
    print("\n📊 Verificando clima disponible en la DB...")
    
    import sqlite3
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all weather data for today
        today = today_iso()
        cursor.execute("""
            SELECT date, city, temp_max, condition
            FROM weather 
            WHERE date = ?
            ORDER BY city
        """, (today,))
        
        weather_data = cursor.fetchall()
        
        if weather_data:
            print(f"   Clima disponible para {today}:")
            for date, city, temp, condition in weather_data:
                print(f"   - {city}: {temp}°C, {condition}")
        else:
            print(f"   ❌ No hay clima para {today}")
            
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error consultando clima: {e}")

if __name__ == "__main__":
    check_weather_data_availability()
    simulate_save_profile()