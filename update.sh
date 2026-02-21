#!/bin/bash

# Script otomatisasi Update Repository Nyetplix
# Penggunaan: ./update.sh "Pesan commit Anda"

MESSAGE=${1:-"Update repository dan addons"}

echo "--- 1. Menghasilkan Master List dan File ZIP ---"
python3 generate_repo.py

if [ $? -eq 0 ]; then
    echo "--- 2. Mengirim Perubahan ke GitHub ---"
    git add .
    git commit -m "$MESSAGE"
    git push origin main
    
    echo ""
    echo "BERHASIL! Repository Nyetplix Anda telah diperbarui di GitHub."
    echo "Tunggu 1-2 menit sebelum mengecek update di Kodi."
else
    echo "ERROR: Gagal menjalankan generate_repo.py. Periksa kode Python Anda."
    exit 1
fi
