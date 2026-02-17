import sys, time
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox, QSpinBox
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from bruteforce import parsing, langkah_bruteforce, print_board, validasi_input

def build_color(board_lines):
    symbols = sorted({ch for row in board_lines for ch in row if ch != '#'})
    m = len(symbols)
    palette = {}
    if m == 0: return palette
    for i, sym in enumerate(symbols):
        hue = int(360 * i / m)
        sat = 150
        val = 235
        palette[sym] = QColor.fromHsv(hue, sat, val)
    return palette

def cell_size(n, max_canvas=1000, margin=20, min_cell=6, max_cell=60):
    usable = max_canvas - 2 * margin
    cell = usable // max(1, n)
    return max(min_cell, min(max_cell, cell))

def board_image(base_lines, queen_lines, max_canvas=1000, margin=20):
    n = len(base_lines)
    cell = cell_size(n, max_canvas=max_canvas, margin=margin)
    w = margin * 2 + n * cell
    h = margin * 2 + n * cell
    pix = QPixmap(w, h)
    pix.fill(QColor("#FFF7ED"))
    palette = build_color(base_lines)
    p = QPainter(pix)
    font = QFont("Segoe UI Symbol", max(8, int(cell * 0.65)))
    font.setBold(True)
    p.setFont(font)
    for r in range(n):
        for c in range(n):
            x = margin + c * cell
            y = margin + r * cell
            ch_base = base_lines[r][c]
            fill = palette.get(ch_base, QColor("#FFFFFF"))
            p.fillRect(x, y, cell, cell, fill)
            p.setPen(QColor("#3B1D1A"))
            p.drawRect(x, y, cell, cell)
            if queen_lines[r][c] == '#':
                p.setPen(QColor("#111111"))
                p.drawText(x, y, cell, cell, Qt.AlignmentFlag.AlignCenter, "#")
    p.end()
    return pix

class SolverThread(QThread):
    progress = pyqtSignal(int,list)
    finished_ok = pyqtSignal(int,list)
    finished_fail = pyqtSignal(int,list)
    error = pyqtSignal(str)
    
    def __init__(self,board,update_every=10,parent=None):
        super().__init__(parent)
        self.board = board
        self.update_every = update_every
    def run(self):
        try:
            start = time.perf_counter()
            steps = langkah_bruteforce(self.board, skip_time=True)
            solusi = None
            last_kasus = 0
            last_lines = print_board(self.board, None)
            for kasus, queen, valid in steps:
                last_kasus = kasus
                last_lines = print_board(self.board,queen)
                if valid:
                    end = time.perf_counter()
                    total_waktu = (end - start) * 1000
                    solusi = queen
                    solusi_lines = print_board(self.board, solusi)
                    self.finished_ok.emit(kasus, solusi_lines + [f"Waktu eksekusi: {total_waktu:.2f} ms"])
                    return
                if kasus % self.update_every == 0: self.progress.emit(kasus,last_lines)
            end = time.perf_counter()
            total_waktu = (end - start) * 1000
            self.finished_fail.emit(last_kasus, last_lines + [f"Waktu eksekusi: {total_waktu:.2f} ms"])
        except Exception as e: self.error.emit(str(e))
    
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Queens Solver (Tucil1_13524109)")
        self.resize(900,650)
        self.input_path = None
        self.board = None
        self.worker = None
        self.last_result_text = ""
        self.last_result_board_lines = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        top = QHBoxLayout()
        self.btn_open = QPushButton("Open File .txt")
        self.btn_run = QPushButton("Run")
        self.btn_save = QPushButton("Save Result .txt")
        self.btn_save_img = QPushButton("Save Image")
        self.btn_run.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_save_img.setEnabled(False)

        top.addWidget(self.btn_open)
        top.addWidget(self.btn_run)
        top.addWidget(self.btn_save)
        top.addWidget(self.btn_save_img)
        top.addStretch(1)

        top.addWidget(QLabel("Update setiap"))
        self.spin_update = QSpinBox()
        self.spin_update.setRange(1, 10_000_000)
        self.spin_update.setValue(10)
        top.addWidget(self.spin_update)
        top.addWidget(QLabel("kasus"))
        root.addLayout(top)

        self.lbl_status = QLabel("Belum ada file yang dibuka")
        root.addWidget(self.lbl_status)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlaceholderText("Live Update")
        root.addWidget(self.text, 1)

        self.btn_open.clicked.connect(self.open_file)
        self.btn_run.clicked.connect(self.run_solver)
        self.btn_save.clicked.connect(self.save_output)
        self.btn_save_img.clicked.connect(self.save_image)

    def open_file(self):
        path, _= QFileDialog.getOpenFileName(self, "Pilih File Input", "", "Text Files (*.txt);;All Files (*)")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f: lines = f.readlines()
            board = parsing(lines)
            if not validasi_input(board):
                self.input_path = path
                self.board = None
                preview = "\n".join(print_board(board, None))
                self.text.setPlainText(preview)
                self.lbl_status.setText("Board tidak valid")
                self.btn_run.setEnabled(False)
                self.btn_save.setEnabled(False)
                self.last_result_text = ""
                self.last_result_board_lines = None
                self.btn_save_img.setEnabled(False)
                QMessageBox.warning(self, "Input tidak valid", "Board tidak valid!\n\n" "Syarat:\n" "- Ukuran NxN\n" "- Hanya mengandung A-Z\n" "- Jumlah daerah (region warna) = N\n" "- N <= 26\n")
                return
            self.input_path = path
            self.board = board
            preview = "\n".join(print_board(board,None))
            self.text.setPlainText(preview)
            self.lbl_status.setText(f"File dibuka: {path}")
            self.btn_run.setEnabled(True)
            self.btn_save.setEnabled(False)
            self.last_result_text = ""
            self.btn_save_img.setEnabled(False)
            self.last_result_board_lines = None
        except Exception as e: QMessageBox.critical(self, "Error", f"Gagal Membuka File:\n{e}")

    def run_solver(self):
        if self.board is None: 
            QMessageBox.warning(self, "Warning", "Buka file input terlebih dahulu")
            return
        self.btn_run.setEnabled(False)
        self.btn_open.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_save_img.setEnabled(False)
        update_every = self.spin_update.value()
        self.lbl_status.setText("Running...")
        self.worker = SolverThread(self.board, update_every=update_every)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished_ok.connect(self.on_finished_ok)
        self.worker.finished_fail.connect(self.on_finished_fail)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_progress(self, kasus, board_lines):
        text = []
        text.append(f"Progress ({kasus} kasus)")
        text.extend(board_lines)
        text.append("")
        self.text.setPlainText("\n".join(text))

    def on_finished_ok(self, kasus, solusi_lines):
        self.btn_open.setEnabled(True)
        self.btn_run.setEnabled(True)
        self.btn_save.setEnabled(True)
        message = []
        message.extend(solusi_lines)
        message.append("")
        message.append(f"Banyak kasus yang ditinjau: {kasus} kasus")
        out = "\n".join(message)
        self.text.setPlainText(out)
        self.lbl_status.setText("Solusi Ditemukan")
        self.last_result_text = out
        self.last_result_board_lines = solusi_lines
        self.btn_save_img.setEnabled(True)
        self.ask_save()
        self.worker = None
    
    def on_finished_fail(self, kasus, last_lines):
        self.btn_open.setEnabled(True)
        self.btn_run.setEnabled(True)
        self.btn_save.setEnabled(True)
        awal_lines = print_board(self.board, None)
        message = []
        message.extend(awal_lines)
        message.append("")
        message.append(f"Tidak Ada Solusi")
        if last_lines and last_lines[-1].startswith("Waktu eksekusi:"): message.append(last_lines[-1])
        message.append(f"Banyak kasus yang ditinjau: {kasus} kasus")
        out = "\n".join(message)
        self.text.setPlainText(out)
        self.lbl_status.setText("Tidak Ada Solusi")
        self.last_result_text = out
        self.last_result_board_lines = None
        self.btn_save_img.setEnabled(False)
        self.ask_save()
        self.worker = None

    def on_error(self, message):
        self.btn_open.setEnabled(True)
        self.btn_run.setEnabled(True)
        self.btn_save.setEnabled(False)
        self.last_result_board_lines = None
        self.btn_save_img.setEnabled(False)
        QMessageBox.critical(self, "Error", f"Terjadi error:\n{message}")
        self.worker = None

    def ask_save(self):
        if not self.last_result_text: return
        answer = QMessageBox.question(self, "Simpan hasil?", "Ingin simpan hasil ke file .txt baru?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes: self.save_output()

    def save_output(self):
        if not self.last_result_text:
            QMessageBox.information(self, "Info", "Belum ada hasil untuk disimpan")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save as", "solusi.txt", "Text Files (*.txt);;All Files (*)")
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f: f.write(self.last_result_text)
            QMessageBox.information(self, "Berhasil", f"Hasil disimpan ke:\n{path}")
        except Exception as e: QMessageBox.critical(self, "Error", f"Gagal menyimpan:\n{e}")
    
    def save_image(self):
        if not self.last_result_board_lines:
            QMessageBox.information(self, "Info", "Belum ada solusi untuk disimpan sebagai gambar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save image as", "solusi.png", "PNG Image (*.png)")
        if not path: return
        try:
            pix = board_image(print_board(self.board, None), self.last_result_board_lines, max_canvas=1200, margin=20)
            ok = pix.save(path, "PNG")
            if not ok: raise RuntimeError("Gagal menyimpan PNG.")
            QMessageBox.information(self, "Berhasil", f"Gambar disimpan ke:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan gambar:\n{e}")

def main():
    app = QApplication(sys.argv)
    w = Main()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()