from src.utils.performance import measure_performance

@measure_performance
def rod_cutting_iterative(prices, n, allowed_lengths=None):
    """
    Implementasi rod cutting dengan pendekatan iteratif murni (brute force).
    Menggunakan iterasi untuk menghasilkan semua kemungkinan kombinasi potongan.
    
    Args:
        prices (list): Daftar harga untuk setiap panjang potongan (0-indexed)
        n (int): Panjang batang yang akan dipotong
        allowed_lengths (list, optional): Daftar panjang potongan yang diperbolehkan.
            Jika None, semua panjang dari 1 sampai n diperbolehkan.
    
    Returns:
        tuple: (nilai_maksimal, daftar_potongan)
            - nilai_maksimal (int): Nilai maksimal yang bisa didapat
            - daftar_potongan (list): Urutan panjang potongan yang menghasilkan nilai maksimal
    
    Perbedaan dengan DP:
        - Tidak menyimpan hasil subproblem
        - Mencoba semua kombinasi potongan yang mungkin
        - Kompleksitas waktu lebih tinggi O(n^n) vs O(n²) pada DP
    """
    if n <= 0:
        return 0, []
    
    # Tentukan panjang yang akan dicoba
    if allowed_lengths:
        lengths_to_try = [l for l in allowed_lengths if l <= n]
    else:
        lengths_to_try = range(1, n + 1)
    
    # Inisialisasi nilai maksimum dan potongan terbaik
    max_val = float('-inf')
    best_cuts = []
    
    # Stack untuk menyimpan state: (sisa_panjang, potongan_sekarang)
    stack = [(n, [])]
    
    # Iterasi menggunakan stack untuk menggantikan rekursi
    while stack:
        remaining, current_cuts = stack.pop()
        
        # Jika sisa panjang 0, evaluasi kombinasi potongan saat ini
        if remaining == 0:
            current_value = sum(prices[i-1] for i in current_cuts)
            if current_value > max_val:
                max_val = current_value
                best_cuts = current_cuts[:]
            continue
        
        # Coba semua kemungkinan potongan untuk sisa panjang
        for length in lengths_to_try:
            if length <= remaining:
                # Tambahkan state baru ke stack
                stack.append((remaining - length, current_cuts + [length]))
    
    return max_val if max_val != float('-inf') else 0, best_cuts