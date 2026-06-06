import time
import tracemalloc
import statistics
import sys
from collections import Counter
sys.setrecursionlimit(3000)
from jenis_data import permutasi, non_permutasi, terurut, terurut_terbalik, hampir_terurut


def quick_sort(arr, jenis_pivot):
    if len(arr) <= 1:
        return arr

    if jenis_pivot == "mean":
        pivot = sum(arr) / len(arr)
    elif jenis_pivot == "median":
        pivot = statistics.median(arr)
    elif jenis_pivot == "modus":
        frekuensi = Counter(arr)
        pivot = frekuensi.most_common(1)[0][0]
    elif jenis_pivot == "awal":
        pivot = arr[0]
    elif jenis_pivot == "tengah":
        pivot = arr[len(arr) // 2]
    elif jenis_pivot == "akhir":
        pivot = arr[-1]

    left = []
    middle = []
    right = []

    for item in arr:
        if item < pivot:
            left.append(item)
        elif item > pivot:
            right.append(item)
        else:
            middle.append(item)

    return quick_sort(left, jenis_pivot) + middle + quick_sort(right, jenis_pivot)


if __name__ == "__main__":
    kamus_data = {
        "permutasi": permutasi,
        "non_permutasi": non_permutasi,
        "terurut": terurut,
        "terurut_terbalik": terurut_terbalik,
        "hampir_terurut": hampir_terurut
    }

    user_pivot = input("pilih pivot yang ingin digunakan (mean/median/modus/awal/tengah/akhir): ").lower()
    pilihan_data = input("pilih jenis data yang ingin digunakan (permutasi/non_permutasi/terurut/terurut_terbalik/hampir_terurut): ").lower()

    if pilihan_data in kamus_data:
        data_asli = kamus_data[pilihan_data]
    else:
        print("Jenis data tidak valid!")
        sys.exit()

    log_durasi = []
    log_memory = []
    jumlah_percobaan = 20

    print("\nData sebelum diurutkan")
    print(data_asli)

    for i in range(jumlah_percobaan):
        data_uji = data_asli.copy()

        tracemalloc.start()

        waktu_mulai = time.perf_counter_ns()
        data_terurut = quick_sort(data_uji, user_pivot)
        waktu_selesai = time.perf_counter_ns()

        memori_sekarang, memori_puncak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        durasi = waktu_selesai - waktu_mulai
        milidetik = durasi / 1_000_000
        log_durasi.append(milidetik)

        memori_puncak_kb = memori_puncak / 1024
        log_memory.append(memori_puncak_kb)
        print(f"Percobaan ke-{i + 1}: {milidetik:,.2f} miudetik | Puncak memori: {memori_puncak_kb:.2f} KB")

    print(f"\nData setelah diurutkan: \n{data_terurut}")

    rata_rata_durasi = sum(log_durasi) / len(log_durasi)
    rata_rata_memory = sum(log_memory) / len(log_memory)
    print(f"\nRata-rata durasi: {rata_rata_durasi:,.2f} miudetik")
    print(f"Rata-rata memory: {rata_rata_memory:,.2f} KB")