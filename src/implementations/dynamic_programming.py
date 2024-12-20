from src.utils.performance import measure_performance

@measure_performance
def rod_cutting_dp(prices, n, allowed_lengths=None):
    """
    Implementasi rod cutting dengan pendekatan dynamic programming bottom-up (tabulasi).
    
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
        - Waktu: O(n²) karena menggunakan nested loop
        - Ruang: O(n) untuk array dp dan cuts
    
    Pendekatan:
        1. Menggunakan tabulasi (bottom-up) untuk membangun solusi dari subproblem terkecil
        2. Menyimpan hasil optimal dan potongan untuk setiap panjang dalam array
        3. Menghindari overhead rekursi dengan pendekatan iteratif
    """
    if n <= 0:
        return 0, []
    
    # Inisialisasi tabel DP untuk menyimpan nilai maksimal
    dp = [0] * (n + 1)
    # Inisialisasi array untuk tracking pola potong optimal
    cuts = [[] for _ in range(n + 1)]
    
    # Tentukan panjang yang akan dicoba berdasarkan allowed_lengths
    if allowed_lengths:
        lengths_to_try = [l for l in allowed_lengths if l <= n]
    else:
        lengths_to_try = range(1, n + 1)
    
    # Bangun solusi dari bawah ke atas untuk setiap panjang
    for i in range(1, n + 1):
        for length in lengths_to_try:
            if length <= i:
                # Hitung nilai dari potongan saat ini + nilai optimal sisa batang
                current_value = prices[length-1] + dp[i-length]
                # Update jika mendapat nilai yang lebih baik
                if current_value > dp[i]:
                    dp[i] = current_value
                    cuts[i] = cuts[i-length] + [length]
    
    return dp[n], cuts[n]

@measure_performance
def rod_cutting_dp_space_optimized(prices, n, allowed_lengths=None):
    """
    Implementasi rod cutting dengan pendekatan dynamic programming yang dioptimasi untuk penggunaan memori.
    
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
        - Waktu: O(n²) karena menggunakan nested loop
        - Ruang: O(n) untuk array dp dan best_cuts
    
    Optimasi Memori:
        1. Hanya menyimpan satu angka untuk setiap panjang dalam best_cuts
        2. Rekonstruksi potongan optimal dilakukan di akhir
        3. Mengurangi penggunaan memori dari O(n²) menjadi O(n)
    """
    if n <= 0:
        return 0, []
    
    # Tentukan panjang yang akan dicoba
    if allowed_lengths:
        lengths_to_try = [l for l in allowed_lengths if l <= n]
    else:
        lengths_to_try = range(1, n + 1)
    
    # Array untuk menyimpan nilai maksimum untuk setiap panjang
    dp = [0] * (n + 1)
    # Array untuk menyimpan panjang potongan optimal untuk setiap panjang
    best_cuts = [0] * (n + 1)
    
    # Iterasi untuk membangun solusi optimal
    for i in range(1, n + 1):
        for length in lengths_to_try:
            if length <= i:
                # Hitung nilai dari potongan saat ini + nilai optimal sisa batang
                current_value = prices[length-1] + dp[i-length]
                # Update jika mendapat nilai yang lebih baik
                if current_value > dp[i]:
                    dp[i] = current_value
                    best_cuts[i] = length
    
    # Rekonstruksi urutan potongan optimal
    cuts = []
    remaining = n
    while remaining > 0:
        cut = best_cuts[remaining]
        cuts.append(cut)
        remaining -= cut
    
    return dp[n], cuts