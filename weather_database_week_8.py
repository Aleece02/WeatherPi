import sqlite3

def create_database():
    """Creates the database and cities table if it doesn't exist."""
    conn = sqlite3.connect("weather_app.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_city(city_name):
    """Adds a city to the database."""
    conn = sqlite3.connect("weather_app.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO cities (name) VALUES (?)", (city_name,))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"{city_name} is already saved.")
    conn.close()

def get_cities():
    """Retrieves all stored cities."""
    conn = sqlite3.connect("weather_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM cities")
    cities = cursor.fetchall()
    conn.close()
    return [city[0] for city in cities]

def delete_city(city_name):
    """Deletes a city from the database."""
    conn = sqlite3.connect("weather_app.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cities WHERE name=?", (city_name,))
    conn.commit()
    conn.close()

# Run this when starting the app to ensure the database exists
create_database()