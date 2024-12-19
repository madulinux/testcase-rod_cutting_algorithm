from src.utils.performance import measure_performance

@measure_performance
def rod_cutting_pure_recursive(prices, n, allowed_lengths=None):
    """
    Implementasi rod cutting dengan pendekatan rekursif murni (brute force)
    dengan opsi pembatasan panjang potong yang diperbolehkan
    """
    def _recursive(length):
        if length <= 0:
            return 0, []
        
        max_val = float('-inf')
        best_cuts = []
        
        # Tentukan panjang yang akan dicoba
        if allowed_lengths:
            lengths_to_try = [l for l in allowed_lengths if l <= length]
        else:
            lengths_to_try = range(1, length + 1)
        
        for i in lengths_to_try:
            val, cuts = _recursive(length - i)
            current_value = prices[i-1] + val
            if current_value > max_val:
                max_val = current_value
                best_cuts = [i] + cuts
        
        return (max_val if max_val != float('-inf') else 0), best_cuts
    
    return _recursive(n)

@measure_performance
def rod_cutting_recursive(prices, n, allowed_lengths=None, memo=None):
    """
    Implementasi rod cutting dengan pendekatan rekursif dan memoization
    dengan opsi pembatasan panjang potong yang diperbolehkan
    """
    def _recursive(length, memo):
        if length <= 0:
            return 0, []
        
        if length in memo:
            return memo[length]
        
        max_val = float('-inf')
        best_cuts = []
        
        # Tentukan panjang yang akan dicoba
        if allowed_lengths:
            lengths_to_try = [l for l in allowed_lengths if l <= length]
        else:
            lengths_to_try = range(1, length + 1)
        
        for i in lengths_to_try:
            val, cuts = _recursive(length - i, memo)
            current_value = prices[i-1] + val
            if current_value > max_val:
                max_val = current_value
                best_cuts = [i] + cuts
        
        result = ((max_val if max_val != float('-inf') else 0), best_cuts)
        memo[length] = result
        return result
    
    if memo is None:
        memo = {}
    return _recursive(n, memo)