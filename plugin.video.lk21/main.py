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
LK21_URL = "https://tv8.lk21official.cc"
SERIES_URL = "https://tv3.nontondrama.my"
JAV_URL = "https://javtiful.com"

IPTV_INDO_URL = "https://iptv-org.github.io/iptv/countries/id.m3u"
IPTV_SPORTS_URL = "https://iptv-org.github.io/iptv/categories/sports.m3u"

# Konten Mapping
MOVIES_CATS = [
    ("Movies Terbaru", f"{LK21_URL}/latest"),
    ("Action", f"{LK21_URL}/genre/action/"),
    ("Anime", f"{LK21_URL}/genre/animation/"),
    ("Horror", f"{LK21_URL}/genre/horror/"),
    ("Comedy", f"{LK21_URL}/genre/comedy/"),
    ("Sci-Fi", f"{LK21_URL}/genre/sci-fi/"),
    ("Romance", f"{LK21_URL}/genre/romance/"),
    ("Bluray", f"{LK21_URL}/quality/bluray/"),
    ("Populer", f"{LK21_URL}/populer/")
]

SERIES_CATS = [
    ("Action", f"{SERIES_URL}/genre/action/"),
    ("Sci-Fi", f"{SERIES_URL}/genre/sci-fi/"),
    ("Populer", f"{SERIES_URL}/populer/")
]

JAV_CATS = [
    ("Semua Video", f"{JAV_URL}/videos"),
    ("Trending", f"{JAV_URL}/trending"),
    ("Rekomendasi", f"{JAV_URL}/recommendation"),
    ("Sedang Ditonton", f"{JAV_URL}/videos/sort=being_watched"),
    ("Paling Banyak Dilihat", f"{JAV_URL}/videos/sort=most_viewed"),
    ("Rating Teratas", f"{JAV_URL}/videos/sort=top_rated"),
    ("Favorit Teratas", f"{JAV_URL}/videos/sort=top_favorites"),
    ("Disensor", f"{JAV_URL}/censored"),
    ("Tanpa Sensor", f"{JAV_URL}/uncensored"),
    ("Pemeran (Actresses)", f"{JAV_URL}/actresses"),
    ("Channels", f"{JAV_URL}/channels"),
    ("Genre (Categories)", f"{JAV_URL}/categories")
]

# List Kategori (Berdasarkan riset browser)
GENRES = ["Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy", "History", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Sport", "Thriller", "War", "Western"]
COUNTRIES = ["USA", "China", "India", "Japan", "South-Korea", "Thailand"]
YEARS = [str(y) for y in range(2026, 2010, -1)]
# The original SERIES_CATS is now replaced by the new one above.
# SERIES_CATS = [
#     ("Daftar Series", "/nontondrama"),
#     ("Series Terbaru", "/nontondrama?page=latest-series"),
#     ("Series Ongoing", "/nontondrama?page=series/ongoing"),
#     ("Series Complete", "/nontondrama?page=series/complete"),
#     ("Series Asian", "/nontondrama?page=series/asian"),
#     ("Series West", "/nontondrama?page=series/west")
# ]

HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 0

def fetch(url):
    """Fetch content using requests if in Kodi, or curl if in simulator."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Referer': url
    }
    if KODI:
        xbmc.log(f"NYETPLIX FETCH: {url}", xbmc.LOGINFO)
        try:
            # Bypass SSL (verify=False) untuk menghindari error sertifikat di Kodi
            r = requests.get(url, headers=headers, timeout=20, verify=False)
            if r.status_code != 200:
                xbmcgui.Dialog().notification("Nyetplix Error", f"HTTP {r.status_code}", xbmcgui.NOTIFICATION_ERROR, 3000)
            return r.text
        except Exception as e:
            err_msg = str(e)[:30] # Ambil potongan pesan error
            xbmc.log(f"NYETPLIX FETCH ERROR: {str(e)}", xbmc.LOGERROR)
            xbmcgui.Dialog().notification("Nyetplix Error", f"Gagal: {err_msg}", xbmcgui.NOTIFICATION_ERROR, 5000)
            return ""
    else:
        command = ['curl', '-s', '-k', '-L', '-A', headers['User-Agent'], '-H', f"Referer: {url}", url]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout if result.returncode == 0 else ""

# --- Scraper Logic ---

def list_lk21_movies(page_url, current_page=1):
    html = fetch(page_url)
    if not html:
        return []
        
    found = []
    # Temukan setiap blok <article> terlebih dahulu
    articles = re.findall(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    
    for art in articles:
        # Ekstrak Link: cari href pertama
        link = ""
        link_match = re.search(r'href=["\']([^"\']+)["\']', art)
        if link_match:
            link = link_match.group(1)
            # Handle relative links based on domain (LK21 or Series)
            domain = SERIES_URL if "nontondrama" in page_url else LK21_URL
            if not link.startswith('http'):
                link = domain + link
        
        # Ekstrak Judul: cari di dalam h3
        title = "No Title"
        title_match = re.search(r'<h3[^>]*>([^<]+)</h3>', art)
        if title_match:
            title = title_match.group(1).strip()
            
        # Ekstrak Thumbnail
        thumb = ""
        img_matches = re.findall(r'src=["\']([^"\']+)["\']', art)
        for img in img_matches:
            if any(k in img for k in ["poster", "thumb", "uploads"]):
                thumb = img
                break
        if not thumb and img_matches:
            thumb = img_matches[0]
            
        if link and "/page/" not in link:
            if not any(f['url'] == link for f in found):
                found.append({'title': title, 'url': link, 'thumb': thumb})
    
    return found

def list_jav_movies(page_url):
    """Refined scraper for javtiful.com"""
    html = fetch(page_url)
    if not html:
        return []
        
    found = []
    # Pola: <a href="video_url" class="video-tmb"><img data-src="thumb_url">...<a class="video-link" title="title">
    pattern = r'href=["\'](https?://javtiful\.com/video/[^"\']+)["\'][^>]*class="[^"]*video-tmb[^"]*".*?data-src=["\']([^"\']+)["\'].*?class="[^"]*video-link[^"]*"[^>]*title=["\']([^"\']+)["\']'
    matches = re.findall(pattern, html, re.DOTALL)
    
    for link, thumb, title in matches:
        found.append({'title': title.strip(), 'url': link, 'thumb': thumb})
        
    if not found:
        # Fallback pola lebih fleksibel jika pola utama gagal
        matches = re.findall(r'href=["\']([^"\']+/video/[^"\']+)["\'].*?data-src=["\']([^"\']+)["\'].*?title=["\']([^"\']+)["\']', html, re.DOTALL)
        for link, thumb, title in matches:
            if not link.startswith('http'): link = JAV_URL + link
            found.append({'title': title.strip(), 'url': link, 'thumb': thumb})
            
    return found

def get_jav_video(video_url):
    """Resolver for JAVtiful.com"""
    html = fetch(video_url)
    if not html: return None
    
    # 1. Cari URL embed
    embed_match = re.search(r'data-embed-url=["\']([^"\']+)["\']', html)
    if embed_match:
        embed_url = embed_match.group(1)
        embed_html = fetch(embed_url)
        if embed_html:
            # 2. Cari playlist/source di halaman embed
            # Pola: const source = '...'; atau response.playlists = '...';
            source_match = re.search(r'(?:source|playlist|playlists)\s*[:=]\s*[\'"]([^\'"]+)[\'"]', embed_html)
            if source_match:
                return source_match.group(1)
    
    # Fallback: Cari langsung .m3u8 di halaman utama jika ada
    m3u8_match = re.search(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', html)
    if m3u8_match:
        return m3u8_match.group(1)
        
    return None

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
    # Membersihkan konten dari baris kosong yang mengganggu pembacaan
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    current_name = ""
    for line in lines:
        if line.startswith("#EXTINF"):
            # Ambil bagian setelah koma terakhir sebagai nama
            if "," in line:
                current_name = line.split(",")[-1].strip()
            else:
                current_name = "Unknown Channel"
        elif line.startswith("http"):
            if current_name:
                channels.append({'title': current_name, 'url': line})
                current_name = "" # Reset setelah dapet pasangan URL
            
    if KODI: xbmc.log(f"NYETPLIX M3U CHANNELS FOUND: {len(channels)}", xbmc.LOGINFO)
    return channels[:300]

# --- Kodi UI Logic ---

def add_item(label, url_params, is_folder=True, thumbnail=""):
    addon_base = sys.argv[0]
    query = urllib.parse.urlencode(url_params)
    url = f"{addon_base}?{query}"
    # Gunakan offscreen=True dan setLabel agar kompatibel dengan Kodi 19+
    list_item = xbmcgui.ListItem(offscreen=True)
    list_item.setLabel(label)
    
    if thumbnail:
        list_item.setArt({'thumb': thumbnail, 'icon': thumbnail})
    
    if not is_folder:
        list_item.setProperty('IsPlayable', 'true')
        
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

def main_menu():
    add_item("Movies", {'action': 'folder', 'type': 'movies'})
    add_item("Series", {'action': 'folder', 'type': 'series'})
    add_item("Telenovela", {'action': 'folder', 'type': 'jav'})
    add_item("TV Indonesia", {'action': 'iptv', 'url': IPTV_INDO_URL, 'mode': 'indo'})
    add_item("Sports Live", {'action': 'iptv', 'url': IPTV_SPORTS_URL, 'mode': 'sports'})
    xbmcplugin.endOfDirectory(HANDLE)

def folder_menu(ftype):
    if ftype == 'movies':
        for label, url in MOVIES_CATS:
            add_item(label, {'action': 'list_content', 'url': url, 'page': 1, 'site': 'lk21'})
    elif ftype == 'series':
        for label, url in SERIES_CATS:
            add_item(label, {'action': 'list_content', 'url': url, 'page': 1, 'site': 'series'})
    elif ftype == 'jav':
        for label, url in JAV_CATS:
            add_item(label, {'action': 'list_content', 'url': url, 'page': 1, 'site': 'jav'})
    xbmcplugin.endOfDirectory(HANDLE)

def list_content_menu(base_url, page, site):
    page = int(page)
    # Tentukan URL berdasarkan pola paginasi
    if page == 1:
        request_url = base_url
    else:
        if site == 'jav':
            request_url = f"{base_url}?page={page}"
        else: # lk21 & series
            # Bersihkan slash akhir jika ada
            clean_url = base_url.rstrip('/')
            request_url = f"{clean_url}/page/{page}/"

    if site == 'jav':
        items = list_jav_movies(request_url)
    else:
        items = list_lk21_movies(request_url)

    if not items and page > 1:
        xbmcgui.Dialog().notification("Info", "Halaman Terakhir", xbmcgui.NOTIFICATION_INFO, 2000)
        return

    for item in items:
        # Telenovela plays direct (usually), LK21/Series uses resolver
        action = 'play_jav' if site == 'jav' else 'play_lk21'
        add_item(item['title'], {'action': action, 'url': item['url']}, is_folder=False, thumbnail=item['thumb'])
    
    # Tombol Next Page Otomatis
    if items:
        add_item(f"Halaman Berikutnya ({page + 1})", {'action': 'list_content', 'url': base_url, 'page': page + 1, 'site': site})
        
    xbmcplugin.endOfDirectory(HANDLE)

def iptv_menu(url, mode='all'):
    channels = parse_m3u(url)
    
    # Filter untuk Sports jika diinginkan
    if mode == 'sports':
        # Prioritaskan beIN dan SPOTV
        priority = []
        others = []
        keywords = ["BEIN", "SPOTV", "FOX SPORTS", "ESPN", "STAR SPORTS", "PREMIER LEAGUE"]
        for ch in channels:
            if any(k in ch['title'].upper() for k in keywords):
                priority.append(ch)
            else:
                others.append(ch)
        # Tampilkan yang prioritas saja atau gabungan?
        # User minta "hanya stasiun terkenal", jadi kita tampilkan yang match saja.
        channels = priority if priority else others[:100]
    elif mode == 'indo':
        # Filter untuk Transvision/MNC style (General/Premium tags)
        premium_keywords = ["ANTV", "INDOSIAR", "TRANS", "METRO", "MNCTV", "SCTV", "RCTI", "GTV", "BTV"]
        priority = []
        for ch in channels:
            if any(k in ch['title'].upper() for k in premium_keywords):
                priority.append(ch)
        # Jika ada yang cocok tampilkan di atas
        channels = priority + [c for c in channels if c not in priority]

    for ch in channels:
        add_item(ch['title'], {'action': 'play_direct', 'url': ch['url']}, is_folder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def play(media_url):
    list_item = xbmcgui.ListItem(path=media_url)
    xbmcplugin.setResolvedUrl(HANDLE, True, list_item)

# --- Routing ---

def router(param_string):
    params = dict(urllib.parse.parse_qsl(param_string))
    action = params.get('action')

    if not action:
        main_menu()
    elif action == 'folder':
        folder_menu(params.get('type'))
    elif action == 'list_content':
        list_content_menu(params.get('url'), params.get('page'), params.get('site'))
    elif action == 'iptv':
        iptv_menu(params.get('url'), params.get('mode', 'all'))
    elif action == 'play_lk21':
        v_url = get_lk21_video(params.get('url'))
        if v_url:
            play(v_url)
    elif action == 'play_jav':
        v_url = get_jav_video(params.get('url'))
        if v_url:
            play(v_url)
    elif action == 'play_direct':
        # Default UA
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        v_url = f"{params.get('url')}|User-Agent={ua}"
        play(v_url)

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
            print(f"LK21 Sample: {list_lk21_movies(f'{LK21_URL}/latest')[:2]}")
    except Exception as e:
        if KODI:
            import traceback
            error_msg = traceback.format_exc()
            xbmcgui.Dialog().ok("Nyetplix Error", f"Terjadi kesalahan:\n{str(e)}\n\nKirimkan pesan ini ke developer.")
            xbmc.log(f"NYETPLIX ERROR: {error_msg}", xbmc.LOGERROR)
        else:
            raise e
