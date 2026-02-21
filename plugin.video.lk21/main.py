import sys
import re
import json
import urllib.parse

# Import Kodi modules safely
try:
    import xbmc
    import xbmcgui
    import xbmcplugin
    import xbmcaddon
    import requests
    KODI = True
except ImportError:
    import subprocess
    KODI = False

# URL Dasar
BASE_URL = "https://tv8.lk21official.cc"
IPTV_INDO_URL = "https://raw.githubusercontent.com/mgi24/tvdigital/main/iptv_indonesia.m3u"
IPTV_SPORTS_URL = "https://iptv-org.github.io/iptv/categories/sports.m3u"

HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 0

def fetch(url):
    """Fetch content using requests if in Kodi, or curl if in simulator."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Referer': BASE_URL
    }
    if KODI:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            return r.text
        except:
            return ""
    else:
        command = ['curl', '-s', '-L', '-A', headers['User-Agent'], '-H', f"Referer: {BASE_URL}", url]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout if result.returncode == 0 else ""

# --- Scraper Logic ---

def list_lk21_movies(page_url):
    html = fetch(page_url)
    pattern = r'<a href="([^"]+)" itemprop="url">.*?<h3 class="poster-title" itemprop="name">([^<]+)</h3>.*?<img.*?src="([^"]+)"'
    movies = re.findall(pattern, html, re.DOTALL)
    
    found = []
    for link, title, thumb in movies:
        full_link = link if link.startswith('http') else BASE_URL + link
        found.append({'title': title.strip(), 'url': full_link, 'thumb': thumb})
    return found

def get_lk21_video(movie_url):
    html = fetch(movie_url)
    player_pattern = r'href="(https://playeriframe.sbs/iframe/[^"]+)"'
    players = re.findall(player_pattern, html)
    return players[0] if players else None

def parse_m3u(url):
    content = fetch(url)
    channels = []
    pattern = r'#EXTINF:.*?,(.*?)\n(http.*?)$'
    matches = re.findall(pattern, content, re.MULTILINE)
    for name, stream_url in matches[:50]:
        channels.append({'title': name.strip(), 'url': stream_url.strip()})
    return channels

# --- Kodi UI Logic ---

def add_item(label, url_params, is_folder=True, thumbnail=""):
    addon_base = sys.argv[0]
    query = urllib.parse.urlencode(url_params)
    url = f"{addon_base}?{query}"
    list_item = xbmcgui.ListItem(label=label)
    if thumbnail:
        list_item.setArt({'thumb': thumbnail, 'icon': thumbnail})
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

def main_menu():
    add_item("Movies (LK21)", {'action': 'lk21_menu'})
    add_item("TV Indonesia", {'action': 'iptv', 'url': IPTV_INDO_URL})
    add_item("Sports Live", {'action': 'iptv', 'url': IPTV_SPORTS_URL})
    xbmcplugin.endOfDirectory(HANDLE)

def lk21_menu():
    movies = list_lk21_movies(f"{BASE_URL}/latest")
    for movie in movies:
        add_item(movie['title'], {'action': 'play_lk21', 'url': movie['url']}, is_folder=False, thumbnail=movie['thumb'])
    xbmcplugin.endOfDirectory(HANDLE)

def iptv_menu(url):
    channels = parse_m3u(url)
    for ch in channels:
        add_item(ch['title'], {'action': 'play_direct', 'url': ch['url']}, is_folder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def play(url):
    list_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(HANDLE, True, list_item)

# --- Routing ---

def router(param_string):
    params = dict(urllib.parse.parse_qsl(param_string))
    action = params.get('action')

    if not action:
        main_menu()
    elif action == 'lk21_menu':
        lk21_menu()
    elif action == 'iptv':
        iptv_menu(params.get('url'))
    elif action == 'play_lk21':
        video_url = get_lk21_video(params.get('url'))
        if video_url:
            play(video_url)
    elif action == 'play_direct':
        play(params.get('url'))

if __name__ == "__main__":
    try:
        if KODI:
            # sys.argv[2] contains the parameters like ?action=...
            # If it's empty or doesn't exist, we send empty string
            params = sys.argv[2][1:] if len(sys.argv) > 2 else ""
            router(params)
        else:
            print("Simulator mode - use terminal to test logic.")
            # Manual test logic for simulator if needed
            print(f"LK21 Sample: {list_lk21_movies(f'{BASE_URL}/latest')[:2]}")
    except Exception as e:
        if KODI:
            import traceback
            error_msg = traceback.format_exc()
            xbmcgui.Dialog().ok("Nyetplix Error", f"Terjadi kesalahan:\n{str(e)}\n\nKirimkan pesan ini ke developer.")
            xbmc.log(f"NYETPLIX ERROR: {error_msg}", xbmc.LOGERROR)
        else:
            raise e
