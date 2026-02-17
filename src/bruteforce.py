def parsing(lines):
    board = []
    for baris in lines:
        line = baris.strip()
        if line == "" : continue
        if " " in line:
            hasil = line.split()
        else:
            hasil = list(line)
        board.append(hasil)
    return board

def validasi_input(board):
    n = len(board)
    if n == 0: 
        return False
    for row in board:
        if len(row) != n: 
            return False
    for b in range(n):
        for k in range(n):
            now = board[b][k]
            if len(now) != 1 or not('A' <= now <= 'Z'):
                return False
    if n > 26:
        return False
    daerah = set_daerah(board)
    if len(daerah) != n:
        return False
    return True

def set_daerah(board):
    n = len(board)
    s = set()
    for b in range(n):
        for k in range(n):
            s.add(board[b][k])
    return s

def cek_daerah(board, queen):
    daerah = set()
    for (b,k) in queen:
        now = board[b][k]
        if now in daerah: return False
        daerah.add(now)
    return True

def cek_tetangga(queen):
    posisi_queen = set(queen)
    for b, k in queen:
        if (b-1, k-1) in posisi_queen or (b-1, k) in posisi_queen or (b-1, k+1) in posisi_queen or (b, k-1) in posisi_queen or (b, k+1) in posisi_queen or (b+1, k-1) in posisi_queen or (b+1, k) in posisi_queen or (b+1, k+1) in posisi_queen: return False
    return True

def cek_kolom_baris(queen, n):
    if len(queen) != n : return False
    baris = set()
    kolom = set()
    for (b,k) in queen:
        if b in baris or k in kolom: return False
        baris.add(b)
        kolom.add(k)
    return True

def bangun_permutasi(array):
    i = len(array) - 2
    while i>=0 and array[i]>=array[i+1]: i -= 1
    if i < 0 : return False
    j = len(array) - 1
    while array[j]<=array[i]: j -= 1
    temp = array[i]
    array[i] = array[j]
    array[j] = temp
    kiri = i + 1
    kanan = len(array) - 1
    while kiri < kanan:
        temp = array[kiri]
        array[kiri] = array[kanan]
        array[kanan] = temp
        kiri += 1
        kanan -= 1
    return True

def semua_kemungkinan(n):
    permutasi = list(range(n))
    yield permutasi[:]
    while bangun_permutasi(permutasi): yield permutasi[:]

def langkah_bruteforce(board, skip_time=False):
    if not skip_time and not validasi_input(board):
        yield 0, None, False
        return
    n = len(board)
    kasus = 0
    for permutasi in semua_kemungkinan(n):
        kasus += 1
        queen = [(r,permutasi[r]) for r in range(n)]
        valid = cek_daerah(board,queen) and cek_tetangga(queen) and cek_kolom_baris(queen,n)
        yield kasus, queen, valid
        if valid: return

def hasil_bruteforce(board, skip_time=False):
    if not skip_time and not validasi_input(board): return None, 0
    n = len(board)
    kasus = 0
    for permutasi in semua_kemungkinan(n):
        kasus += 1
        queen = [(r,permutasi[r]) for r in range(n)]
        if cek_daerah(board,queen) and cek_tetangga(queen) and cek_kolom_baris(queen,n): return queen, kasus
    return None, kasus

def print_board(board,queen):
    copy_board = [baris[:] for baris in board]
    if queen is not None:
        for (b,k) in queen: copy_board[b][k] = '#'
    hasil = []
    for baris in copy_board: hasil.append(''.join(baris))
    return hasil