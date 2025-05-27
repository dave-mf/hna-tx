# Auto Deposit ETH, Grow, and Draw Hanafuda for HANA Network 

<img height="300" alt="image" src="https://github.com/user-attachments/assets/90dc4730-188d-4f64-b3ea-8fedc1400dff" />
<img height="300" alt="Screenshot 2024-11-17 at 06 06 43" src="https://github.com/user-attachments/assets/d126ec9d-9f09-41ac-a298-c1d36dba953d">
<img height="300" alt="image" src="https://github.com/user-attachments/assets/ef5586f1-5602-4674-9f4a-2a176072b0c7">

## Deskripsi
Bot otomatis untuk melakukan deposit ETH dan mengelola akun Hanafuda di jaringan Base, Optimism, dan Blast.

**Fitur:**
- Multi Account Support
- Auto Deposit dengan gas fee optimal
- Progress monitoring dan estimasi waktu
- Safety checks untuk transaksi besar
- Auto retry untuk transaksi yang gagal

## Instalasi

1. Clone repository:
```bash
git clone https://github.com/dpangestuw/HANA.git
cd HANA
```

2. Install dependencies yang diperlukan:
```bash
pip install web3 colorama requests
```

3. Siapkan file yang diperlukan:
   - Buat file `pvkey.txt` dan masukkan private key wallet Anda
   - Buat file `tokens.json` dengan format:
   ```json
   [
       {
           "name": "Account_1",
           "refresh_token": "YOUR_REFRESH_TOKEN"
       }
   ]
   ```

## Cara Mendapatkan Refresh Token
1. Register di https://hanafuda.hana.network/dashboard
2. Login dengan Google
3. Input Code **5147WQ**
4. Buka Developer Tools (F12)
5. Pilih tab Network
6. Cari request yang mengandung "securetoken"
7. Copy refresh_token dari response

## Penggunaan

1. Jalankan script deposit:
```bash
python3 hana.py (Linux)
```

2. Pilih jaringan:
   - 1: Base Mainnet
   - 2: OP Mainnet
   - 3: Blast Mainnet

3. Masukkan jumlah transaksi yang ingin dilakukan

## Fitur Tambahan
- **growmulti.py**: Untuk memilih kartu dan mendapatkan poin
- **drawmulti.py**: Untuk membuka koleksi kartu

## Catatan Penting
- Pastikan wallet memiliki cukup saldo ETH
- Gas fee dioptimalkan untuk low priority
- Script akan otomatis retry jika transaksi gagal
- Progress dan estimasi waktu akan ditampilkan

## Credits
Original Author: [dpangestuw](https://t.me/dpangestuw)
Additional Code Editor: [DaveMF & Cursor]

## Disclaimer
Gunakan script ini dengan bijak dan sesuai dengan Terms of Service dari HANA Network.

