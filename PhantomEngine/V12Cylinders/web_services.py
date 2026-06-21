import os
import httpx
import re

# Global thread-safe keep-alive HTTP client to pool connections and avoid handshakes
httpx_client = httpx.Client(timeout=8.0, follow_redirects=True)

def get_weather(location: str) -> str:
    """Fetches real-time weather using OpenWeather API."""
    key = os.environ.get("OPENWEATHER_API_KEY")
    if not key:
        return "Weather API Key not configured."
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={key}&units=metric"
    try:
        r = httpx_client.get(url)
        if r.status_code == 200:
            data = r.json()
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            return f"Weather in {location}: {weather.capitalize()} with a temperature of {temp}°C."
        return f"Failed to get weather. Code {r.status_code}: {r.text}"
    except Exception as e:
        return f"Weather API error: {e}"

def get_news(topic: str = "general") -> str:
    """Fetches latest news using NewsAPI India focus or global topic."""
    key = os.environ.get("NEWS_API_KEY")
    if not key:
        return "News API Key not configured."
    
    url = f"https://newsapi.org/v2/top-headlines?q={topic}&apiKey={key}&pageSize=5"
    if topic.lower() == "general" or not topic:
         url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={key}&pageSize=5"
         
    try:
        r = httpx_client.get(url)
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])
            if not articles:
                return f"No news found for topic: {topic}"
            
            res = f"Top News ({topic}):\n"
            for i, a in enumerate(articles, 1):
                res += f"{i}. {a.get('title')}\n"
            return res
        return f"Failed to get news. Code {r.status_code}"
    except Exception as e:
        return f"News API error: {e}"

def web_search(query: str) -> str:
    """Performs a live web search using DuckDuckGo Html (Free, No API Key needed)."""
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    data = {"q": query}
    try:
        r = httpx_client.post(url, data=data, headers=headers)
        if r.status_code == 200:
            html = r.text
            # Extract snippets using regex
            snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
            # Remove HTML tags inside snippets
            clean_snippets = [re.sub(r'<[^>]+>', '', s).strip() for s in snippets]
            
            if not clean_snippets:
                return f"No search results found for: {query}"
                
            res = f"Search Results for '{query}':\n"
            for i in range(min(5, len(clean_snippets))):
                res += f"{i+1}. {clean_snippets[i]}\n"
            return res
        return f"Search failed. Code {r.status_code}"
    except Exception as e:
        return f"Search API error: {e}"
