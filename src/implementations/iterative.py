from src.utils.performance import measure_performance

@measure_performance
def rod_cutting_iterative(prices, n, allowed_lengths=None):
    """
    Implementasi rod cutting dengan pendekatan iteratif (brute force)
    dengan opsi pembatasan panjang potong yang diperbolehkan
    """
    if n <= 0:
        return 0, []
    
    # Tentukan panjang yang akan dicoba
    if allowed_lengths:
        lengths_to_try = [l for l in allowed_lengths if l <= n]
    else:
        lengths_to_try = range(1, n + 1)
    
    max_val = float('-inf')
    best_cuts = []
    
    def get_all_combinations(remaining, current_cuts):
        nonlocal max_val, best_cuts
        
        if remaining == 0:
            current_value = sum(prices[i-1] for i in current_cuts)
            if current_value > max_val:
                max_val = current_value
                best_cuts = current_cuts[:]
            return
        
        for length in lengths_to_try:
            if length <= remaining:
                get_all_combinations(remaining - length, current_cuts + [length])
    
    get_all_combinations(n, [])
    return max_val if max_val != float('-inf') else 0, best_cuts