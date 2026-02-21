import sys
import re
import urllib.request
import urllib.parse
import json

# URL Dasar Website
BASE_URL = "https://tv8.lk21official.cc"

import subprocess

def get_html(url):
    command = [
        'curl', '-s', '-L',
        '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        '-H', f'Referer: {BASE_URL}',
        url
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(f"Curl failed with error: {result.stderr}")

def list_movies(page_url):
    print(f"Mengambil daftar film dari: {page_url}")
    html = get_html(page_url)
    
    # Pattern baru berdasarkan HTML asli:
    # <a href="([^"]+)" itemprop="url">
    # <h3 class="poster-title" itemprop="name">([^<]+)</h3>
    # <img ... src="([^"]+)"
    pattern = r'<a href="([^"]+)" itemprop="url">.*?<h3 class="poster-title" itemprop="name">([^<]+)</h3>.*?<img.*?src="([^"]+)"'
    movies = re.findall(pattern, html, re.DOTALL)
    
    found_movies = []
    for link, title, thumb in movies:
        full_link = link if link.startswith('http') else BASE_URL + link
        found_movies.append({
            'title': title.strip(),
            'url': full_link,
            'thumb': thumb
        })
    return found_movies

def get_video_sources(movie_url):
    print(f"Mencari sumber video untuk: {movie_url}")
    html = get_html(movie_url)
    
    # Berdasarkan riset terbaru: Link player ada di tag <a> yang mengarah ke playeriframe.sbs
    # Polanya: <a ... href="https://playeriframe.sbs/iframe/..." ...>
    player_pattern = r'href="(https://playeriframe.sbs/iframe/[^"]+)"'
    players = re.findall(player_pattern, html)
    
    if players:
        # Kita ambil yang pertama saja (biasanya P2P atau Hydrax)
        print(f"Ditemukan {len(players)} player.")
        return players[0]
        
    return None

def main():
    print("=== LK21 KODI ADDON SIMULATOR ===")
    
    # 1. Ambil List Film di halaman depan (Hanya contoh halaman terbaru)
    latest_url = f"{BASE_URL}/latest"
    try:
        movies = list_movies(latest_url)
        
        if not movies:
            print("Gagal mengambil daftar film. Cek koneksi atau website mungkin berubah.")
            return

        # Ambil 3 film pertama saja untuk contoh
        for i, movie in enumerate(movies[:3]):
            print(f"\n[{i+1}] {movie['title']}")
            print(f"    Info Link: {movie['url']}")
            
            # 2. Coba bedah sumber videonya
            video_link = get_video_sources(movie['url'])
            if video_link:
                print(f"    HASIL SCRAPE VIDEO: {video_link}")
            else:
                print("    HASIL: Gagal menemukan link video (butuh analisa lanjutan).")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
