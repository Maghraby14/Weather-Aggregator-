import datetime as dt
import threading
import requests
from bs4 import BeautifulSoup
import socket
import json
from geopy.geocoders import Nominatim
import pytz
from timezonefinder import TimezoneFinder

# Weather Aggregator
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = "39f4e923867af7a7d94e04171d7cdfe7"


def to_celsius(temp_kelvin):
    temp_celsius = temp_kelvin - 273.15
    return temp_celsius


def get_weather(city):
    url = BASE_URL + "q=" + city + "&appid=" + API_KEY
    response1 = requests.get(url).json()

    temp_kelvin = response1['main']['temp']
    temp_celsius = to_celsius(temp_kelvin)
    feels_like_kelvin = response1['main']['feels_like']
    feels_like_celsius = to_celsius(feels_like_kelvin)
    humidity = response1['main']['humidity']
    wind_speed = response1['wind']['speed']
    description = response1['weather'][0]['description']
    sunrise_time = dt.datetime.utcfromtimestamp(response1['sys']['sunrise'])
    sunset_time = dt.datetime.utcfromtimestamp(response1['sys']['sunset'])
    pressure = response1['main']['pressure']

    weather_data = {
        'temperature': f"{temp_celsius:.2f}",
        'feels_like': f"{feels_like_celsius:.2f}",
        'humidity': f"{humidity}",
        'wind_speed': f"{wind_speed}",
        'description': f"{description}",
        'sun_rise': f"{sunrise_time}",
        'sun_set': f"{sunset_time}",
        'pressure': f"{pressure}"
    }
    return weather_data


def scrape_tech_news():
    response2 = requests.get("https://news.ycombinator.com/")
    yc_web_page = response2.text

    soup = BeautifulSoup(yc_web_page, "html.parser")
    articles = soup.select(".titleline > a")
    article_points_tags = soup.find_all(name="span", class_="score")
    article_titles = []
    article_links = []
    article_points = []

    for article_tag in articles:
        title = article_tag.getText()
        article_titles.append(title)
        link = article_tag.get("href")
        article_links.append(link)

    for x in article_points_tags:
        points = int(x.getText().split()[0])
        article_points.append(points)

    tech_news_data = []
    for i in range(len(article_titles)):
        article_data = {
            "title": article_titles[i],
            "link": article_links[i],
            # "points": article_points[i]
        }
        tech_news_data.append(article_data)
    return tech_news_data


def get_coordinates(city):
    geolocator = Nominatim(user_agent='Weather & news aggregator')
    location = geolocator.geocode(city)
    obj = TimezoneFinder()
    result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
    return result


def handle_client(conn, addr):
    with conn:
        print('Connected by', addr)
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                city, request = data.split(b'|')
                if request == b'weather':
                    response = get_weather(city.decode())
                elif request == b'news':
                    response = scrape_tech_news()
                elif request == b'time':
                    timezone = pytz.timezone(get_coordinates(city.decode()))
                    current_time = dt.datetime.now(timezone)
                    response = current_time.strftime('%I:%M:%S %p')
                else:
                    response = "Invalid request."
                # converts dict to string as we can't send dictionaries
                response_json = json.dumps(response)
                conn.sendall(response_json.encode())
        except ConnectionResetError:
            print(f"Connection with {addr} reset by remote host.")
        except ValueError:
            print("Incorrect format")
        finally:
            conn.close()


HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
