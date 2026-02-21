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
        command = ['curl', '-s', '-k', '-L', '-A', headers['User-Agent'], '-H', f"Referer: {BASE_URL}", url]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout if result.returncode == 0 else ""

# --- Scraper Logic ---

def list_lk21_movies(page_url):
    html = fetch(page_url)
    if not html:
        return [], None
        
    found = []
    # Temukan setiap blok <article> terlebih dahulu
    articles = re.findall(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    
    for art in articles:
        # Ekstrak Link: cari href pertama
        link = ""
        link_match = re.search(r'href=["\']([^"\']+)["\']', art)
        if link_match:
            link = link_match.group(1)
            if not link.startswith('http'):
                link = BASE_URL + link
        
        # Ekstrak Judul: cari di dalam h3
        title = "No Title"
        title_match = re.search(r'<h3[^>]*>([^<]+)</h3>', art)
        if title_match:
            title = title_match.group(1).strip()
            
        # Ekstrak Thumbnail: cari src pertama yang bukan placeholder
        thumb = ""
        # Mencari gambar yang biasanya mengandung poster atau slug di URL-nya
        img_matches = re.findall(r'src=["\']([^"\']+)["\']', art)
        for img in img_matches:
            if "poster" in img or "thumb" in img or "uploads" in img:
                thumb = img
                break
        if not thumb and img_matches:
            thumb = img_matches[0]
            
        if link and "/page/" not in link: # Hindari link paginasi masuk ke list film
            if not any(f['url'] == link for f in found):
                found.append({'title': title, 'url': link, 'thumb': thumb})
    
    # Cari link "Next Page" - cari teks "Next" atau simbol »
    next_page = None
    next_match = re.search(r'<a href=["\']([^"\']+)["\'][^>]*>(?:Next|&raquo;|»|Halaman Berikutnya)</a>', html)
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
