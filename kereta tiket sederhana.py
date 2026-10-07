import os
import platform
import random
import sqlite3
import string
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

# 1. DATABASE LOKAL (Pustaka Bawaan: sqlite3)
DB_NAME = "tiket_kereta_laptop.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_booking TEXT,
            nama TEXT,
            nik TEXT,
            rute TEXT,
            kereta TEXT,
            kelas TEXT,
            jumlah INTEGER,
            total INTEGER,
            metode TEXT,
            waktu TEXT
        )
    """
    )
    conn.commit()
    conn.close()


init_db()

# DATA RUTE & HARGA
DATA_RUTE = {
    "Ketapang (Banyuwangi) -> Gambir (Jakarta)": {
        "kereta": "KA Blambangan Ekspres",
        "harga": 380000,
    },
    "Surabaya Pasar Turi -> Gambir (Jakarta)": {
        "kereta": "KA Argo Bromo Anggrek",
        "harga": 520000,
    },
    "Malang -> Bandung": {"kereta": "KA Gajayana", "harga": 450000},
}

MULTIPLIER = {"Ekonomi": 1.0, "Eksekutif": 1.8, "Luxury": 2.5}


# 2. INTEGRASI APLIKASI BAWAAN LAPTOP (Notepad / TextEdit)
def buka_di_aplikasi_laptop(filepath):
    sistem = platform.system()
    if sistem == "Windows":
        os.startfile(
            filepath
        )  # Membuka otomatis dengan Notepad / Text Viewer bawaan Windows
    elif sistem == "Darwin":  # macOS
        subprocess.call(["open", filepath])
    else:  # Linux
        subprocess.call(["xdg-open", filepath])


# 3. GUI ANTARMUKA (Pustaka Bawaan: tkinter)
class AplikasiTiketKereta:

    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Tiket Kereta Api - Desktop App")
        self.root.geometry("460x540")
        self.root.resizable(False, False)

        tk.Label(
            root,
            text="PEMESANAN TIKET KERETA API",
            font=("Helvetica", 14, "bold"),
        ).pack(pady=12)

        # Form Input
        frame_form = tk.Frame(root)
        frame_form.pack(padx=20, pady=5, fill="x")

        tk.Label(frame_form, text="Nama Pemesan:").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.txt_nama = tk.Entry(frame_form, width=30)
        self.txt_nama.grid(row=0, column=1, pady=5)

        tk.Label(frame_form, text="NIK / KTP:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.txt_nik = tk.Entry(frame_form, width=30)
        self.txt_nik.grid(row=1, column=1, pady=5)

        tk.Label(frame_form, text="Rute Perjalanan:").grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.combo_rute = ttk.Combobox(
            frame_form, values=list(DATA_RUTE.keys()), width=27, state="readonly"
        )
        self.combo_rute.current(0)
        self.combo_rute.grid(row=2, column=1, pady=5)

        tk.Label(frame_form, text="Kelas Kereta:").grid(
            row=3, column=0, sticky="w", pady=5
        )
        self.combo_kelas = ttk.Combobox(
            frame_form,
            values=list(MULTIPLIER.keys()),
            width=27,
            state="readonly",
        )
        self.combo_kelas.current(0)
        self.combo_kelas.grid(row=3, column=1, pady=5)

        tk.Label(frame_form, text="Jumlah Tiket:").grid(
            row=4, column=0, sticky="w", pady=5
        )
        self.txt_jumlah = tk.Entry(frame_form, width=30)
        self.txt_jumlah.insert(0, "1")
        self.txt_jumlah.grid(row=4, column=1, pady=5)

        tk.Label(frame_form, text="Kode Voucher:").grid(
            row=5, column=0, sticky="w", pady=5
        )
        self.txt_voucher = tk.Entry(frame_form, width=30)
        self.txt_voucher.grid(row=5, column=1, pady=5)

        tk.Label(frame_form, text="Pembayaran:").grid(
            row=6, column=0, sticky="w", pady=5
        )
        self.combo_bayar = ttk.Combobox(
            frame_form,
            values=["QRIS", "Virtual Account", "Cash"],
            width=27,
            state="readonly",
        )
        self.combo_bayar.current(0)
        self.combo_bayar.grid(row=6, column=1, pady=5)

        # Tombol Proses
        btn_proses = tk.Button(
            root,
            text="PROSES & CETAK DI NOTEPAD",
            bg="#2196F3",
            fg="white",
            font=("Helvetica", 10, "bold"),
            command=self.proses_transaksi,
        )
        btn_proses.pack(pady=15, fill="x", padx=20)

        # Log Status
        self.lbl_status = tk.Label(
            root, text="Status: Siap bertransaksi", fg="gray"
        )
        self.lbl_status.pack(pady=5)

    def proses_transaksi(self):
        nama = self.txt_nama.get().strip()
        nik = self.txt_nik.get().strip()
        rute_key = self.combo_rute.get()
        kelas = self.combo_kelas.get()
        voucher = self.txt_voucher.get().strip().upper()
        metode = self.combo_bayar.get()

        if not nama or not nik:
            messagebox.showwarning(
                "Peringatan", "Nama dan NIK wajib diisi!"
            )
            return

        try:
            jumlah = int(self.txt_jumlah.get())
            if jumlah <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Peringatan", "Jumlah tiket harus berupa angka positif!"
            )
            return

        # Perhitungan Harga
        detail_rute = DATA_RUTE[rute_key]
        harga_dasar = detail_rute["harga"]
        nama_kereta = detail_rute["kereta"]

        harga_satuan = int(harga_dasar * MULTIPLIER[kelas])
        subtotal = harga_satuan * jumlah

        diskon = 0
        if voucher == "KERETAJAWA":
            diskon = int(subtotal * 0.10)
        elif voucher == "SULTAN50K":
            diskon = 50000

        total_bayar = max(0, subtotal - diskon)
        kode_booking = "NJ" + "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        waktu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # 1. Simpan Ke Database SQLite (Bawaan Python)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO transaksi (kode_booking, nama, nik, rute, kereta, kelas, jumlah, total, metode, waktu)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                kode_booking,
                nama,
                nik,
                rute_key,
                nama_kereta,
                kelas,
                jumlah,
                total_bayar,
                metode,
                waktu,
            ),
        )
        conn.commit()
        conn.close()

        # 2. Generasi File Struk (.txt)
        filename = f"Struk_{kode_booking}.txt"
        isi_struk = f"""==================================================
              STRUK BUKTI PEMBAYARAN TIKET
               PT KERETA API NUSA JAVA
==================================================
Kode Booking    : {kode_booking}
Waktu Transaksi : {waktu}
Nama Pemesan    : {nama}
NIK             : {nik}
--------------------------------------------------
Rute            : {rute_key}
Kereta          : {nama_kereta} ({kelas})
Jumlah Tiket    : {jumlah} Penumpang
--------------------------------------------------
Harga @ Tiket   : Rp {harga_satuan:,}
Subtotal        : Rp {subtotal:,}
Diskon          : Rp {diskon:,}
TOTAL BAYAR     : Rp {total_bayar:,}
Metode Bayar    : {metode}
Status          : LUNAS (Database Linked)
==================================================
  * Tunjukkan struk ini saat boarding di stasiun.
==================================================
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(isi_struk)

        # 3. Buka File Struk Menggunakan Aplikasi Laptop Bawaan (Notepad)
        buka_di_aplikasi_laptop(filename)

        self.lbl_status.config(
            text=f"Sukses! Struk dibuka di Notepad ({filename})", fg="green"
        )
        messagebox.showinfo(
            "Sukses",
            f"Transaksi Berhasil!\n\nStruk transaksi telah dibuka secara otomatis menggunakan aplikasi Notepad di laptop Anda.",
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = AplikasiTiketKereta(root)
    root.mainloop()