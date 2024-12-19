from src.utils.performance import measure_performance

@measure_performance
def rod_cutting_dp(prices, n, allowed_lengths=None):
    """
    Implementasi rod cutting dengan pendekatan dynamic programming
    dengan opsi pembatasan panjang potong yang diperbolehkan
    """
    if n <= 0:
        return 0, []
    
    # Inisialisasi tabel DP
    dp = [0] * (n + 1)
    cuts = [[] for _ in range(n + 1)]
    
    # Tentukan panjang yang akan dicoba
    if allowed_lengths:
        lengths_to_try = [l for l in allowed_lengths if l <= n]
    else:
        lengths_to_try = range(1, n + 1)
    
    # Isi tabel DP
    for i in range(1, n + 1):
        for length in lengths_to_try:
            if length <= i:
                current_value = prices[length-1] + dp[i-length]
                if current_value > dp[i]:
                    dp[i] = current_value
                    cuts[i] = cuts[i-length] + [length]
    
    return dp[n], cuts[n]

@measure_performance
def rod_cutting_dp_space_optimized(prices, n, allowed_lengths=None):
    """
    Implementasi rod cutting dengan pendekatan dynamic programming yang dioptimasi untuk penggunaan memori
    dengan opsi pembatasan panjang potong yang diperbolehkan
    """
    if n <= 0:
        return 0, []
    
    # Tentukan panjang yang akan dicoba
    if allowed_lengths:
        lengths_to_try = [l for l in allowed_lengths if l <= n]
    else:
        lengths_to_try = range(1, n + 1)
    
    # Array untuk menyimpan nilai maksimum
    dp = [0] * (n + 1)
    # Array untuk tracking pola potong optimal
    cuts = [[] for _ in range(n + 1)]
    
    # Iterasi untuk setiap panjang
    for i in range(1, n + 1):
        for length in lengths_to_try:
            if length <= i:
                current_value = prices[length-1] + dp[i-length]
                if current_value > dp[i]:
                    dp[i] = current_value
                    cuts[i] = cuts[i-length] + [length]
    
    return dp[n], cuts[n]

@measure_performance
def rod_cutting_dp_with_cuts(prices, n, allowed_lengths=None):
    """
    Implementasi rod cutting dengan pendekatan dynamic programming
    dengan opsi pembatasan panjang potong yang diperbolehkan
    """
    if n <= 0:
        return 0, []
    
    # Inisialisasi tabel DP
    dp = [0] * (n + 1)
    cuts = [[] for _ in range(n + 1)]
    
    # Tentukan panjang yang akan dicoba
    if allowed_lengths:
        lengths_to_try = [l for l in allowed_lengths if l <= n]
    else:
        lengths_to_try = range(1, n + 1)
    
    # Isi tabel DP
    for i in range(1, n + 1):
        for length in lengths_to_try:
            if length <= i:
                current_value = prices[length-1] + dp[i-length]
                if current_value > dp[i]:
                    dp[i] = current_value
                    cuts[i] = cuts[i-length] + [length]
    
    return dp[n], cuts[n]