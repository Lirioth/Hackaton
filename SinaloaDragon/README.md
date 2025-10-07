# Chen Toka — Sinaloa Dragon
## Retro 2D Sidescroller

Un juego de plataformas 2D estilo retro protagonizado por Chen Toka, un dragon de Sinaloa en una aventura por las ciudades de México.

### 🎮 Características
- Resolución retro 320×180 escalada a 1280×720
- 3 niveles únicos: Ciudad de México, Guadalajara y Oaxaca
- Sistema de combate con parry y mecánicas avanzadas
- Controles remapeables (teclado + gamepad XInput)
- Guardado automático y sistema de configuración
- Compilable a ejecutable Windows (.exe)

### 🚀 Inicio Rápido (Windows)

**Requisitos:**
- Python 3.11+ instalado
- Windows 10/11

**Para jugar:**
1. Doble clic en `run.bat` (la primera vez creará el entorno virtual e instalará dependencias)
2. El juego iniciará automáticamente

**Controles por defecto:**
- **Movimiento:** WASD o Flechas
- **Salto:** Espacio
- **Ataque ligero:** J
- **Ataque pesado:** K  
- **Roll/Esquive:** L
- **Parry:** Shift izquierdo
- **Pausa:** Escape
- **Gamepad:** Compatible con controles XInput (Xbox)

### 🛠️ Compilar a EXE

Para crear un ejecutable Windows independiente:

1. Doble clic en `build_exe.bat`
2. El archivo `ChenToka.exe` se generará en la carpeta `dist/`
3. El ejecutable incluye todos los assets y dependencias

### ⚙️ Configuración

**Remap de controles:**
- Accede al menú Options desde la pantalla principal
- Selecciona el control que deseas cambiar
- Presiona la nueva tecla/botón

**Archivos de guardado:**
- Configuración: `%APPDATA%\ChenToka\config.json`
- Progreso: `%APPDATA%\ChenToka\slot_01.json`
- Fallback local: `./save/` si no se puede acceder a APPDATA

### 🎯 Gameplay

**Chen Toka puede:**
- Correr y saltar (salto variable y doble salto)
- Roll con marcos de invencibilidad
- Parry con timing perfecto
- Combo de 3 ataques
- Atravesar plataformas hacia abajo

**Enemigos:**
- **Matón:** Ataques lentos con gran telegrafía
- **Chacal:** Lanza cuchillos con ritmo
- **Luchador:** Agarres cortos, vulnerable al roll
- **Dron de Seguridad:** Patrulla aérea, débil a ataques aéreos

**Niveles:**
1. **CDMX:** Metro que pasa cada 12 segundos
2. **Guadalajara:** Suelos resbaladizos por la lluvia
3. **Oaxaca:** Papel picado que oscurece la visión

**Boss Final:** El Jaguar (ex-luchador) con 3 fases

### 🔧 Solución de Problemas

**El juego no inicia:**
- Verifica que Python 3.11+ esté instalado
- Ejecuta `run.bat` desde el explorador de archivos
- Si falla, abre CMD y ejecuta: `.venv\Scripts\python -m src.main`

**Error al compilar EXE:**
- Asegúrate de que el juego funcione primero con `run.bat`
- Verifica que no haya procesos usando archivos del proyecto
- Si PyInstaller falla, prueba ejecutar `build_exe.bat` como administrador

**Audio no funciona:**
- El juego detecta automáticamente dispositivos de audio
- Si no hay audio disponible, funcionará en modo silencioso

**Para debug:**
- Activa "Debug Mode" en el menú Options para ver hitboxes
- Los logs se guardan en la consola (ejecuta con `--console` en PyInstaller)

### 📁 Estructura del Proyecto

```
/
├── README.md
├── requirements.txt
├── run.bat
├── build_exe.bat
├── src/
│   ├── main.py
│   ├── game.py
│   ├── settings.py
│   ├── assets.py
│   ├── input.py
│   ├── ecs/
│   ├── ui/
│   ├── levels/
│   └── save/
├── assets/
│   ├── sprites/
│   ├── backgrounds/
│   ├── audio/
│   └── fonts/
├── save/
├── tests/
└── LICENSE.txt
```

### 📜 Licencia y Atribuciones

- Código fuente bajo MIT License
- Assets placeholder incluidos para desarrollo
- Fuente incluida bajo SIL Open Font License
- Sonidos generados procedimentalmente para evitar problemas de copyright

**Nota:** Los assets son placeholders básicos. Se recomienda reemplazarlos con arte original para distribución comercial.

### 🤝 Contribuciones

Este proyecto respeta y celebra la cultura mexicana. Los elementos culturales están representados con respeto, destacando murales, música, comida callejera y la comunidad.

---

**¡Disfruta la aventura de Chen Toka por México!** 🐉🇲🇽