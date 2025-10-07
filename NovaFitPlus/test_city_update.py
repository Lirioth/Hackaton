#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar que las actualizaciones de ciudad funcionen correctamente
"""

import sys
import os

# Add the parent directory to the path to import the NovaFit Plus modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from novafit_plus.db import upsert_user, get_user, weather_on_date
from novafit_plus.utils import today_iso

# Database path
db_path = "data/novafit_plus.db"

def test_city_update():
    """Test that city updates work correctly"""
    
    print("🧪 Probando actualizaciones de ciudad...")
    
    # Get current user
    user = get_user(db_path, "Kevin")
    if user:
        print(f"Usuario actual: {user[1]} en {user[7] or 'Ciudad no establecida'}")
        
        # Test updating to a different city
        print("\n📍 Actualizando ciudad a Madrid...")
        upsert_user(db_path, user[1], user[2], user[3], user[4], user[5], user[6], "Madrid", user[8])
        
        # Check if user was updated
        updated_user = get_user(db_path, "Kevin")
        if updated_user:
            print(f"✅ Usuario actualizado: {updated_user[1]} en {updated_user[7]}")
            
            # Test weather lookup with new city
            weather_data = weather_on_date(db_path, today_iso(), "Kevin")
            if weather_data:
                print(f"🌤️ Clima encontrado: {weather_data[5]} - {weather_data[4]}°C")
            else:
                print("❌ No se encontró clima para la nueva ciudad")
                
        # Restore original city
        print(f"\n🔄 Restaurando ciudad original a {user[7]}...")
        upsert_user(db_path, user[1], user[2], user[3], user[4], user[5], user[6], user[7], user[8])
        
        final_user = get_user(db_path, "Kevin")
        if final_user:
            print(f"✅ Usuario restaurado: {final_user[1]} en {final_user[7]}")
            
    else:
        print("❌ No se encontró el usuario Kevin")

if __name__ == "__main__":
    test_city_update()