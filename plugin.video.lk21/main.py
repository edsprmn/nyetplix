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
IPTV_INDO_URL = "https://raw.githubusercontent.com/mgi24/tvdigital/main/idwork.m3u"
IPTV_SPORTS_URL = "https://iptv-org.github.io/iptv/categories/sports.m3u"

HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 0

def fetch(url):
    """Fetch content using requests if in Kodi, or curl if in simulator."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Referer': BASE_URL
    }
    if KODI:
        xbmc.log(f"NYETPLIX FETCH: {url}", xbmc.LOGINFO)
        try:
            r = requests.get(url, headers=headers, timeout=10)
            return r.text
        except Exception as e:
            xbmc.log(f"NYETPLIX FETCH ERROR: {str(e)}", xbmc.LOGERROR)
            return ""
    else:
        command = ['curl', '-s', '-L', '-A', headers['User-Agent'], '-H', f"Referer: {BASE_URL}", url]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout if result.returncode == 0 else ""

# --- Scraper Logic ---

def list_lk21_movies(page_url):
    html = fetch(page_url)
    if not html:
        return [], None
        
    # Temukan setiap blok <article> untuk setiap film
    articles = re.findall(r'<article[^>]*>.*?</article>', html, re.DOTALL)
    if KODI: xbmc.log(f"NYETPLIX LK21 ARTICLES FOUND: {len(articles)}", xbmc.LOGINFO)
    
    found = []
    for art in articles:
        # Ekstrak Link, Judul, dan Thumbnail dari dalam article
        # Menggunakan regex yang sangat fleksibel (non-greedy)
        link_match = re.search(r'href=["\']([^"\']+)["\'][^>]*itemprop=["\']url["\']', art)
        if not link_match:
            link_match = re.search(r'itemprop=["\']url["\'][^>]*href=["\']([^"\']+)["\']', art)
            
        thumb_match = re.search(r'src=["\']([^"\']+)["\']', art)
        title_match = re.search(r'class=["\']poster-title["\'][^>]*>([^<]+)</h3>', art)
        
        if link_match and thumb_match and title_match:
            link = link_match.group(1)
            thumb = thumb_match.group(1)
            title = title_match.group(1).strip()
            
            full_link = link if link.startswith('http') else BASE_URL + link
            if not any(f['url'] == full_link for f in found):
                found.append({'title': title, 'url': full_link, 'thumb': thumb})
    
    # Cari link "Next Page" dengan pola yang lebih fleksibel
    next_match = re.search(r'<a href=["\']([^"\']+)["\'][^>]*>(?:&raquo;|»|Next)</a>', html)
    next_page = None
    if next_match:
        next_page = next_match.group(1)
        if not next_page.startswith('http'):
            next_page = BASE_URL + next_page

    return found, next_page

def get_lk21_video(movie_url):
    html = fetch(movie_url)
    player_pattern = r'href="(https://playeriframe.sbs/iframe/(p2p|hydrax|turbovip|cast)/([^"]+))"'
    player_match = re.search(player_pattern, html)
    
    if player_match:
        player_url = player_match.group(1)
        player_id = player_match.group(3)
        
        # Mencoba memanggil API resolver internal (cloud.hownetwork.xyz)
        api_url = f"https://cloud.hownetwork.xyz/api2.php?id={player_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Referer': f'https://cloud.hownetwork.xyz/video.php?id={player_id}',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        if KODI:
            try:
                payload = {'r': 'https://playeriframe.sbs/', 'd': 'cloud.hownetwork.xyz'}
                r = requests.post(api_url, headers=headers, data=payload, timeout=10)
                data = r.json()
                video_url = data.get('url')
                if not video_url and 'sources' in data and data['sources']:
                    video_url = data['sources'][0].get('file')
                
                if video_url:
                    return f"{video_url}|Referer=https://cloud.hownetwork.xyz/&User-Agent={headers['User-Agent']}"
            except:
                pass
        
        # Fallback ke pola zzz/39 jika API gagal
        return f"https://cloud.hownetwork.xyz/zzz/{player_id}/39/480.m3u8|Referer=https://cloud.hownetwork.xyz/"
        
    return None

def parse_m3u(url):
    content = fetch(url)
    if not content:
        return []
        
    channels = []
    # Regex yang lebih handal untuk M3U (menangani variasi atribut dan multipis liness)
    # Mencari #EXTINF diikuti oleh baris URL, mengabaikan baris kosong di antaranya
    segments = re.findall(r'#EXTINF:[^\n]*,([^\n\r]+)[\s\r\n]+(http[^\s\r\n]+)', content, re.MULTILINE)
    
    if KODI: xbmc.log(f"NYETPLIX M3U CHANNELS FOUND: {len(segments)}", xbmc.LOGINFO)
    
    for name, stream_url in segments[:250]:
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
    
    if not is_folder:
        list_item.setProperty('IsPlayable', 'true')
        
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

def main_menu():
    add_item("Movies (LK21)", {'action': 'lk21_menu', 'url': f"{BASE_URL}/latest"})
    add_item("TV Indonesia", {'action': 'iptv', 'url': IPTV_INDO_URL})
    add_item("Sports Live", {'action': 'iptv', 'url': IPTV_SPORTS_URL})
    xbmcplugin.endOfDirectory(HANDLE)

def lk21_menu(url):
    movies, next_page = list_lk21_movies(url)
    for movie in movies:
        add_item(movie['title'], {'action': 'play_lk21', 'url': movie['url']}, is_folder=False, thumbnail=movie['thumb'])
    
    if next_page:
        add_item(">>> Halaman Berikutnya", {'action': 'lk21_menu', 'url': next_page})
        
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
        lk21_menu(params.get('url'))
    elif action == 'iptv':
        iptv_menu(params.get('url'))
    elif action == 'play_lk21':
        video_url = get_lk21_video(params.get('url'))
        if video_url:
            play(video_url)
    elif action == 'play_direct':
        # Tambahkan User-Agent standar agar IPTV lebih lancar diputar
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        video_url = f"{params.get('url')}|User-Agent={ua}"
        play(video_url)

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
