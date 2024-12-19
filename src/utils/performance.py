import time
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
    """
    Decorator untuk mengukur waktu eksekusi dan penggunaan memori
    """
    def wrapper(*args, **kwargs):
        # Ukur memori sebelum
        memory_before = get_memory_usage()
        
        # Ukur waktu
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Ukur memori setelah
        memory_after = get_memory_usage()
        
        # Hitung penggunaan memori berdasarkan struktur data
        def calculate_memory(obj):
            if isinstance(obj, (list, tuple)):
                return sys.getsizeof(obj) + sum(calculate_memory(item) for item in obj)
            elif isinstance(obj, dict):
                return sys.getsizeof(obj) + sum(calculate_memory(k) + calculate_memory(v) for k, v in obj.items())
            elif isinstance(obj, (int, float)):
                return sys.getsizeof(obj)
            return sys.getsizeof(obj)
        
        # Hitung memori yang digunakan selama eksekusi
        memory_used = memory_after - memory_before
        
        # Jika memory_used terlalu kecil atau negatif, gunakan ukuran struktur data
        if memory_used <= 0:
            result_memory = calculate_memory(result)
            args_memory = sum(calculate_memory(arg) for arg in args)
            memory_used = result_memory + args_memory
        
        return result, execution_time, memory_used
    
    return wrapper