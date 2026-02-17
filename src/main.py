import time, os
from bruteforce import parsing, langkah_bruteforce, print_board, validasi_input

print("Masukkan path file input (.txt)!")
print("Contoh: ../test/tc1.txt")
input_path = input("Path file: ").strip()

if not os.path.exists(input_path):
    print("File tidak ditemukan")
    exit()

with open(input_path, "r", encoding="utf-8") as f: lines = f.readlines()

board = parsing(lines)
if not validasi_input(board):
    print("Board tidak valid")
    exit()
UPDATE = 100
solusi = None
last_kasus = 0
log_lines = []
start = time.perf_counter()
steps = langkah_bruteforce(board, skip_time=True)

for kasus, queen, valid in steps:
    last_kasus = kasus
    if valid:
        solusi = queen
        print("Solusi ditemukan di kasus:", kasus)
        break
    if kasus % UPDATE == 0:
        print("Progress (kasus =", kasus, "):")
        for baris in print_board(board,queen):
            print(baris)
        print()
end = time.perf_counter()
total_waktu = (end - start) * 1000
if solusi is None:
    print("\nTidak ada solusi")
else:
    for baris in print_board(board,solusi):
        print(baris)
        log_lines.append(baris)
print()
print(f"Waktu eksekusi: {total_waktu:.2f} ms")
print(f"Banyak kasus yang ditinjau: {last_kasus} kasus")
jawab = input("\nSimpan hasil ke file .txt? (y/n): ").strip().lower()
if jawab == "y":
    output_path = input("Nama file output (contoh: solusi.txt): ").strip()
    with open(output_path, "w", encoding="utf-8") as f: f.write("\n".join(log_lines))
    print(f"Hasil disimpan ke file: {output_path}")
else: print("Hasil tidak disimpan")