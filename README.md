# Nyetplix Kodi Repository

Selamat datang di **Nyetplix**! Ini adalah repository kustom untuk plugin Kodi Anda sendiri.

## Cara Menggunakan di Kodi

### 1. Tambahkan Source di Kodi
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

Setiap kali Anda menambah plugin baru atau mengupdate kode, jalankan script berikut di folder ini:

```bash
python3 generate_repo.py
```

Lalu **push** perubahan tersebut ke GitHub agar repository di Kodi Anda ikut terupdate.
