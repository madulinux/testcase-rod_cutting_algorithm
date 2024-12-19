import time
import tracemalloc
import sys
import psutil
import os

def get_memory_usage():
    """
    Mengukur penggunaan memori saat ini menggunakan psutil
    """
    process = psutil.Process(os.getpid())
    return process.memory_info().rss  # Resident Set Size

def format_bytes(size):
    """
    Format ukuran bytes ke format yang mudah dibaca
    """
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def measure_performance(func):
    """Decorator untuk mengukur kinerja fungsi"""
    def wrapper(*args, **kwargs):
        # Start memory tracking
        tracemalloc.start()
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Get peak memory
        peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        
        # If result is a tuple, return tuple with peak memory
        if isinstance(result, tuple):
            return (*result, peak)
        # If result is not a tuple, return tuple of result and peak memory
        return result, peak
    
    return wrapper