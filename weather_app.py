import requests
from PIL import Image, ImageTk
Image.CUBIC = Image.BICUBIC
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from tkinter import messagebox
from datetime import datetime, timezone, timedelta
from io import BytesIO
from weather_database_week_8 import add_city, get_cities, delete_city

# OpenWeatherMap API Key 
API_KEY = "0404e4dd8c27b6a5c9dcfd390e6ed0c9"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

temp_unit = "Fahrenheit"

# Function to determine meter color based on temperature
def get_meter_color(temp):
    if temp <= 59:
        return "info"  # Blue for cold
    elif temp >= 60 and temp < 75:
        return "success"  # Green for mild
    else:
        return "danger"  # Red for hot

# Function to convert timezone offset to readable time
def convert_timezone(utc_offset):
    # Get the current UTC time
    utc_now = datetime.now(timezone.utc)
    # Apply the offset (convert seconds to hours)
    local_time = utc_now + timedelta(seconds=utc_offset)
    return local_time.strftime("%m-%d-%Y %I:%M %p")


# Function to get weather data
def get_weather(event=None):
    city = city_entry.get().strip()
    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name.")
        return

    unit = "imperial" if temp_unit == "Fahrenheit" else "metric"
    params = {"q": city, "appid": API_KEY, "units": unit}  # Fahrenheit
    try:
        response = requests.get(BASE_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            city_name = data['name']           
            weather_icon_code = data["weather"][0]["icon"]
            icon_url = f"http://openweathermap.org/img/wn/{weather_icon_code}@2x.png"
            weather_description = data['weather'][0]['description'].capitalize()
            temperature = data['main']['temp']
            temp_max = data['main']['temp_max']
            temp_min = data['main']['temp_min']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            timezone_offset = data['timezone']  # Get timezone offset in seconds

            response = requests.get(icon_url)
            img_data = Image.open(BytesIO(response.content))
            img_data = img_data.resize((100, 100), Image.Resampling.LANCZOS)  # Resize icon
            img = ImageTk.PhotoImage(img_data)
        
            icon_label.config(image=img)
            icon_label.image = img  # Keep a reference to avoid garbage collection

            # Convert timezone offset to readable format
            local_time = convert_timezone(timezone_offset)

            # Get the appropriate color
            meter_color = get_meter_color(temperature)

            # Update the temperature meter
            temp_meter.configure(
                amountused=int(temperature),
                bootstyle=meter_color  # Dynamically set color
            )

            # Update the text label with "Feels Like" and Timezone
            result_label.config(text=f" {city_name}\n"
                                     f" Local Time: {local_time}\n"
                                     f" Weather Description: {weather_description}\n"
                                     f" Temperature: {temperature}°{'F' if temp_unit == 'Fahrenheit' else 'C'}\n"
                                     f" Temperature Max: {temp_max}°{'F' if temp_unit == 'Fahrenheit' else 'C'}\n"
                                     f" Temperature Min: {temp_min}°{'F' if temp_unit == 'Fahrenheit' else 'C'}\n"
                                     f" Feels Like: {feels_like}°{'F' if temp_unit == 'Fahrenheit' else 'C'}\n"
                                     f" Humidity: {humidity}%\n"
                                     f" Wind Speed: {wind_speed} mph",
                                bootstyle=meter_color)

        elif response.status_code == 404:
            messagebox.showerror("Error", f"City '{city}' not found. Please check spelling.")
        else:
            messagebox.showerror("Error", f"Unable to fetch data. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to connect to API.\n{e}")


def refresh_weather():
    print("Fetching updated weather data...")


def show_cities():
    """Fetch and display stored cities."""
    cities_listbox.delete(0, ttk.END)
    for city in get_cities():
        cities_listbox.insert(ttk.END, city)

def add_city_gui():
    """Handles adding a city from the GUI."""
    city = city_entry.get().strip()
    if city:
        add_city(city)
        show_cities()
    else:
        messagebox.showwarning("Warning", "City name cannot be empty!")

def delete_city_gui():
    """Handles deleting a selected city."""
    selected_city = cities_listbox.get(ttk.ACTIVE)
    if selected_city:
        delete_city(selected_city)
        show_cities()
    else:
        messagebox.showwarning("Warning", "Select a city to delete!")

def on_city_selected():
    """Gets the selected city and fetches weather when clicked."""
    selected_index = cities_listbox.curselection()
    if selected_index:
        city = cities_listbox.get(selected_index)
        get_weather(city)

def open_settings():
    """Open the settings window to change temperature unit."""
    settings_win = tk.Toplevel(app)
    settings_win.title("Settings")
    settings_win.geometry("300x200")

    tk.Label(settings_win, text="Select Temperature Unit:", font=("Arial", 14)).pack(pady=10)

    unit_var = tk.StringVar(value=temp_unit)
    unit_menu = ttk.Combobox(settings_win, textvariable=unit_var, values=["Fahrenheit", "Celsius"], state="readonly")
    unit_menu.pack(pady=10)

    def save_settings():
        """Save and apply the new temperature unit."""
        global temp_unit
        temp_unit = unit_var.get()
        get_weather()  # Refresh weather with new unit
        settings_win.destroy()  # Close settings window

    save_button = tk.Button(settings_win, text="Save", command=save_settings)
    save_button.pack(pady=10)
    
   
    
# Setting up the ttkbootstrap GUI
app = ttk.Window(themename="superhero") 
app.title("Weather App")
app.geometry("480x320")
app.attributes('-fullscreen', True)

ttk.Label(app, text="Enter City:", font=("Arial", 12), bootstyle=PRIMARY).pack(pady=5)
city_entry = ttk.Entry(app, font=("Arial", 12), width=30)
city_entry.pack(pady=5)

ttk.Button(app, text="Get Weather", bootstyle=SUCCESS, command=get_weather).pack(pady=10)


# Temperature Meter
temp_meter = ttk.Meter(
    app,
    bootstyle="info",  # Default blue color
    subtext="Temperature (°F)",
    interactive=False,  # Users cannot change it
    amounttotal=120,  # Max temperature (adjust as needed)
    amountused=0,  # Default value
    metertype="semi",  # Semi-circle meter
    metersize=20,
)
temp_meter.pack(side="left", padx=10)

icon_label = ttk.Label(app)
icon_label.pack(side="left", padx=10)


result_label = ttk.Label(app, text="", font=("Arial", 12), bootstyle=INFO)
result_label.pack(side="left", padx=10)

refresh_button = tk.Button(app, text="Refresh Weather", command=refresh_weather)
refresh_button.pack(pady=5)

settings_button = tk.Button(app, text="Settings", command=open_settings)
settings_button.pack(pady=5)

weather_var = tk.StringVar(value="Click a saved city to view the weather")
weather_label = tk.Label(app, textvariable=weather_var, font=("Arial", 12))
weather_label.pack(padx=5)

add_button = ttk.Button(app, text="Add City", bootstyle=SUCCESS, command=add_city_gui)
add_button.pack(pady=5)

delete_button = ttk.Button(app, text="Delete City", bootstyle=DANGER, command=delete_city_gui)
delete_button.pack(pady=5)


cities_listbox = tk.Listbox(app, width=30, height=10)  
cities_listbox.config(bg="white", fg="black", font=("Arial", 12)) 
cities_listbox.bind("<<ListboxSelect>>", get_weather) 
cities_listbox.pack(pady=10)
cities_listbox.pack(pady=10)

show_cities()
app.mainloop()