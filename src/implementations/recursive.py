from src.utils.performance import measure_performance

@measure_performance
def rod_cutting_pure_recursive(prices, n, allowed_lengths=None):
    """
    Implementasi rod cutting dengan pendekatan rekursif murni (brute force).
    Mencoba semua kemungkinan kombinasi potongan secara rekursif.
    
    Args:
        prices (list): Daftar harga untuk setiap panjang potongan (0-indexed)
        n (int): Panjang batang yang akan dipotong
        allowed_lengths (list, optional): Daftar panjang potongan yang diperbolehkan.
            Jika None, semua panjang dari 1 sampai n diperbolehkan.
    
    Returns:
        tuple: (nilai_maksimal, daftar_potongan)
            - nilai_maksimal (int): Nilai maksimal yang bisa didapat
            - daftar_potongan (list): Urutan panjang potongan yang menghasilkan nilai maksimal
    
    Kompleksitas:
        - Waktu: O(2^n) karena setiap panjang memiliki 2 pilihan (potong atau tidak)
        - Ruang: O(n) untuk call stack rekursi
    
    Karakteristik:
        - Menggunakan rekursi murni tanpa memoization
        - Menghitung ulang subproblem yang sama berkali-kali
        - Tidak efisien untuk input besar
    """
    def _recursive(length):
        # Basis case: jika panjang 0 atau negatif
        if length <= 0:
            return 0, []
        
        max_val = float('-inf')
        best_cuts = []
        
        # Tentukan panjang yang akan dicoba
        if allowed_lengths:
            lengths_to_try = [l for l in allowed_lengths if l <= length]
        else:
            lengths_to_try = range(1, length + 1)
        
        # Coba setiap kemungkinan potongan pertama
        for i in lengths_to_try:
            # Rekursif untuk sisa panjang
            val, cuts = _recursive(length - i)
            # Hitung nilai total dengan potongan saat ini
            current_value = prices[i-1] + val
            # Update jika mendapat nilai yang lebih baik
            if current_value > max_val:
                max_val = current_value
                best_cuts = [i] + cuts
        
        return (max_val if max_val != float('-inf') else 0), best_cuts
    
    return _recursive(n)

@measure_performance
def rod_cutting_recursive(prices, n, allowed_lengths=None, memo=None):
    """
    Implementasi rod cutting dengan pendekatan rekursif dan memoization (top-down DP).
    Menggunakan dictionary untuk menyimpan hasil perhitungan subproblem.
    
    Args:
        prices (list): Daftar harga untuk setiap panjang potongan (0-indexed)
        n (int): Panjang batang yang akan dipotong
        allowed_lengths (list, optional): Daftar panjang potongan yang diperbolehkan.
            Jika None, semua panjang dari 1 sampai n diperbolehkan.
        memo (dict, optional): Dictionary untuk menyimpan hasil perhitungan.
            Key: panjang batang, Value: tuple (nilai_maksimal, potongan_optimal)
    
    Returns:
        tuple: (nilai_maksimal, daftar_potongan)
            - nilai_maksimal (int): Nilai maksimal yang bisa didapat
            - daftar_potongan (list): Urutan panjang potongan yang menghasilkan nilai maksimal
    
    Kompleksitas:
        - Waktu: O(n²) karena setiap subproblem dihitung tepat satu kali
        - Ruang: O(n) untuk memoization dictionary dan call stack
    
    Karakteristik:
        - Menggunakan memoization untuk menghindari perhitungan berulang
        - Pendekatan top-down dynamic programming
        - Lebih efisien dibanding rekursi murni
    """
    def _recursive(length, memo):
        # Basis case: jika panjang 0 atau negatif
        if length <= 0:
            return 0, []
        
        # Cek apakah hasil sudah ada di memo
        if length in memo:
            return memo[length]
        
        max_val = float('-inf')
        best_cuts = []
        
        # Tentukan panjang yang akan dicoba
        if allowed_lengths:
            lengths_to_try = [l for l in allowed_lengths if l <= length]
        else:
            lengths_to_try = range(1, length + 1)
        
        # Coba setiap kemungkinan potongan pertama
        for i in lengths_to_try:
            # Rekursif untuk sisa panjang (hasil akan di-cache)
            val, cuts = _recursive(length - i, memo)
            # Hitung nilai total dengan potongan saat ini
            current_value = prices[i-1] + val
            # Update jika mendapat nilai yang lebih baik
            if current_value > max_val:
                max_val = current_value
                best_cuts = [i] + cuts
        
        # Simpan hasil ke memo sebelum return
        result = ((max_val if max_val != float('-inf') else 0), best_cuts)
        memo[length] = result
        return result
    
    if memo is None:
        memo = {}
    return _recursive(n, memo)