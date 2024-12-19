from src.utils.performance import measure_performance

@measure_performance
def rod_cutting_iterative(prices, n):
    """
    Solusi iteratif murni untuk Rod Cutting Problem tanpa menggunakan dynamic programming.
    Menggunakan pendekatan brute force dengan nested loops untuk mencoba semua kombinasi
    pemotongan yang mungkin.
    """
    if n <= 0:
        return 0
    
    def get_combinations(length, current_cuts=[]):
        """Helper function untuk menghasilkan semua kombinasi pemotongan yang mungkin"""
        if length == 0:
            return [current_cuts]
        combinations = []
        for i in range(1, length + 1):
            combinations.extend(get_combinations(length - i, current_cuts + [i]))
        return combinations
    
    # Dapatkan semua kombinasi pemotongan yang mungkin
    all_combinations = get_combinations(n)
    
    # Hitung nilai untuk setiap kombinasi
    max_value = float('-inf')
    for cuts in all_combinations:
        current_value = sum(prices[i-1] for i in cuts)
        max_value = max(max_value, current_value)
    
    return max_value