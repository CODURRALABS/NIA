"""
PublicAPIHub: Curated wrappers for high-value public APIs.
"""
import requests
import logging
import os

logger = logging.getLogger("PublicAPIHub")

class PublicAPIHub:
    def __init__(self):
        self.weather_key = os.environ.get("OPENWEATHER_API_KEY")
        self.news_key = os.environ.get("NEWSAPI_KEY")

    def get_weather(self, city: str):
        """Fetches current weather for a city."""
        if not self.weather_key: return "Weather API key missing."
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_key}&units=metric"
            resp = requests.get(url).json()
            temp = resp['main']['temp']
            desc = resp['weather'][0]['description']
            return f"Current weather in {city}: {temp}°C, {desc}."
        except Exception: return f"Could not find weather for {city}."

    def get_news(self, category: str = "technology"):
        """Fetches top headlines."""
        if not self.news_key: return "News API key missing."
        try:
            url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={self.news_key}&pageSize=3"
            resp = requests.get(url).json()
            articles = [a['title'] for a in resp.get('articles', [])]
            return "Top Headlines: " + " | ".join(articles)
        except Exception: return "Could not fetch news."

    def get_joke(self):
        """Fetches a random joke."""
        try:
            return requests.get("https://official-joke-api.appspot.com/random_joke").json()['setup'] + " ... " + requests.get("https://official-joke-api.appspot.com/random_joke").json()['punchline']
        except Exception: return "Why did the AI cross the road? To get to the other dataset."

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    hub = PublicAPIHub()
    print(hub.get_joke())
