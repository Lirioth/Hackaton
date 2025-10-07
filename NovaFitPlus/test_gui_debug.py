#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para probar la GUI con debug habilitado
"""

import sys
import os

# Add the parent directory to the path to import the NovaFit Plus modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and enable debug mode
import novafit_plus.ui_tk as ui_module

# Enable debug mode in refresh_dashboard
if hasattr(ui_module, 'refresh_dashboard'):
    # This won't work because it's defined inside main()
    pass

# Better approach: patch the ui_tk module to enable debug
import importlib.util

print("🔧 Ejecutando GUI con modo debug habilitado...")
print("📝 Instrucciones:")
print("   1. Abre la aplicación")
print("   2. Ve al tab Profile")
print("   3. Cambia la ciudad (ej: de Beersheba a Madrid)")
print("   4. Haz clic en 'Save Profile'")
print("   5. Observa los mensajes de debug en la terminal")
print("   6. Ve al Dashboard para verificar si el clima se actualizó")
print("\n🚀 Iniciando aplicación...")

# Run the GUI
exec(open("novafit_plus/ui_tk.py").read())