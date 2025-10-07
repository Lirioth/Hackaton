import sqlite3
from datetime import datetime

# Conectar a la base de datos
conn = sqlite3.connect('data/novafit_plus.db')
cursor = conn.cursor()

# Ver el perfil actual
cursor.execute("SELECT name, city, country FROM users WHERE name='Kevin'")
user = cursor.fetchone()
print(f"Usuario actual: {user}")

# Ver qué datos de clima están disponibles para hoy
today = datetime.now().strftime('%Y-%m-%d')
cursor.execute("SELECT city, temp_max, temp_min, condition FROM weather WHERE date=?", (today,))
weather_data = cursor.fetchall()
print(f"\nClima disponible para hoy ({today}):")
for row in weather_data:
    print(f"  {row[0]}: {row[1]}°C-{row[2]}°C, condición: {row[3]}")

# Simular la función weather_on_date mejorada
def test_weather_for_user(user_name, date):
    print(f"\n🧪 Simulando weather_on_date('{date}', '{user_name}'):")
    
    # Get user's city
    cursor.execute("SELECT city FROM users WHERE name=?", (user_name,))
    user_result = cursor.fetchone()
    
    if user_result and user_result[0]:
        user_city = user_result[0]
        print(f"  1. Ciudad del usuario: {user_city}")
        
        # Try to get weather for user's city
        cursor.execute("""
            SELECT temp_max, temp_min, humidity, wind_speed, condition, city 
            FROM weather 
            WHERE date=? AND city=? 
            ORDER BY id DESC LIMIT 1
        """, (date, user_city))
        weather_result = cursor.fetchone()
        
        if weather_result:
            print(f"  2. ✅ Clima encontrado para {user_city}: {weather_result}")
            return weather_result
        else:
            print(f"  2. ❌ No hay datos de clima para {user_city}")
    
    # Fallback
    cursor.execute("""
        SELECT temp_max, temp_min, humidity, wind_speed, condition, city 
        FROM weather 
        WHERE date=? 
        ORDER BY id DESC LIMIT 1
    """, (date,))
    fallback = cursor.fetchone()
    print(f"  3. Fallback - cualquier clima: {fallback}")
    return fallback

test_weather_for_user('Kevin', today)

conn.close()