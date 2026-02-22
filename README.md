# Nyetplix Kodi Repository

Selamat datang di **Nyetplix**! Ini adalah repository kustom untuk plugin Kodi Anda sendiri.

## Cara Menggunakan di Kodi 📺

> [!IMPORTANT]
> Untuk panduan instalasi lengkap dengan gambar dan langkah detail, silakan baca:
> **[PANDUAN INSTALASI (INSTALL.MD)](file:///Users/edypramono/Documents/EP/kodi/nyetplix/INSTALL.md)**

### Ringkasan Cepat:
1.  Buka **Settings** (ikon gerigi) di Kodi.
2.  Pilih **File Manager**.
3.  Klik **Add source**.
4.  Masukkan URL GitHub Pages Anda (misalnya: `https://edsprmn.github.io/nyetplix/`).
5.  Beri nama source ini `Nyetplix`.

### 2. Instal Repository
1.  Kembali ke menu utama Kodi, pilih **Add-ons**.
2.  Klik ikon kotak terbuka (Add-on Browser) di pojok kiri atas.
3.  Pilih **Install from zip file**.
4.  Pilih `Nyetplix`.
5.  Cari folder `repository.myrepo` dan instal file `.zip`-nya (atau instal dari folder jika Anda menggunakan mode development).

### 3. Instal Add-on (LK21)
1.  Setelah repository terinstal, pilih **Install from repository**.
2.  Pilih **My Custom Repository** (Nyetplix).
3.  Pilih **Video add-ons**.
4.  Pilih **LK21 Official** dan klik **Install**.

---

## Untuk Pengembang (Update Repo)

Setiap kali Anda menambah plugin baru, mengupdate kode, atau mengubah nomor versi, jalankan perintah "sakti" ini di terminal:

```bash
./update.sh "Pesan perubahan Anda"
```

Script ini akan otomatis melakukan:
1.  Menjalankan `generate_repo.py` untuk mengupdate file ZIP dan master list.
2.  Melakukan `git add` dan `git commit`.
3.  Melakukan `git push` ke GitHub.

Sangat praktis, bukan?

---

## 📺 Bonus: Menjadikan Kodi sebagai TV Kabel (PVR IPTV Simple Client)

Jika Anda ingin pengalaman menonton TV yang jauh lebih "nyata" dengan *Channel Guide (EPG)* layaknya TV berlangganan (seperti Indovision/First Media), Anda bisa menggunakan fitur bawaan Kodi. Berikut cara setup TV Lokal Indonesia:

1. Di menu utama Kodi, buka **Add-ons** > ikon kotak terbuka (kiri atas) > **Install from repository** > **PVR clients**.
2. Cari dan klik **PVR IPTV Simple Client**, lalu pilih **Install**.
3. Setelah terpasang, klik aplikasinya lagi dan pilih **Configure**.
4. Pada tab **General**:
   - Location: `Remote Path (Internet Address)`
   - M3U Play List URL: `https://iptv-org.github.io/iptv/countries/id.m3u`
5. Pada tab **EPG Settings**:
   - Location: `Remote Path (Internet Address)`
   - XMLTV URL: `https://iptv-org.github.io/epg/guides/id/transvision.co.id.epg.xml`
6. Klik **OK**, lalu akan ada prompt untuk merestart PVR. Jika tidak, **Restart Kodi** manual.
7. Sekarang Anda akan melihat menu **TV** di layar depan Kodi. Selamat menikmati siaran TV dengan jadwal yang rapi!
