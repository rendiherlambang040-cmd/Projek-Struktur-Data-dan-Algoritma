import jenis_data
import time
import tracemalloc
import sys
sys.setrecursionlimit(3000)


def quick_sort(arr):

    if len(arr) <= 1:
        return arr
    else:
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

    return quick_sort(left) + middle + quick_sort(right)


if __name__ == "__main__":
    data_uji = jenis_data.data_permutasi
    log_durasi = []
    log_memory = []
    jumlah_percobaan = 20
    print("Data sebelum diurutkan:")
    print(data_uji)
    for i in range(jumlah_percobaan):

        tracemalloc.start()

        waktu_mulai = time.perf_counter_ns()
        data_terurut = quick_sort(data_uji)
        waktu_selesai = time.perf_counter_ns()
        durasi = waktu_selesai-waktu_mulai
        milidetik = durasi / 1000000
        memori_sekarang, memori_puncak = tracemalloc.get_traced_memory()

        tracemalloc.stop()
        log_durasi.append(milidetik)

        memori_puncak_kb = memori_puncak / 1024
        log_memory.append(memori_puncak_kb)
        print(f"\nPercobaan ke-{i + 1}: {milidetik:,.2f} milidetik\nPuncak memori yang digunakan: {memori_puncak_kb:.2f} KB")

    print(f"\ndata setelah diurutkan: \n{data_terurut}")
    rata_rata_durasi = sum(log_durasi) / len(log_durasi)
    rata_rata_memory = sum(log_memory) / len(log_memory)
    print(f"rata rata durasi: {rata_rata_durasi:,.2f} nanodetik")
    print(f"rata rata memory: {rata_rata_memory:,.2f} KB")


