# Rod Cutting Problem

## Deskripsi Masalah
Rod Cutting Problem adalah masalah optimasi klasik di mana kita memiliki sebuah batang (rod) dengan panjang n dan daftar harga untuk setiap panjang potongan. Tujuannya adalah untuk memotong batang tersebut sedemikian rupa sehingga menghasilkan nilai maksimum.

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

#### b. Iterative dengan Brute Force
- Mencoba semua kombinasi pemotongan yang mungkin
- Tidak menggunakan memoization atau tabulasi
- Kompleksitas waktu: O(n * 2^n)
- Menunjukkan pendekatan iteratif murni

### 2. Implementasi dengan Dynamic Programming

#### a. Recursive dengan Memoization (Top-down DP)
- Menggunakan DP dengan pendekatan top-down
- Menyimpan hasil perhitungan dalam dictionary
- Menghindari perhitungan ulang subproblem
- Kompleksitas waktu: O(n²)
- Trade-off antara waktu dan memori

#### b. Bottom-up DP
- Menggunakan DP dengan pendekatan bottom-up
- Membangun solusi dari subproblem terkecil
- Menyimpan hasil dalam array
- Kompleksitas waktu: O(n²)
- Lebih efisien dalam penggunaan memori dibanding top-down

### 3. Implementasi dengan Optimasi

#### Space Optimized DP
- Berbasis Bottom-up DP
- Mengoptimalkan penggunaan memori
- Hanya menggunakan satu array untuk menyimpan hasil
- Kompleksitas waktu tetap O(n²)
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

## Implementasi

Proyek ini membandingkan lima implementasi berbeda dari Rod Cutting Problem:

### 1. Pure Recursive (Brute Force)
- Menggunakan rekursi murni tanpa optimasi
- Menghitung ulang subproblem yang sama berkali-kali
- Kompleksitas Waktu: O(2^n)
- Kompleksitas Ruang: O(n) untuk call stack

```python
def rod_cutting_pure_recursive(prices, n):
    if n <= 0:
        return 0
    max_val = float('-inf')
    for i in range(1, n + 1):
        max_val = max(max_val, prices[i-1] + rod_cutting_pure_recursive(prices, n - i))
    return max_val
```

### 2. Iterative (Brute Force)
- Menggunakan iterasi untuk mencoba semua kombinasi pemotongan
- Tidak menyimpan hasil perhitungan sebelumnya
- Kompleksitas Waktu: O(n * 2^n)
- Kompleksitas Ruang: O(2^n) untuk menyimpan kombinasi

```python
def rod_cutting_iterative(prices, n):
    if n <= 0:
        return 0
    
    def get_combinations(length, current_cuts=[]):
        if length == 0:
            return [current_cuts]
        combinations = []
        for i in range(1, length + 1):
            combinations.extend(get_combinations(length - i, current_cuts + [i]))
        return combinations
    
    all_combinations = get_combinations(n)
    max_value = float('-inf')
    for cuts in all_combinations:
        current_value = sum(prices[i-1] for i in cuts)
        max_value = max(max_value, current_value)
    return max_value
```

### 3. Recursive with Memoization (Top-down DP)
- Menggunakan rekursi dengan memoization
- Menyimpan hasil perhitungan untuk menghindari perhitungan ulang
- Kompleksitas Waktu: O(n²)
- Kompleksitas Ruang: O(n) untuk memo dan call stack

```python
def rod_cutting_recursive(prices, n, memo=None):
    if memo is None:
        memo = {}
    if n <= 0:
        return 0
    if n in memo:
        return memo[n]
    max_val = float('-inf')
    for i in range(1, n + 1):
        max_val = max(max_val, prices[i-1] + rod_cutting_recursive(prices, n - i, memo))
    memo[n] = max_val
    return max_val
```

### 4. Bottom-up DP
- Menggunakan tabulasi untuk membangun solusi dari bawah
- Menghindari overhead rekursi
- Kompleksitas Waktu: O(n²)
- Kompleksitas Ruang: O(n)

```python
def rod_cutting_dp(prices, n):
    dp = [0 for _ in range(n + 1)]
    for i in range(1, n + 1):
        max_val = float('-inf')
        for j in range(1, i + 1):
            max_val = max(max_val, prices[j-1] + dp[i-j])
        dp[i] = max_val
    return dp[n]
```

### 5. Space Optimized DP
- Optimasi dari Bottom-up DP
- Menggunakan struktur data minimal
- Kompleksitas Waktu: O(n²)
- Kompleksitas Ruang: O(n)

```python
def rod_cutting_dp_space_optimized(prices, n):
    dp = [0 for _ in range(n + 1)]
    for i in range(1, n + 1):
        max_val = float('-inf')
        for j in range(1, i + 1):
            max_val = max(max_val, prices[j-1] + dp[i-j])
        dp[i] = max_val
    return dp[n]
```

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
1. Pendekatan brute force (Pure Recursive dan Iterative) menunjukkan pertumbuhan waktu eksponensial
2. Dynamic Programming memberikan peningkatan kinerja yang signifikan
3. Space Optimized DP memiliki kinerja serupa dengan Bottom-up DP

### Penggunaan Memori
1. Pure Recursive menggunakan memori untuk call stack
2. Iterative menggunakan memori untuk menyimpan kombinasi
3. Pendekatan DP menggunakan memori tambahan untuk menyimpan hasil
4. Space Optimized DP menunjukkan penggunaan memori yang paling efisien

### Rekomendasi Penggunaan
1. Input kecil (n ≤ 10): Semua implementasi dapat digunakan
2. Input menengah (10 < n ≤ 20): Gunakan pendekatan DP
3. Input besar (n > 20): Gunakan Space Optimized DP
4. Memori terbatas: Pilih Space Optimized DP
5. Debugging/pemahaman: Gunakan Bottom-up DP

## Kontribusi
Silakan berkontribusi dengan membuat pull request atau melaporkan issues.
