import sys
from src.utils.test_utils import test_performance, save_analysis_to_file

def get_user_input():
    """
    Mendapatkan input dari user untuk panjang batang dan harga
    """
    print("\nRod Cutting Problem - Input Data")
    print("=" * 40)
    
    # Input panjang batang yang akan diuji
    print("\nMasukkan ukuran batang yang akan diuji")
    print("(Pisahkan dengan koma, contoh: 5,7,10,13)")
    test_sizes_input = input("Ukuran batang: ")
    test_sizes = [int(x.strip()) for x in test_sizes_input.split(',')]
    
    # Input panjang potong yang diperbolehkan
    print("\nMasukkan panjang potong yang diperbolehkan")
    print("(Pisahkan dengan koma, contoh: 2,5,7)")
    print("Tekan Enter untuk mengizinkan semua panjang")
    allowed_input = input("Panjang potong: ")
    allowed_lengths = None
    if allowed_input.strip():
        allowed_lengths = [int(x.strip()) for x in allowed_input.split(',')]
    
    # Input harga untuk setiap panjang
    prices = {}
    print("\nMasukkan harga untuk setiap panjang batang")
    if allowed_lengths:
        print("Masukkan harga hanya untuk panjang yang diperbolehkan:")
        for length in allowed_lengths:
            while True:
                try:
                    price = int(input(f"Harga untuk panjang {length}: "))
                    prices[length] = price
                    break
                except ValueError:
                    print("Masukkan angka yang valid!")
    else:
        print("Format: panjang,harga (contoh: 1,10)")
        print("Ketik 'selesai' untuk mengakhiri input")
        
        while True:
            price_input = input("Masukkan panjang,harga (atau 'selesai'): ")
            if price_input.lower() == 'selesai':
                break
            
            try:
                length, price = map(int, price_input.split(','))
                prices[length] = price
            except ValueError:
                print("Format salah! Gunakan format: panjang,harga")
                continue
    
    return test_sizes, prices, allowed_lengths

def main():
    # Set recursion limit
    sys.setrecursionlimit(1500000)
    
    # Pilihan mode: otomatis atau input user
    print("Rod Cutting Analysis")
    print("1. Gunakan test case otomatis")
    print("2. Input manual")
    choice = input("Pilih mode (1/2): ")
    
    if choice == "1":
        # Test sizes dengan justifikasi:
        # Rentang panjang kecil ( n≤10).
        # Rentang panjang besar ( n>10).
        test_sizes = [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 20]
        
        # Jalankan pengujian dengan generate_test_case
        metrics = test_performance(test_sizes)
    else:
        # Dapatkan input dari user
        test_sizes, prices, allowed_lengths = get_user_input()
        
        # Validasi input
        max_size = max(test_sizes)
        if not all(length in prices for length in range(1, max_size + 1)):
            print("\nPeringatan: Beberapa panjang tidak memiliki harga.")
            print("Program akan menggunakan interpolasi linear untuk harga yang hilang.")
            
            # Interpolasi harga yang hilang
            sorted_lengths = sorted(prices.keys())
            for length in range(1, max_size + 1):
                if length not in prices:
                    # Cari dua titik terdekat untuk interpolasi
                    left = max((l for l in sorted_lengths if l < length), default=None)
                    right = min((l for l in sorted_lengths if l > length), default=None)
                    
                    if left is None:
                        # Extrapolasi dari kanan
                        prices[length] = int(prices[right] * (length / right))
                    elif right is None:
                        # Extrapolasi dari kiri
                        prices[length] = int(prices[left] * (length / left))
                    else:
                        # Interpolasi linear
                        slope = (prices[right] - prices[left]) / (right - left)
                        prices[length] = int(prices[left] + slope * (length - left))
        
        # Jalankan pengujian dengan harga yang ditentukan user
        metrics = test_performance(test_sizes, prices, allowed_lengths)
    
    # Simpan hasil analisis
    result_dir = save_analysis_to_file(metrics, test_sizes)
    print(f"\nAnalisis lengkap tersimpan di: {result_dir}")

if __name__ == "__main__":
    main()