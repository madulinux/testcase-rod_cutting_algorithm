from src.utils.performance import measure_performance

@measure_performance
def rod_cutting_pure_recursive(prices, n):
    """
    Solusi rekursif murni untuk Rod Cutting Problem tanpa optimasi
    """
    if n <= 0:
        return 0
    
    max_val = float('-inf')
    for i in range(1, n + 1):
        max_val = max(max_val, prices[i-1] + rod_cutting_pure_recursive(prices, n - i)[0])
    return max_val

@measure_performance
def rod_cutting_recursive(prices, n, memo=None):
    """
    Solusi rekursif untuk Rod Cutting Problem dengan memoization
    """
    if memo is None:
        memo = {}
    
    if n <= 0:
        return 0
    
    if n in memo:
        return memo[n]
    
    max_val = float('-inf')
    for i in range(1, n + 1):
        max_val = max(max_val, prices[i-1] + rod_cutting_recursive(prices, n - i, memo)[0])
    
    memo[n] = max_val
    return max_val