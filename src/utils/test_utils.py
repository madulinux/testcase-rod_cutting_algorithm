import random
import os
from datetime import datetime
from src.utils.performance import format_bytes
import math

def generate_test_case(size, base_price=10):
    """
    Menghasilkan test case untuk rod cutting problem dengan pola harga yang lebih variatif.
    
    Strategi harga:
    1. Sweet spots: Beberapa panjang tertentu memiliki harga yang sangat menguntungkan
    2. Potongan pendek (1-3): Premium bervariasi (40-90%)
    3. Potongan menengah (4-7): Kombinasi premium dan diskon
    4. Potongan panjang (8+): Pola diskon yang bervariasi
    
    Args:
        size: Panjang maksimum rod
        base_price: Harga dasar per unit panjang
    Returns:
        list: Daftar harga untuk setiap panjang
    """
    prices = []
    # Tentukan sweet spots (panjang yang akan memiliki harga sangat menguntungkan)
    sweet_spots = {
        3: 1.9,  # 90% premium
        5: 1.6,  # 60% premium
        7: 1.4   # 40% premium
    }
    
    for i in range(size):
        length = i + 1
        price = base_price * length
        
        # Sweet spots calculation
        if length in sweet_spots:
            price *= sweet_spots[length]
            # Tambah sedikit variasi
            variation = random.uniform(-0.05, 0.05)
            price *= (1 + variation)
            
        # Regular price calculation
        elif length <= 3:
            # Premium bervariasi untuk potongan pendek
            premium = random.uniform(1.4, 1.7)  # 40-70% premium
            price *= premium
            
        elif length <= 7:
            if length % 2 == 0:  # Panjang genap
                # Premium medium
                premium = random.uniform(1.2, 1.3)
                price *= premium
            else:  # Panjang ganjil
                # Sedikit diskon
                discount = random.uniform(0.9, 0.95)
                price *= discount
                
        else:
            # Pola diskon yang lebih bervariasi untuk potongan panjang
            if length % 3 == 0:  # Setiap kelipatan 3
                discount = 0.85 - (0.02 * (length // 3))  # Diskon progresif
                price *= max(0.6, discount)
            elif length % 2 == 0:  # Panjang genap
                discount = 0.9 - (0.01 * (length - 8))
                price *= max(0.7, discount)
            else:  # Panjang ganjil lainnya
                discount = 0.95 - (0.015 * ((length - 8) // 2))
                price *= max(0.75, discount)
        
        # Tambahkan variasi kecil
        variation = random.uniform(-0.03, 0.03)
        price *= (1 + variation)
        
        # Pembulatan dan pastikan harga minimal
        price = max(int(price), base_price * length // 2)
        
        # Pastikan harga meningkat dengan pola yang masuk akal
        if prices:
            min_increase = base_price // 3
            # Biarkan sweet spots memiliki lompatan harga yang lebih tinggi
            if length in sweet_spots:
                price = max(price, prices[-1] + base_price)
            else:
                price = max(price, prices[-1] + min_increase)
        
        prices.append(price)
    
    return prices

def get_optimal_cuts(prices, n, max_value, allowed_lengths=None):
    """
    Mendapatkan kombinasi potongan optimal untuk hasil tertentu,
    mempertimbangkan kombinasi yang lebih variatif ketika nilai totalnya sama
    
    Args:
        prices: List harga untuk setiap panjang
        n: Panjang total rod
        max_value: Nilai optimal yang dicari
        allowed_lengths: Optional list of allowed cutting lengths
    Returns:
        list: Daftar panjang potongan optimal
    """
    def find_all_cuts(length, target_value, memo=None):
        """
        Mencari semua kombinasi potongan yang menghasilkan nilai target
        """
        if memo is None:
            memo = {}
        
        if length == 0 and target_value == 0:
            return [[]]
        if length <= 0 or target_value <= 0:
            return []
            
        if (length, target_value) in memo:
            return memo[(length, target_value)]
            
        all_combinations = []
        
        for i in range(1, length + 1):
            if allowed_lengths and i not in allowed_lengths:
                continue
            if i <= len(prices) and prices[i-1] <= target_value:
                remaining_cuts = find_all_cuts(length - i, target_value - prices[i-1], memo)
                for cuts in remaining_cuts:
                    all_combinations.append([i] + cuts)
                        
        memo[(length, target_value)] = all_combinations
        return all_combinations
    
    # Dapatkan semua kombinasi yang menghasilkan nilai maksimal
    all_possible_cuts = find_all_cuts(n, max_value)
    
    if not all_possible_cuts:
        return [n]  # Fallback ke potongan tunggal jika tidak ada solusi lain
    
    # Pilih kombinasi terbaik berdasarkan beberapa kriteria
    best_cuts = None
    best_score = -1
    
    for cuts in all_possible_cuts:
        # Hitung skor untuk kombinasi ini
        diversity_score = len(set(cuts)) / len(cuts)  # Keberagaman potongan
        sweet_spot_score = sum(1 for x in cuts if x in [3, 5, 7]) / len(cuts)  # Penggunaan sweet spots
        efficiency_score = sum(prices[x-1]/x for x in cuts) / len(cuts)  # Efisiensi harga per unit
        
        # Kombinasikan skor-skor dengan bobot
        total_score = (
            diversity_score * 0.4 +      # Prioritaskan keberagaman
            sweet_spot_score * 0.3 +     # Manfaatkan sweet spots
            efficiency_score * 0.3        # Pertimbangkan efisiensi
        )
        
        # Update kombinasi terbaik
        if total_score > best_score:
            best_score = total_score
            best_cuts = cuts
    
    return sorted(best_cuts) if best_cuts else [n]

def measure_memory_usage(func, *args):
    """
    Mengukur penggunaan memori maksimum selama eksekusi fungsi
    """
    import tracemalloc
    import gc
    
    # Force garbage collection untuk memastikan pengukuran yang akurat
    gc.collect()
    
    # Mulai pelacakan memori
    tracemalloc.start()
    
    # Jalankan fungsi
    result = func(*args)
    
    # Dapatkan statistik penggunaan memori
    current, peak = tracemalloc.get_traced_memory()
    
    # Hentikan pelacakan
    tracemalloc.stop()
    
    return result, peak

def test_performance(test_sizes, user_prices=None, allowed_lengths=None):
    """
    Menguji dan membandingkan kinerja semua implementasi dengan analisis yang lebih detail
    
    Args:
        test_sizes: List ukuran rod yang akan diuji
        user_prices: Optional dictionary mapping panjang ke harga (untuk input manual)
        allowed_lengths: Optional list of allowed cutting lengths
    Returns:
        dict: Dictionary berisi hasil pengujian
    """
    from src.implementations.recursive import rod_cutting_pure_recursive, rod_cutting_recursive
    from src.implementations.iterative import rod_cutting_iterative
    from src.implementations.dynamic_programming import rod_cutting_dp, rod_cutting_dp_space_optimized
    import time
    
    metrics = {
        'execution_time': {},
        'memory_usage': {},
        'peak_memory': {},
        'solution_quality': {},
        'prices': {},
        'cut_patterns': {},
        'price_analysis': {},
        'efficiency_metrics': {},
        'allowed_lengths': allowed_lengths
    }
    
    implementations = {
        'Pure Recursive (Brute Force)': rod_cutting_pure_recursive,
        'Iterative (Brute Force)': rod_cutting_iterative,
        'Recursive with Memoization (Top-down DP)': rod_cutting_recursive,
        'Bottom-up DP': rod_cutting_dp,
        'Space Optimized DP': rod_cutting_dp_space_optimized
    }
    
    for size in test_sizes:
        if user_prices is None:
            if allowed_lengths:
                # Generate prices hanya untuk panjang yang diperbolehkan
                prices = [0] * size  # Initialize dengan 0
                for length in allowed_lengths:
                    if length <= size:
                        prices[length-1] = generate_test_case(length)[length-1]
            else:
                prices = generate_test_case(size)
        else:
            # Gunakan harga dari user, hanya untuk panjang yang diperbolehkan
            prices = [0] * size  # Initialize dengan 0
            if allowed_lengths:
                for length in allowed_lengths:
                    if length <= size and length in user_prices:
                        prices[length-1] = user_prices[length]
            else:
                for i in range(1, size + 1):
                    if i in user_prices:
                        prices[i-1] = user_prices[i]
        
        metrics['prices'][size] = prices
        metrics['price_analysis'][size] = analyze_prices(prices)
        
        for name, impl in implementations.items():
            try:
                # Ukur waktu eksekusi
                start_time = time.time()
                if allowed_lengths:
                    result = impl(prices, size, allowed_lengths)
                else:
                    result = impl(prices, size)
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                # Unpack hasil
                if len(result) == 3:  # value, cuts, peak_memory
                    value, cuts, peak_memory = result
                else:  # value, peak_memory
                    value, peak_memory = result
                    cuts = get_optimal_cuts(prices, size, value, allowed_lengths)
                
                # Simpan metrik
                if size not in metrics['execution_time']:
                    metrics['execution_time'][size] = {}
                metrics['execution_time'][size][name] = execution_time
                
                if size not in metrics['peak_memory']:
                    metrics['peak_memory'][size] = {}
                metrics['peak_memory'][size][name] = peak_memory
                
                if size not in metrics['solution_quality']:
                    metrics['solution_quality'][size] = {}
                metrics['solution_quality'][size][name] = value
                
                if size not in metrics['cut_patterns']:
                    metrics['cut_patterns'][size] = {}
                metrics['cut_patterns'][size][name] = cuts
                
                if size not in metrics['efficiency_metrics']:
                    metrics['efficiency_metrics'][size] = {}
                efficiency_metrics = calculate_efficiency_metrics(
                    value, cuts, prices, execution_time, peak_memory
                )
                metrics['efficiency_metrics'][size][name] = efficiency_metrics
                
                print(f"\n{name} (Size {size}):")
                print(f"Hasil: {value}")
                print(f"Pola Potong: {cuts}")
                print(f"Waktu: {execution_time:.6f} detik")
                print(f"Peak Memory: {format_bytes(peak_memory)}")
                
            except Exception as e:
                print(f"Error in {name}: {str(e)}")
                # Inisialisasi metrik kosong untuk implementasi yang gagal
                if size not in metrics['execution_time']:
                    metrics['execution_time'][size] = {}
                if size not in metrics['peak_memory']:
                    metrics['peak_memory'][size] = {}
                if size not in metrics['solution_quality']:
                    metrics['solution_quality'][size] = {}
                if size not in metrics['cut_patterns']:
                    metrics['cut_patterns'][size] = {}
                if size not in metrics['efficiency_metrics']:
                    metrics['efficiency_metrics'][size] = {}
                    
                metrics['execution_time'][size][name] = 0
                metrics['peak_memory'][size][name] = 0
                metrics['solution_quality'][size][name] = 0
                metrics['cut_patterns'][size][name] = []
                metrics['efficiency_metrics'][size][name] = {
                    'efficiency_ratio': 0,
                    'memory_efficiency': 0,
                    'time_efficiency': 0
                }
                continue
    
    return metrics

def analyze_prices(prices):
    """
    Menganalisis karakteristik harga untuk setiap panjang
    """
    analysis = {}
    avg_price_per_unit = sum(price/(i+1) for i, price in enumerate(prices)) / len(prices)
    
    for i, price in enumerate(prices):
        length = i + 1
        price_per_unit = price / length
        
        # Menentukan karakteristik harga
        is_premium = price_per_unit > 1.1 * avg_price_per_unit
        is_regular = 0.9 * avg_price_per_unit <= price_per_unit <= 1.1 * avg_price_per_unit
        is_sweet_spot = False
        
        # Cek apakah ini sweet spot
        if length in [3, 5, 7]:
            expected_price = length * (prices[0] / 1)  # Bandingkan dengan harga per unit pertama
            if price > expected_price * 1.3:  # 30% lebih tinggi dari yang diharapkan
                is_sweet_spot = True
        
        analysis[length] = {
            'price_per_unit': price_per_unit,
            'is_premium': is_premium,
            'is_regular': is_regular,
            'is_sweet_spot': is_sweet_spot,
            'relative_to_avg': price_per_unit / avg_price_per_unit
        }
    
    return analysis

def calculate_efficiency_metrics(value, cuts, prices, time, memory):
    """
    Menghitung berbagai metrik efisiensi untuk solusi
    """
    total_length = sum(cuts)
    value_per_unit = value / total_length
    time_efficiency = value / (time + 1e-10)  # Menghindari pembagian dengan nol
    memory_efficiency = value / (memory + 1e-10)
    
    return {
        'value_per_unit': value_per_unit,
        'time_efficiency': time_efficiency,
        'memory_efficiency': memory_efficiency,
        'cut_diversity': len(set(cuts)) / len(cuts) if cuts else 0
    }

def format_cut_pattern(cuts):
    """
    Format pola pemotongan dengan cara yang lebih informatif
    """
    if not cuts:
        return "[]"
    
    # Hitung frekuensi setiap panjang
    from collections import Counter
    freq = Counter(cuts)
    
    # Format output
    pattern = []
    for length, count in sorted(freq.items()):
        if count > 1:
            pattern.append(f"{length}x{count}")
        else:
            pattern.append(str(length))
    
    return "[" + ", ".join(pattern) + "]"

def visualize_results(metrics, test_sizes, result_dir):
    """
    Membuat visualisasi hasil analisis menggunakan matplotlib
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Set default style yang lebih modern
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    
    def create_performance_plot():
        """Membuat plot perbandingan waktu eksekusi"""
        plt.figure(figsize=(12, 6))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        for i, (impl, color) in enumerate(zip(metrics['execution_time'][test_sizes[0]].keys(), colors)):
            times = [metrics['execution_time'][size][impl] for size in test_sizes]
            plt.plot(test_sizes, times, marker='o', label=impl, color=color, linewidth=2)
        
        plt.yscale('log')
        plt.xlabel('Ukuran Rod', fontsize=12)
        plt.ylabel('Waktu Eksekusi (detik)', fontsize=12)
        plt.title('Perbandingan Waktu Eksekusi Antar Implementasi', fontsize=14, pad=20)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f'{result_dir}/execution_time_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_memory_comparison_plot():
        """Membuat plot perbandingan penggunaan memori"""
        plt.figure(figsize=(12, 6))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        bar_width = 0.15
        index = np.arange(len(test_sizes))
        
        for i, (impl, color) in enumerate(zip(metrics['peak_memory'][test_sizes[0]].keys(), colors)):
            memory_usage = [metrics['peak_memory'][size][impl] / (1024 * 1024) for size in test_sizes]  # Convert to MB
            plt.bar(index + i * bar_width, memory_usage, bar_width, 
                   label=impl, color=color, alpha=0.8)
        
        plt.xlabel('Ukuran Rod', fontsize=12)
        plt.ylabel('Penggunaan Memori (MB)', fontsize=12)
        plt.title('Perbandingan Penggunaan Memori Antar Implementasi', fontsize=14, pad=20)
        plt.xticks(index + bar_width * 2, test_sizes)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f'{result_dir}/memory_usage_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_memory_growth_plot():
        """Membuat plot pertumbuhan penggunaan memori"""
        plt.figure(figsize=(12, 6))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        for i, (impl, color) in enumerate(zip(metrics['peak_memory'][test_sizes[0]].keys(), colors)):
            memory_usage = [metrics['peak_memory'][size][impl] / (1024 * 1024) for size in test_sizes]  # Convert to MB
            plt.plot(test_sizes, memory_usage, marker='o', label=impl, color=color, linewidth=2)
        
        plt.xlabel('Ukuran Rod', fontsize=12)
        plt.ylabel('Penggunaan Memori (MB)', fontsize=12)
        plt.title('Pertumbuhan Penggunaan Memori', fontsize=14, pad=20)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f'{result_dir}/memory_growth.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_price_analysis_plot(size):
        """Membuat plot analisis harga untuk ukuran tertentu"""
        plt.figure(figsize=(12, 6))
        
        lengths = list(range(1, size + 1))
        prices = metrics['prices'][size]
        price_per_unit = [prices[i-1]/i for i in lengths]
        
        plt.plot(lengths, prices, marker='o', label='Harga Total', color='#1f77b4', linewidth=2)
        plt.plot(lengths, [p*l for l, p in zip(lengths, price_per_unit)], 
                marker='s', label='Harga Proporsional', color='#2ca02c', linewidth=2)
        
        # Highlight sweet spots
        sweet_spots = [3, 5, 7]
        sweet_spot_prices = [prices[i-1] for i in sweet_spots if i <= size]
        sweet_spot_lengths = [i for i in sweet_spots if i <= size]
        if sweet_spot_prices:
            plt.scatter(sweet_spot_lengths, sweet_spot_prices, 
                       color='#d62728', s=150, label='Sweet Spots', zorder=5)
        
        plt.xlabel('Panjang Potongan', fontsize=12)
        plt.ylabel('Harga', fontsize=12)
        plt.title(f'Analisis Harga untuk Rod Ukuran {size}', fontsize=14, pad=20)
        plt.legend(fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(f'{result_dir}/price_analysis_size_{size}.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_cut_pattern_plot():
        """Membuat plot analisis pola pemotongan"""
        plt.figure(figsize=(12, 6))
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(test_sizes)))
        for size, color in zip(test_sizes, colors):
            # Ambil pola pemotongan dari implementasi DP (yang paling efisien)
            cuts = metrics['cut_patterns'][size]['Bottom-up DP']
            unique_cuts = len(set(cuts))
            avg_cut_length = sum(cuts) / len(cuts)
            
            plt.scatter(size, unique_cuts, label=f'Size {size}', color=color, s=100)
            plt.annotate(f'Avg Length: {avg_cut_length:.1f}',
                        (size, unique_cuts),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=10)
        
        plt.xlabel('Ukuran Rod', fontsize=12)
        plt.ylabel('Jumlah Potongan Unik', fontsize=12)
        plt.title('Analisis Pola Pemotongan', fontsize=14, pad=20)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(f'{result_dir}/cut_pattern_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

    # Buat semua visualisasi
    create_performance_plot()
    create_memory_comparison_plot()
    create_memory_growth_plot()
    for size in test_sizes:
        create_price_analysis_plot(size)
    create_cut_pattern_plot()

def save_analysis_to_file(metrics, test_sizes):
    """Menyimpan hasil analisis ke file markdown dengan detail lengkap"""
    # Buat direktori untuk hasil
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    result_dir = f"results/analysis_{timestamp}"
    os.makedirs(result_dir, exist_ok=True)
    analysis_file = f"{result_dir}/analysis.md"
    
    # Buat visualisasi
    visualize_results(metrics, test_sizes, result_dir)
    
    with open(analysis_file, 'w') as f:
        f.write("# Analisis Rod Cutting Problem\n\n")
        f.write(f"### Tanggal Pengujian: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        # Kategorisasi dan Penjelasan Implementasi
        f.write("## Kategorisasi Implementasi\n\n")
        f.write("### 1. Implementasi Tanpa Dynamic Programming (Brute Force)\n\n")
        f.write("#### Pure Recursive\n")
        f.write("- Menggunakan rekursi murni tanpa optimasi\n")
        f.write("- Menghitung ulang subproblem yang sama berkali-kali\n")
        f.write("- Kompleksitas Waktu: O(2^n)\n")
        f.write("- Kompleksitas Ruang: O(n) untuk call stack\n\n")
        
        f.write("#### Iterative (Brute Force)\n")
        f.write("- Mencoba semua kombinasi pemotongan yang mungkin\n")
        f.write("- Tidak menggunakan memoization atau tabulasi\n")
        f.write("- Kompleksitas Waktu: O(n * 2^n)\n")
        f.write("- Kompleksitas Ruang: O(2^n) untuk menyimpan kombinasi\n\n")
        
        f.write("### 2. Implementasi dengan Dynamic Programming\n\n")
        f.write("#### Recursive dengan Memoization (Top-down DP)\n")
        f.write("- Menggunakan DP dengan pendekatan top-down\n")
        f.write("- Menyimpan hasil perhitungan dalam dictionary\n")
        f.write("- Kompleksitas Waktu: O(n²)\n")
        f.write("- Trade-off antara waktu dan memori\n\n")
        
        f.write("#### Bottom-up DP\n")
        f.write("- Menggunakan DP dengan pendekatan bottom-up\n")
        f.write("- Membangun solusi dari subproblem terkecil\n")
        f.write("- Kompleksitas Waktu: O(n²)\n")
        f.write("- Lebih efisien dalam penggunaan memori dibanding top-down\n\n")
        
        f.write("### 3. Implementasi dengan Optimasi\n\n")
        f.write("#### Space Optimized DP\n")
        f.write("- Berbasis Bottom-up DP\n")
        f.write("- Mengoptimalkan penggunaan memori\n")
        f.write("- Kompleksitas Waktu: O(n²)\n")
        f.write("- Overhead memori minimal\n\n")
        
        # Informasi tentang batasan panjang potong
        if metrics.get('allowed_lengths'):
            f.write("## Batasan Panjang Potong\n")
            f.write(f"Panjang yang diperbolehkan: {sorted(metrics['allowed_lengths'])}\n\n")
        
        # Hasil Pengujian Detail
        f.write("## Hasil Pengujian Detail\n\n")
        for size in test_sizes:
            f.write(f"### Ukuran Input: {size}\n\n")
            
            # Tampilkan daftar harga
            prices = [str(metrics['prices'][size][i]) for i in range(size)]
            f.write(f"**Daftar Harga:**\n")
            f.write(f"```\n[{', '.join(prices)}]\n```\n\n")
            
            # Analisis harga per unit
            price_per_unit = [(i+1, float(metrics['prices'][size][i])/(i+1)) for i in range(size)]
            max_price_per_unit = max(price_per_unit, key=lambda x: x[1])
            
            f.write("**Analisis Harga per Unit:**\n")
            f.write("```\n")
            for length, ppu in price_per_unit:
                if (length, ppu) == max_price_per_unit:
                    f.write(f"  Panjang {length}: {ppu:.2f} per unit ⭐ (optimal per unit)\n")
                else:
                    f.write(f"  Panjang {length}: {ppu:.2f} per unit\n")
            f.write("```\n\n")
        
        # Perbandingan Kinerja
        f.write("## Perbandingan Kinerja\n")
        f.write("### Waktu Eksekusi\n")
        f.write("| Size | " + " | ".join(metrics['execution_time'][test_sizes[0]].keys()) + " |\n")
        f.write("|" + "---|" * (len(metrics['execution_time'][test_sizes[0]]) + 1) + "\n")
        
        for size in test_sizes:
            row = [str(size)]
            for impl in metrics['execution_time'][test_sizes[0]].keys():
                time_val = metrics['execution_time'][size][impl]
                row.append(f"{time_val:.6f}s")
            f.write("| " + " | ".join(row) + " |\n")
        f.write("\n")
        
        # Analisis Peningkatan Waktu
        f.write("### Analisis Peningkatan Waktu\n")
        for size1, size2 in zip(test_sizes[:-1], test_sizes[1:]):
            f.write(f"\n#### Peningkatan dari ukuran {size1} ke {size2}:\n")
            for impl in metrics['execution_time'][size1].keys():
                time1 = metrics['execution_time'][size1][impl]
                time2 = metrics['execution_time'][size2][impl]
                increase = (time2 - time1) / time1 * 100
                f.write(f"- {impl}: {increase:.2f}% \n")
        
        # Penggunaan Memori
        f.write("\n### Penggunaan Memori\n")
        f.write("| Size | " + " | ".join(metrics['peak_memory'][test_sizes[0]].keys()) + " |\n")
        f.write("|" + "---|" * (len(metrics['peak_memory'][test_sizes[0]]) + 1) + "\n")
        
        for size in test_sizes:
            row = [str(size)]
            for impl in metrics['peak_memory'][test_sizes[0]].keys():
                memory_val = metrics['peak_memory'][size][impl]
                row.append(format_bytes(memory_val))
            f.write("| " + " | ".join(row) + " |\n")
        f.write("\n")
        
        # Analisis Hasil dan Efisiensi
        f.write("## Analisis Hasil\n")
        f.write("### Nilai Optimal dan Pola Pemotongan\n")
        f.write("| Size | " + " | ".join(metrics['solution_quality'][test_sizes[0]].keys()) + " |\n")
        f.write("|" + "---|" * (len(metrics['solution_quality'][test_sizes[0]]) + 1) + "\n")
        
        for size in test_sizes:
            row = [str(size)]
            for impl in metrics['solution_quality'][test_sizes[0]].keys():
                value = metrics['solution_quality'][size][impl]
                cuts = metrics['cut_patterns'][size][impl]
                row.append(f"{value} ({cuts})")
            f.write("| " + " | ".join(row) + " |\n")
        f.write("\n")
        
        # Detail Analisis Efisiensi
        f.write("### Analisis Efisiensi Detail\n")
        for size in test_sizes:
            f.write(f"\n#### Size {size}\n")
            prices = metrics['prices'][size]
            
            # Hitung harga per unit jika tidak memotong
            no_cut_price = prices[size-1] if size-1 < len(prices) and prices[size-1] > 0 else 1
            
            for impl in metrics['solution_quality'][test_sizes[0]].keys():
                value = metrics['solution_quality'][size][impl]
                cuts = metrics['cut_patterns'][size][impl]
                
                if not cuts:  # Skip jika tidak ada pola potong
                    continue
                    
                total_length = sum(cuts)
                if total_length == 0:  # Hindari pembagian dengan nol
                    continue
                    
                price_per_unit = value / total_length if total_length > 0 else 0
                
                # Hindari pembagian dengan nol
                if no_cut_price > 0:
                    relative_saving = ((price_per_unit/(no_cut_price/size)) - 1) * 100
                else:
                    relative_saving = 0
                
                f.write(f"\n**{impl}**\n")
                f.write(f"- Nilai Total: {value}\n")
                f.write(f"- Pola Potong: {cuts}\n")
                f.write(f"- Harga per Unit: {price_per_unit:.2f}\n")
                f.write(f"- Efisiensi vs No Cut: {relative_saving:.1f}%\n")
                
                # Detail perhitungan
                f.write("- Detail perhitungan:\n")
                f.write("```\n")
                cut_frequency = {}
                for cut in cuts:
                    cut_frequency[cut] = cut_frequency.get(cut, 0) + 1
                
                total = 0
                for cut, freq in sorted(cut_frequency.items()):
                    price = prices[cut-1]
                    total += price * freq
                    cut_price_per_unit = price / cut
                    f.write(f"  Panjang {cut} (x{freq}): {price} (per unit: {cut_price_per_unit:.2f})\n")
                f.write(f"  Total: {total}\n")
                f.write("```\n")
        
        # Analisis Trade-off
        f.write("\n## Analisis Trade-off\n\n")
        
        f.write("### 1. Trade-off Waktu vs Memori\n")
        # Hitung rata-rata waktu dan memori untuk setiap implementasi
        avg_metrics = {}
        for impl in metrics['execution_time'][test_sizes[0]].keys():
            times = [metrics['execution_time'][size][impl] for size in test_sizes]
            memories = [metrics['peak_memory'][size][impl] for size in test_sizes]
            avg_metrics[impl] = {
                'avg_time': sum(times) / len(times),
                'avg_memory': sum(memories) / len(memories),
                'max_time': max(times),
                'max_memory': max(memories)
            }
        
        for impl, stats in avg_metrics.items():
            f.write(f"\n#### {impl}\n")
            f.write(f"- Rata-rata Waktu: {stats['avg_time']:.6f}s\n")
            f.write(f"- Rata-rata Memori: {format_bytes(stats['avg_memory'])}\n")
            f.write(f"- Waktu Maksimum: {stats['max_time']:.6f}s\n")
            f.write(f"- Memori Maksimum: {format_bytes(stats['max_memory'])}\n")
        
        f.write("\n### 2. Karakteristik Implementasi\n\n")
        f.write("#### Pure Recursive (Brute Force)\n")
        f.write("- **Kelebihan:**\n")
        f.write("  - Implementasi sederhana dan mudah dipahami\n")
        f.write("  - Cocok untuk debugging karena alur eksekusi jelas\n")
        f.write("- **Kekurangan:**\n")
        f.write("  - Waktu eksekusi meningkat eksponensial\n")
        f.write("  - Banyak perhitungan redundan\n")
        f.write("- **Best Case:** Input kecil (n ≤ 10) untuk pembelajaran\n\n")
        
        f.write("#### Iterative (Brute Force)\n")
        f.write("- **Kelebihan:**\n")
        f.write("  - Menghindari overhead rekursi\n")
        f.write("  - Lebih efisien dalam penggunaan call stack\n")
        f.write("- **Kekurangan:**\n")
        f.write("  - Tetap memerlukan waktu eksponensial\n")
        f.write("  - Penggunaan memori untuk menyimpan kombinasi\n")
        f.write("- **Best Case:** Input kecil dengan batasan memori longgar\n\n")
        
        f.write("#### Recursive with Memoization (Top-down DP)\n")
        f.write("- **Kelebihan:**\n")
        f.write("  - Hanya menghitung subproblem yang diperlukan\n")
        f.write("  - Mudah diimplementasi dari versi rekursif\n")
        f.write("- **Kekurangan:**\n")
        f.write("  - Overhead dari rekursi masih ada\n")
        f.write("  - Penggunaan memori untuk memoization\n")
        f.write("- **Best Case:** Input menengah dengan subproblem berulang\n\n")
        
        f.write("#### Bottom-up DP\n")
        f.write("- **Kelebihan:**\n")
        f.write("  - Menghindari overhead rekursi\n")
        f.write("  - Lebih efisien dalam penggunaan memori\n")
        f.write("- **Kekurangan:**\n")
        f.write("  - Menghitung semua subproblem\n")
        f.write("  - Memerlukan array tambahan untuk tracking\n")
        f.write("- **Best Case:** Input besar dengan memori mencukupi\n\n")
        
        f.write("#### Space Optimized DP\n")
        f.write("- **Kelebihan:**\n")
        f.write("  - Penggunaan memori paling efisien\n")
        f.write("  - Kinerja waktu tetap kompetitif\n")
        f.write("- **Kekurangan:**\n")
        f.write("  - Implementasi lebih kompleks\n")
        f.write("  - Tracking solusi lebih sulit\n")
        f.write("- **Best Case:** Input besar dengan batasan memori ketat\n\n")
        
        f.write("### 3. Perbedaan Urutan Pemotongan\n\n")
        f.write("Beberapa implementasi menghasilkan urutan pemotongan yang berbeda (misalnya [2, 3] vs [3, 2]) karena:\n\n")
        f.write("1. **Arah Pencarian:**\n")
        f.write("   - Top-down: Memecah masalah dari atas ke bawah\n")
        f.write("   - Bottom-up: Membangun solusi dari bawah ke atas\n\n")
        f.write("2. **Prioritas Pemilihan:**\n")
        f.write("   - Beberapa implementasi mengutamakan potongan kecil dulu\n")
        f.write("   - Yang lain mengutamakan potongan besar dulu\n\n")
        f.write("3. **Urutan Iterasi:**\n")
        f.write("   - Iterative: Mencoba kombinasi secara sekuensial\n")
        f.write("   - DP: Mengoptimalkan berdasarkan subproblem\n\n")
        f.write("Semua urutan valid selama menghasilkan nilai optimal yang sama.\n\n")
        
        f.write("### 4. Rekomendasi Penggunaan Berdasarkan Karakteristik Input\n\n")
        f.write("#### Berdasarkan Ukuran Input\n")
        f.write("- **Kecil (n ≤ 10):**\n")
        f.write("  - Gunakan Pure Recursive untuk pembelajaran\n")
        f.write("  - Atau Iterative untuk performa lebih baik\n\n")
        f.write("- **Menengah (10 < n ≤ 20):**\n")
        f.write("  - Gunakan Top-down DP jika subproblem sedikit\n")
        f.write("  - Atau Bottom-up DP untuk konsistensi\n\n")
        f.write("- **Besar (n > 20):**\n")
        f.write("  - Gunakan Bottom-up DP untuk kinerja optimal\n")
        f.write("  - Atau Space Optimized DP jika memori terbatas\n\n")
        
        f.write("#### Berdasarkan Batasan Panjang Potong\n")
        f.write("- **Sedikit Pilihan:**\n")
        f.write("  - Top-down DP lebih efisien karena subproblem lebih sedikit\n\n")
        f.write("- **Banyak Pilihan:**\n")
        f.write("  - Bottom-up DP atau Space Optimized DP untuk konsistensi\n\n")
        
        f.write("#### Berdasarkan Kebutuhan Debugging\n")
        f.write("- **Fase Development:**\n")
        f.write("  - Gunakan Pure Recursive atau Top-down DP\n")
        f.write("  - Lebih mudah di-debug dan dipahami\n\n")
        f.write("- **Fase Production:**\n")
        f.write("  - Gunakan Bottom-up DP atau Space Optimized DP\n")
        f.write("  - Performa dan efisiensi lebih penting\n\n")
        
        # Visualisasi
        f.write("\n## Visualisasi\n")
        
        # Perbandingan Waktu Eksekusi
        f.write("### 1. Perbandingan Waktu Eksekusi\n")
        f.write("![Perbandingan Waktu Eksekusi](execution_time_comparison.png)\n\n")
        
        # Analisis waktu eksekusi berdasarkan data
        max_times = {impl: max(metrics['execution_time'][size][impl] for size in test_sizes) 
                    for impl in metrics['execution_time'][test_sizes[0]].keys()}
        min_times = {impl: min(metrics['execution_time'][size][impl] for size in test_sizes) 
                    for impl in metrics['execution_time'][test_sizes[0]].keys()}
        
        f.write(f"Berdasarkan data pengujian dengan ukuran input {test_sizes}:\n")
        f.write("- **Waktu Eksekusi Terbaik:**\n")
        for impl, min_time in sorted(min_times.items(), key=lambda x: x[1]):
            f.write(f"  - {impl}: {min_time:.6f}s\n")
        
        f.write("\n- **Waktu Eksekusi Terburuk:**\n")
        for impl, max_time in sorted(max_times.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  - {impl}: {max_time:.6f}s\n")
        
        # Analisis Pola Pemotongan
        f.write("\n### 2. Analisis Pola Pemotongan\n")
        f.write("![Analisis Pola Pemotongan](cut_pattern_analysis.png)\n\n")
        f.write("Hasil pola pemotongan untuk setiap ukuran input:\n")
        for size in test_sizes:
            f.write(f"\n**Ukuran {size}:**\n")
            for impl in metrics['cut_patterns'][size].keys():
                cuts = metrics['cut_patterns'][size][impl]
                if cuts:
                    f.write(f"- {impl}: {cuts} (Nilai: {metrics['solution_quality'][size][impl]})\n")
        
        # Visualisasi Penggunaan Memori
        f.write("\n### 3. Visualisasi Penggunaan Memori\n")
        f.write("#### a. Grafik Pertumbuhan Memori\n")
        f.write("![Memory Growth](memory_growth.png)\n\n")
        
        # Analisis memori berdasarkan data
        max_memory = {impl: max(metrics['peak_memory'][size][impl] for size in test_sizes) 
                     for impl in metrics['peak_memory'][test_sizes[0]].keys()}
        min_memory = {impl: min(metrics['peak_memory'][size][impl] for size in test_sizes) 
                     for impl in metrics['peak_memory'][test_sizes[0]].keys()}
        
        f.write("Pengukuran penggunaan memori:\n")
        f.write("- **Memori Minimum:**\n")
        for impl, min_mem in sorted(min_memory.items(), key=lambda x: x[1]):
            f.write(f"  - {impl}: {format_bytes(min_mem)}\n")
        
        f.write("\n- **Memori Maksimum:**\n")
        for impl, max_mem in sorted(max_memory.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  - {impl}: {format_bytes(max_mem)}\n")
        
        f.write("\n#### b. Perbandingan Penggunaan Memori\n")
        f.write("![Memory Usage Comparison](memory_usage_comparison.png)\n\n")
        
        # Perbandingan relatif memori
        base_impl = min(max_memory.items(), key=lambda x: x[1])[0]
        base_mem = max_memory[base_impl]
        f.write("Perbandingan relatif penggunaan memori:\n")
        for impl, max_mem in max_memory.items():
            if impl != base_impl:
                ratio = max_mem / base_mem
                f.write(f"- {impl} menggunakan {ratio:.2f}x lebih banyak memori dibanding {base_impl}\n")
        
        # Kesimpulan
        f.write("\n## Kesimpulan\n\n")
        
        # Hitung rata-rata waktu eksekusi
        avg_times = {}
        for impl in metrics['execution_time'][test_sizes[0]].keys():
            times = [metrics['execution_time'][size][impl] for size in test_sizes]
            avg_times[impl] = sum(times) / len(times)
        
        sorted_impls = sorted(avg_times.items(), key=lambda x: x[1])
        
        f.write("### Performa Implementasi\n")
        f.write(f"1. **Performa Terbaik:** {sorted_impls[0][0]}\n")
        f.write(f"2. **Performa Menengah:** {', '.join(impl[0] for impl in sorted_impls[1:-1])}\n")
        f.write(f"3. **Performa Terendah:** {sorted_impls[-1][0]}\n\n")
        
        f.write("### Rekomendasi Penggunaan\n")
        f.write("1. Untuk dataset kecil (n ≤ 10): Semua implementasi dapat digunakan\n")
        f.write("2. Untuk dataset menengah (10 < n ≤ 20): Gunakan implementasi DP\n")
        f.write("3. Untuk dataset besar (n > 20): Gunakan Bottom-up DP atau Space Optimized DP\n")
        f.write("4. Jika memori terbatas: Gunakan Space Optimized DP\n")
        f.write("5. Untuk tujuan pembelajaran/debugging: Gunakan Top-down DP\n\n")
    
    print(f"Analysis saved to {analysis_file}")
    return result_dir

def main():
    test_sizes = [10, 20, 30, 40, 50]
    metrics = test_performance(test_sizes)
    save_analysis_to_file(metrics, test_sizes)

if __name__ == "__main__":
    main()