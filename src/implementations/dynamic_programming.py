from src.utils.performance import measure_performance

@measure_performance
def rod_cutting_dp(prices, n):
    """
    Solusi Dynamic Programming untuk Rod Cutting Problem
    """
    dp = [0 for _ in range(n + 1)]
    for i in range(1, n + 1):
        max_val = float('-inf')
        for j in range(1, i + 1):
            max_val = max(max_val, prices[j-1] + dp[i-j])
        dp[i] = max_val
    return dp[n]

@measure_performance
def rod_cutting_dp_space_optimized(prices, n):
    """
    Solusi DP dengan optimasi ruang
    """
    dp = [0 for _ in range(n + 1)]
    for i in range(1, n + 1):
        max_val = float('-inf')
        for j in range(1, i + 1):
            max_val = max(max_val, prices[j-1] + dp[i-j])
        dp[i] = max_val
    return dp[n]

@measure_performance
def rod_cutting_dp_with_cuts(prices, n):
    """
    Solusi DP yang juga mengembalikan cara pemotongan
    """
    dp = [0 for _ in range(n + 1)]
    cuts = [0 for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        max_val = float('-inf')
        for j in range(1, i + 1):
            if prices[j-1] + dp[i-j] > max_val:
                max_val = prices[j-1] + dp[i-j]
                cuts[i] = j
        dp[i] = max_val
    
    result = []
    while n > 0:
        result.append(cuts[n])
        n = n - cuts[n]
    
    return dp[n], result