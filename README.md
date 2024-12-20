# Rod Cutting Problem

## Deskripsi Masalah
Rod Cutting Problem adalah masalah optimasi klasik di mana kita memiliki sebuah batang (rod) dengan panjang n dan daftar harga untuk setiap panjang potongan. Tujuannya adalah untuk memotong batang tersebut sedemikian rupa sehingga menghasilkan nilai maksimum.

## Implementasi

Dalam proyek ini, kami menyediakan beberapa implementasi berbeda untuk menyelesaikan Rod Cutting Problem:

### 1. Pure Recursive (Brute Force)
- Menggunakan rekursi murni tanpa optimasi
- Mencoba semua kemungkinan kombinasi potongan
- Kompleksitas Waktu: O(2^n)
- Kompleksitas Ruang: O(n) untuk call stack

```python
def rod_cutting_pure_recursive(prices, n):
    if n <= 0:
        return 0, []
    
    max_val = float('-inf')
    best_cuts = []
    
    for i in range(1, n + 1):
        val, cuts = rod_cutting_pure_recursive(prices, n - i)
        current_value = prices[i-1] + val
        if current_value > max_val:
            max_val = current_value
            best_cuts = [i] + cuts
    
    return (max_val if max_val != float('-inf') else 0), best_cuts
```

### 2. Recursive with Memoization (Top-down DP)
- Menggunakan rekursi dengan memoization
- Menyimpan hasil perhitungan untuk menghindari perhitungan ulang
- Kompleksitas Waktu: O(n²)
- Kompleksitas Ruang: O(n) untuk memo dan call stack

```python
def rod_cutting_memoization(prices, n, memo=None):
    if memo is None:
        memo = {}
    if n <= 0:
        return 0, []
    
    if n in memo:
        return memo[n]
    
    max_val = float('-inf')
    best_cuts = []
    
    for i in range(1, n + 1):
        val, cuts = rod_cutting_memoization(prices, n - i, memo)
        current_value = prices[i-1] + val
        if current_value > max_val:
            max_val = current_value
            best_cuts = [i] + cuts
    
    result = ((max_val if max_val != float('-inf') else 0), best_cuts)
    memo[n] = result
    return result
```

### 3. Space-Optimized Bottom-up Dynamic Programming
- Menggunakan tabulasi untuk membangun solusi dari bawah dengan optimasi memori
- Hanya menyimpan nilai optimal dan satu potongan untuk setiap panjang
- Kompleksitas Waktu: O(n²)
- Kompleksitas Ruang: O(n)

```python
def rod_cutting_dp_space_optimized(prices, n):
    if n <= 0:
        return 0, []
    
    dp = [0] * (n + 1)
    best_cuts = [0] * (n + 1)
    
    for i in range(1, n + 1):
        for j in range(1, i + 1):
            current_value = prices[j-1] + dp[i-j]
            if current_value > dp[i]:
                dp[i] = current_value
                best_cuts[i] = j
    
    cuts = []
    remaining = n
    while remaining > 0:
        cut = best_cuts[remaining]
        cuts.append(cut)
        remaining -= cut
    
    return dp[n], cuts
```

## Perbandingan Kompleksitas

| Implementasi | Kompleksitas Waktu | Kompleksitas Ruang | Karakteristik |
|--------------|-------------------|-------------------|---------------|
| Pure Recursive | O(2^n) | O(n) | Sederhana tapi tidak efisien |
| Recursive + Memo | O(n²) | O(n) | Efisien dengan overhead rekursi |
| Space-Optimized DP | O(n²) | O(n) | Paling efisien dalam penggunaan memori |

## Penggunaan

Setiap implementasi menerima parameter yang sama:
- `prices`: List harga untuk setiap panjang potongan (0-indexed)
- `n`: Panjang batang yang akan dipotong
- `allowed_lengths` (opsional): List panjang potongan yang diperbolehkan

Dan mengembalikan tuple:
- `nilai_maksimal`: Nilai maksimal yang bisa didapat
- `daftar_potongan`: Urutan panjang potongan yang menghasilkan nilai maksimal

## Struktur Proyek
```
rod_cutting/
├── app.py                      # File utama untuk menjalankan pengujian
├── README.md                   # Dokumentasi proyek
├── src/                        # Source code
│   ├── implementations/        # Implementasi algoritma
│   │   ├── __init__.py
│   │   ├── recursive.py       # Implementasi rekursif
│   │   ├── iterative.py       # Implementasi iteratif
│   │   └── dynamic_programming.py  # Implementasi DP
│   └── utils/                 # Utilitas
│       ├── __init__.py
│       ├── performance.py     # Pengukuran kinerja
│       └── test_utils.py      # Fungsi pengujian
└── results/                   # Hasil analisis
    └── performance_analysis_*.md
```

## Instalasi
```bash
# Install dependencies
pip install -r requirements.txt
```

## Cara Penggunaan

1. Jalankan pengujian performa dengan test case otomatis:
```bash
python app.py
```
```bash
Rod Cutting Analysis
1. Gunakan test case otomatis
2. Input manual
Pilih mode (1/2): 1
```

2. Pengujian performa dengan input manual:
```bash
python app.py
```
```bash
Rod Cutting Problem - Input Data
================================
Masukkan ukuran batang yang akan diuji
(Pisahkan dengan koma, contoh: 5,7,10,13)
Ukuran batang: 5,7,11,13,17
Masukkan panjang potong yang diperbolehkan
(Pisahkan dengan koma, contoh: 2,5,7)
Tekan Enter untuk mengizinkan semua panjang
Panjang potong: 2,3,4
Masukkan harga untuk setiap panjang batang
Masukkan harga hanya untuk panjang yang diperbolehkan:
Panjang 2: 12
Panjang 3: 20
Panjang 4: 30
```

3. Hasil analisis akan disimpan di folder `results/` dengan format nama `performance_analysis_YYYYMMDD_HHMMSS.md`

## Kategorisasi Implementasi

Implementasi dalam proyek ini dapat dikategorikan menjadi tiga kelompok berdasarkan teknik yang digunakan:

### 1. Implementasi Tanpa Dynamic Programming (Brute Force)

#### a. Pure Recursive
- Menggunakan rekursi murni
- Menghitung ulang subproblem yang sama berkali-kali
- Tidak ada penyimpanan hasil perhitungan
- Kompleksitas waktu: O(2^n)
- Cocok untuk pembelajaran konsep dasar

### 2. Implementasi dengan Dynamic Programming

#### a. Recursive dengan Memoization (Top-down DP)
- Menggunakan DP dengan pendekatan top-down
- Menyimpan hasil perhitungan dalam dictionary
- Menghindari perhitungan ulang subproblem
- Kompleksitas waktu: O(n²)
- Trade-off antara waktu dan memori

### 3. Implementasi dengan Optimasi

#### Space Optimized DP
- Menggunakan DP dengan pendekatan bottom-up
- Membangun solusi dari subproblem terkecil
- Mengoptimalkan penggunaan memori
- Hanya menggunakan satu array untuk menyimpan hasil
- Kompleksitas waktu tetap O(n²)
- Lebih efisien dalam penggunaan memori dibanding top-down
- Overhead memori minimal

### Perbedaan Utama

1. **Antara DP dan Non-DP**:
   - DP menyimpan hasil perhitungan (memoization atau tabulasi)
   - DP menghindari perhitungan ulang subproblem
   - DP memiliki kompleksitas waktu yang lebih baik (O(n²) vs O(2^n))

2. **Antara Optimasi dan DP Biasa**:
   - Optimasi fokus pada efisiensi penggunaan memori
   - Menyederhanakan struktur data yang digunakan
   - Mempertahankan efisiensi waktu eksekusi

## Analisis Performa

Setiap file analisis di folder `results/` mencakup:

1. **Hasil Perhitungan dan Kinerja**
   - Nilai optimal yang ditemukan
   - Waktu eksekusi
   - Penggunaan memori

2. **Perbandingan Waktu Eksekusi**
   - Waktu absolut
   - Waktu relatif terhadap implementasi tercepat

3. **Perbandingan Penggunaan Memori**
   - Penggunaan memori absolut
   - Penggunaan memori relatif

4. **Analisis Kompleksitas**
   - Kompleksitas waktu teoretis
   - Kompleksitas ruang teoretis
   - Penjelasan dan keterangan

## Kesimpulan dan Rekomendasi

### Waktu Eksekusi
1. Pendekatan brute force (Pure Recursive) menunjukkan pertumbuhan waktu eksponensial
2. Dynamic Programming memberikan peningkatan kinerja yang signifikan
3. Space Optimized DP memiliki kinerja yang jauh lebih baik

### Penggunaan Memori
1. Pure Recursive menggunakan memori untuk call stack
2. Pendekatan DP menggunakan memori tambahan untuk menyimpan hasil
4. Space Optimized DP menunjukkan penggunaan memori yang paling efisien

### Rekomendasi Penggunaan
1. Input kecil (n ≤ 10): Semua implementasi dapat digunakan
2. Input menengah (10 < n ≤ 20): Gunakan pendekatan DP
3. Input besar (n > 20): Gunakan Space Optimized DP
4. Memori terbatas: Pilih Space Optimized DP
5. Debugging/pemahaman: Gunakan Bottom-up DP

## Kontribusi
Silakan berkontribusi dengan membuat pull request atau melaporkan issues.
