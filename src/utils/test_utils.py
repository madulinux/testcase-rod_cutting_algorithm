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

def get_optimal_cuts(prices, n, max_value):
    """
    Mendapatkan kombinasi potongan optimal untuk hasil tertentu,
    mempertimbangkan kombinasi yang lebih variatif ketika nilai totalnya sama
    
    Args:
        prices: List harga untuk setiap panjang
        n: Panjang total rod
        max_value: Nilai optimal yang dicari
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

def test_performance(test_sizes, user_prices=None):
    """
    Menguji dan membandingkan kinerja semua implementasi dengan analisis yang lebih detail
    
    Args:
        test_sizes: List ukuran rod yang akan diuji
        user_prices: Optional dictionary mapping panjang ke harga (untuk input manual)
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
        'efficiency_metrics': {}
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
            prices = generate_test_case(size)
        else:
            # Gunakan harga dari user, pastikan dalam format list
            prices = [user_prices[i] for i in range(1, size + 1)]
        
        metrics['prices'][size] = prices
        metrics['price_analysis'][size] = analyze_prices(prices)
        
        for name, impl in implementations.items():
            try:
                # Ukur waktu eksekusi
                start_time = time.time()
                result, peak_memory = measure_memory_usage(impl, prices, size)
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                # Simpan metrik
                if size not in metrics['execution_time']:
                    metrics['execution_time'][size] = {}
                metrics['execution_time'][size][name] = execution_time
                
                if size not in metrics['peak_memory']:
                    metrics['peak_memory'][size] = {}
                metrics['peak_memory'][size][name] = peak_memory
                
                if size not in metrics['solution_quality']:
                    metrics['solution_quality'][size] = {}
                metrics['solution_quality'][size][name] = result[0]
                
                # Analisis pola pemotongan dan efisiensi
                optimal_cuts = get_optimal_cuts(prices, size, result[0])
                if size not in metrics['cut_patterns']:
                    metrics['cut_patterns'][size] = {}
                metrics['cut_patterns'][size][name] = optimal_cuts
                
                if size not in metrics['efficiency_metrics']:
                    metrics['efficiency_metrics'][size] = {}
                efficiency_metrics = calculate_efficiency_metrics(
                    result[0], optimal_cuts, prices, execution_time, peak_memory
                )
                metrics['efficiency_metrics'][size][name] = efficiency_metrics
                
                print(f"\n{name} (Size {size}):")
                print(f"Hasil: {result[0]}")
                print(f"Waktu: {execution_time:.6f} detik")
                print(f"Peak Memory: {format_bytes(peak_memory)}")
                print(f"Pola Pemotongan: {format_cut_pattern(optimal_cuts)}")
                
            except Exception as e:
                print(f"Error in {name}: {str(e)}")
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
    """
    Menyimpan hasil analisis ke file dengan visualisasi dalam satu folder
    """
    import os
    from datetime import datetime
    
    # Buat direktori results jika belum ada
    base_results_dir = "results"
    if not os.path.exists(base_results_dir):
        os.makedirs(base_results_dir)
    
    # Buat subfolder dengan timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = f"{base_results_dir}/analysis_{timestamp}"
    os.makedirs(result_dir)
    
    # Generate visualisasi
    visualize_results(metrics, test_sizes, result_dir)
    
    # Simpan hasil analisis ke file markdown
    analysis_file = f"{result_dir}/analysis.md"
    
    with open(analysis_file, "w") as f:
        f.write("# Analisis Performa Rod Cutting Problem\n\n")
        
        # Kategorisasi implementasi
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

        # Hasil Pengujian
        f.write("## Hasil Pengujian\n\n")
        f.write("### Parameter Pengujian\n")
        f.write(f"Ukuran input yang diuji: {test_sizes}\n\n")
        
        f.write("### Detail Hasil per Ukuran Input\n\n")
        
        for size in test_sizes:
            f.write(f"#### Ukuran Input: {size}\n\n")
            
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
            
            # Solusi optimal dengan detail
            optimal_value = metrics['solution_quality'][size]['Bottom-up DP']
            optimal_cuts = get_optimal_cuts(metrics['prices'][size], size, optimal_value)
            f.write(f"**Solusi Optimal:**\n")
            f.write(f"- Nilai Total: {optimal_value}\n")
            
            # Hitung frekuensi setiap potongan
            cut_frequency = {}
            for cut in optimal_cuts:
                cut_frequency[cut] = cut_frequency.get(cut, 0) + 1
            
            # Tampilkan potongan dengan frekuensinya
            cuts_str = []
            for cut, freq in sorted(cut_frequency.items()):
                if freq > 1:
                    cuts_str.append(f"{cut}x{freq}")
                else:
                    cuts_str.append(str(cut))
            f.write(f"- Potongan: [{', '.join(cuts_str)}]\n")
            
            # Detail perhitungan
            f.write("- Detail perhitungan:\n")
            f.write("```\n")
            total = 0
            no_cut_price = metrics['prices'][size][size-1]
            
            # Tampilkan detail untuk setiap jenis potongan (sekali)
            for cut, freq in sorted(cut_frequency.items()):
                price = metrics['prices'][size][cut-1]
                total += price * freq
                price_per_unit = price / cut
                relative_saving = ((price_per_unit/(no_cut_price/size)) - 1) * 100
                f.write(f"  Panjang {cut} (x{freq}): {price} (harga per unit: {price_per_unit:.2f}, "
                       f"{'premium' if relative_saving > 0 else 'diskon'}: {abs(relative_saving):.1f}%)\n")
            
            total_saving = ((total/no_cut_price) - 1) * 100
            f.write(f"  Total: {total} ({abs(total_saving):.1f}% {'lebih tinggi' if total_saving > 0 else 'dibanding'} tanpa potongan)\n")
            f.write("```\n\n")
        
        # Visualisasi Performa
        f.write("## Visualisasi Performa\n\n")
        
        # Grafik waktu eksekusi
        f.write("### Grafik Waktu Eksekusi (skala log)\n")
        f.write("```\n")
        implementations = sorted(metrics['execution_time'][test_sizes[0]].keys())
        max_name_length = max(len(impl) for impl in implementations)
        
        for impl in implementations:
            times = [metrics['execution_time'][size][impl] for size in test_sizes]
            max_time = max(max(metrics['execution_time'][size].values()) for size in test_sizes)
            bar_length = 40
            
            f.write(f"{impl.ljust(max_name_length)} │ ")
            for time in times:
                length = int((bar_length * (1 + math.log10(time))) / (1 + math.log10(max_time)))
                f.write("█" * length + " " * (bar_length - length) + " ")
            f.write(f"│ {min(times):.6f}s - {max(times):.6f}s\n")
        
        f.write(" " * max_name_length + " └" + "─" * (bar_length * len(test_sizes) + len(test_sizes)) + "┘\n")
        f.write(" " * max_name_length + "  ")
        for size in test_sizes:
            f.write(f"{str(size).center(bar_length)} ")
        f.write("\n```\n\n")
        
        # Analisis Komparatif
        f.write("## Analisis Komparatif\n\n")
        
        # Time comparison
        f.write("### Perbandingan Waktu Eksekusi\n")
        for size in test_sizes:
            if size in metrics['execution_time']:
                f.write(f"\n#### Untuk ukuran input {size}:\n")
                times = metrics['execution_time'][size]
                if times:
                    fastest = min(times.values())
                    f.write("| Implementasi | Waktu (s) | Relatif terhadap tercepat |\n")
                    f.write("|--------------|-----------|-------------------------|\n")
                    for impl, time in sorted(times.items(), key=lambda x: x[1]):
                        relative = time / fastest
                        f.write(f"| {impl} | {time:.6f} | {relative:.2f}x |\n")
        
        # Memory comparison
        f.write("\n### Perbandingan Penggunaan Memori\n")
        for size in test_sizes:
            if size in metrics['memory_usage']:
                f.write(f"\n#### Untuk ukuran input {size}:\n")
                memories = metrics['memory_usage'][size]
                if memories:
                    min_memory = min(memories.values())
                    f.write("| Implementasi | Memori | Relatif terhadap minimum |\n")
                    f.write("|--------------|---------|------------------------|\n")
                    for impl, memory in sorted(memories.items(), key=lambda x: x[1]):
                        relative = memory / min_memory
                        f.write(f"| {impl} | {format_bytes(memory)} | {relative:.2f}x |\n")
        
        # Kesimpulan
        f.write("\n## Kesimpulan\n\n")
        f.write("### Waktu Eksekusi\n")
        f.write("1. Pendekatan brute force (Pure Recursive dan Iterative) menunjukkan pertumbuhan waktu eksponensial\n")
        f.write("2. Dynamic Programming memberikan peningkatan kinerja yang signifikan\n")
        f.write("3. Space Optimized DP memiliki kinerja serupa dengan Bottom-up DP\n\n")
        
        f.write("### Penggunaan Memori\n")
        f.write("1. Pure Recursive menggunakan memori untuk call stack\n")
        f.write("2. Iterative menggunakan memori untuk menyimpan kombinasi\n")
        f.write("3. Pendekatan DP menggunakan memori tambahan untuk menyimpan hasil\n")
        f.write("4. Space Optimized DP menunjukkan penggunaan memori yang paling efisien\n\n")
        
        f.write("### Rekomendasi Penggunaan\n")
        f.write("1. Untuk dataset kecil (n ≤ 10): Semua implementasi dapat digunakan\n")
        f.write("2. Untuk dataset menengah (10 < n ≤ 20): Gunakan implementasi DP\n")
        f.write("3. Untuk dataset besar (n > 20): Gunakan Bottom-up DP atau Space Optimized DP\n")
        f.write("4. Jika memori terbatas: Gunakan Space Optimized DP\n")
        f.write("5. Untuk tujuan pembelajaran/debugging: Gunakan Top-down DP\n")

        # Tambahkan analisis perbandingan yang lebih mendalam
        f.write("\n## Analisis Perbandingan Mendalam\n\n")
        
        f.write("### 1. Perbandingan Kompleksitas Teoritis\n\n")
        f.write("| Implementasi | Time Complexity | Space Complexity | Keterangan |\n")
        f.write("|--------------|-----------------|------------------|------------|\n")
        f.write("| Brute Force | O(2ⁿ) | O(n) | Mencoba semua kemungkinan kombinasi pemotongan |\n")
        f.write("| Top-down DP | O(n²) | O(n) | Memoization menghindari perhitungan berulang |\n")
        f.write("| Bottom-up DP | O(n²) | O(n) | Membangun solusi dari subproblem terkecil |\n")
        f.write("| Space Optimized DP | O(n²) | O(1) | Mengoptimalkan penggunaan memori |\n\n")
        
        f.write("### 2. Analisis Kinerja Empiris\n\n")
        
        # Hitung rata-rata peningkatan waktu untuk setiap implementasi
        f.write("#### Peningkatan Waktu Relatif\n\n")
        for size1, size2 in zip(test_sizes[:-1], test_sizes[1:]):
            f.write(f"\nPeringkatan dari ukuran {size1} ke {size2}:\n")
            for impl in metrics['execution_time'][size1].keys():
                time1 = metrics['execution_time'][size1][impl]
                time2 = metrics['execution_time'][size2][impl]
                increase = (time2 - time1) / time1 * 100
                f.write(f"- {impl}: {increase:.2f}% \n")
        
        f.write("\n### 3. Trade-offs Antar Implementasi\n\n")
        f.write("#### Brute Force vs Dynamic Programming\n")
        f.write("- **Kelebihan Brute Force:**\n")
        f.write("  - Implementasi sederhana dan mudah dipahami\n")
        f.write("  - Menemukan semua solusi yang mungkin\n")
        f.write("  - Cocok untuk dataset kecil\n")
        f.write("- **Kelebihan Dynamic Programming:**\n")
        f.write("  - Efisiensi waktu yang jauh lebih baik\n")
        f.write("  - Dapat menangani dataset besar\n")
        f.write("  - Menyimpan solusi sub-masalah\n\n")
        
        f.write("#### Top-down vs Bottom-up DP\n")
        f.write("- **Top-down (Memoization):**\n")
        f.write("  - Lebih intuitif dan mirip dengan rekursi\n")
        f.write("  - Hanya menghitung sub-masalah yang diperlukan\n")
        f.write("  - Overhead dari rekursi\n")
        f.write("- **Bottom-up (Tabulation):**\n")
        f.write("  - Menghindari overhead rekursi\n")
        f.write("  - Menghitung semua sub-masalah secara sistematis\n")
        f.write("  - Lebih efisien dalam penggunaan memori\n\n")
        
        f.write("### 4. Kesimpulan dan Rekomendasi\n\n")
        f.write("Berdasarkan hasil pengujian empiris:\n\n")
        
        # Hitung rata-rata waktu eksekusi untuk setiap implementasi
        avg_times = {}
        for impl in metrics['execution_time'][test_sizes[0]].keys():
            times = [metrics['execution_time'][size][impl] for size in test_sizes]
            avg_times[impl] = sum(times) / len(times)
        
        # Urutkan implementasi berdasarkan rata-rata waktu
        sorted_impls = sorted(avg_times.items(), key=lambda x: x[1])
        
        f.write("1. **Performa Terbaik:** " + sorted_impls[0][0] + "\n")
        f.write("2. **Performa Menengah:** " + sorted_impls[1][0] + " dan " + sorted_impls[2][0] + "\n")
        f.write("3. **Performa Terendah:** " + sorted_impls[-1][0] + "\n\n")
        
        f.write("**Rekomendasi Penggunaan:**\n")
        f.write("1. Untuk dataset kecil (n ≤ 10): Semua implementasi dapat digunakan\n")
        f.write("2. Untuk dataset menengah (10 < n ≤ 20): Gunakan implementasi DP\n")
        f.write("3. Untuk dataset besar (n > 20): Gunakan Bottom-up DP atau Space Optimized DP\n")
        f.write("4. Jika memori terbatas: Gunakan Space Optimized DP\n")
        f.write("5. Untuk tujuan pembelajaran/debugging: Gunakan Top-down DP\n")
        
        # Tambahkan referensi ke gambar
        f.write("\n## Visualisasi Hasil\n\n")
        f.write("### Perbandingan Waktu Eksekusi\n")
        f.write("![Perbandingan Waktu Eksekusi](execution_time_comparison.png)\n\n")
        
        f.write("### Analisis Harga per Ukuran\n")
        for size in test_sizes:
            f.write(f"#### Ukuran Rod: {size}\n")
            f.write(f"![Analisis Harga Size {size}](price_analysis_size_{size}.png)\n\n")
        
        f.write("### Analisis Pola Pemotongan\n")
        f.write("![Analisis Pola Pemotongan](cut_pattern_analysis.png)\n\n")
        
        f.write("### Perbandingan Penggunaan Memori\n")
        f.write("![Perbandingan Penggunaan Memori](memory_usage_comparison.png)\n\n")
        f.write("### Pertumbuhan Penggunaan Memori\n")
        f.write("![Pertumbuhan Penggunaan Memori](memory_growth.png)\n\n")
    
    print(f"Analysis saved to {analysis_file}")
    
    return result_dir