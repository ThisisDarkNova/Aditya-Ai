import urllib.request
import urllib.parse
import re
import webbrowser
import os

def play_song_on_youtube(query: str) -> str:
    """
    Finds the first video on YouTube for a query and plays it directly.
    Uses 'Embed Mode' for a cleaner, mini-player-like experience if requested.
    """
    try:
        print(f"[AI] Looking for: {query}")
        
        q = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={q}"
        
        # Adding a User-Agent to prevent getting blocked by YouTube
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req)
        
        # Find all video IDs
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        
        if video_ids:
            video_id = video_ids[0]
            link = f"https://www.youtube.com/watch?v={video_id}"
            embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1"
            
            print(f"[AI] Playing Video ({link})")
            
            try:
                # Force open explicitly in Chrome
                os.system(f'start chrome "{link}"')
            except Exception:
                webbrowser.open(link)
            
            return f"Playing '{query}' on YouTube."
        else:
            # Fallback to standard search result if regex fails
            try:
                os.system(f'start chrome "{url}"')
            except Exception:
                webbrowser.open(url)
            return f"Couldn't find a direct video, but opened search results for '{query}'."

    except Exception as e:
        print(f"[ERROR] Youtube Player error: {e}")
        return f"Sorry, I ran into an error trying to play that: {e}"
