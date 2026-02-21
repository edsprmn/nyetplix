import sys
import re
import urllib.request
import urllib.parse
import json
import subprocess

# URL Dasar
BASE_URL = "https://tv8.lk21official.cc"
IPTV_INDO_URL = "https://raw.githubusercontent.com/mgi24/tvdigital/main/iptv_indonesia.m3u"
IPTV_SPORTS_URL = "https://iptv-org.github.io/iptv/categories/sports.m3u"

def get_html(url):
    command = [
        'curl', '-s', '-L',
        '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        '-H', f'Referer: {BASE_URL}',
        url
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout if result.returncode == 0 else ""

def list_lk21_movies(page_url):
    html = get_html(page_url)
    pattern = r'<a href="([^"]+)" itemprop="url">.*?<h3 class="poster-title" itemprop="name">([^<]+)</h3>.*?<img.*?src="([^"]+)"'
    movies = re.findall(pattern, html, re.DOTALL)
    
    found = []
    for link, title, thumb in movies:
        full_link = link if link.startswith('http') else BASE_URL + link
        found.append({'title': title.strip(), 'url': full_link, 'thumb': thumb, 'type': 'movie'})
    return found

def get_lk21_video(movie_url):
    html = get_html(movie_url)
    player_pattern = r'href="(https://playeriframe.sbs/iframe/[^"]+)"'
    players = re.findall(player_pattern, html)
    return players[0] if players else None

def parse_m3u(url):
    print(f"Parsing M3U dari: {url}")
    content = get_html(url)
    channels = []
    # Simple M3U Parser
    # #EXTINF:-1 tvg-logo="url" group-title="group",Name
    # url
    pattern = r'#EXTINF:.*?,(.*?)\n(http.*?)$'
    matches = re.findall(pattern, content, re.MULTILINE)
    
    for name, stream_url in matches[:40]: # Ambil 40 saja agar tidak lambat
        channels.append({
            'title': name.strip(),
            'url': stream_url.strip(),
            'thumb': "", # Bisa di-improve dengan regex tvg-logo
            'type': 'live'
        })
    return channels

def simulator():
    print("=== NYETPLIX KODI ADDON SIMULATOR ===")
    print("1. Movies (LK21)")
    print("2. TV Indonesia (Live)")
    print("3. Sports (Live)")
    
    choice = input("Pilih Menu: ")
    
    if choice == "1":
        items = list_lk21_movies(f"{BASE_URL}/latest")
        for i, item in enumerate(items[:5]):
            print(f"[{i+1}] {item['title']}")
            if input("Putar? (y/n): ") == "y":
                print(f"Streaming link: {get_lk21_video(item['url'])}")
    elif choice == "2":
        items = parse_m3u(IPTV_INDO_URL)
        for i, item in enumerate(items[:10]):
            print(f"[{i+1}] {item['title']} -> {item['url']}")
    elif choice == "3":
        items = parse_m3u(IPTV_SPORTS_URL)
        for i, item in enumerate(items[:10]):
            print(f"[{i+1}] {item['title']} -> {item['url']}")

if __name__ == "__main__":
    # Jika dijalankan di Kodi, gunakan logika Kodi. Jika di terminal, gunakan simulator.
    if len(sys.argv) > 1 and sys.argv[1].startswith("plugin://"):
        # Logika Kodi (akan diimplementasikan jika user ingin mencoba di aplikasi)
        pass
    else:
        simulator()
