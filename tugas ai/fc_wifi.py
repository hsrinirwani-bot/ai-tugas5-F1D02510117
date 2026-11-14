t"""
fc_wifi.py - Sistem pakar sederhana (Forward Chaining)
Topik: laptop tidak bisa internet lewat WiFi.
Cara jalan: python fc_wifi.py
"""
import json
import sys

FILE_ATURAN = "kb_wifi.json"


def muat(nama_file):
    with open(nama_file, encoding="utf-8") as f:
        return json.load(f)


def syarat_terpenuhi(aturan, memori):
    """Cek syarat aturan. Mode 'dan': semua harus ada. Mode 'atau': salah satu cukup.
    Mengembalikan (terpenuhi?, daftar syarat yang ada di memori)."""
    ada = [s for s in aturan["jika"] if s in memori]
    if aturan["mode"] == "dan":
        return len(ada) == len(aturan["jika"]), ada
    return len(ada) > 0, ada


def cari_fakta_dasar(daftar_aturan):
    """Fakta dasar = syarat yang tidak pernah jadi hasil (THEN) aturan manapun.
    Hanya fakta ini yang ditanyakan ke user."""
    hasil = {a["maka"] for a in daftar_aturan}
    dasar = []
    for a in daftar_aturan:
        for s in a["jika"]:
            if s not in hasil and s not in dasar:
                dasar.append(s)
    return dasar


def tanya_user(fakta_dasar):
    print("Jawab y/t.")
    memori = []
    for i, f in enumerate(fakta_dasar, 1):
        while True:
            jawab = input(f"{i}. Apakah {f}? (y/t) > ").strip().lower()
            if jawab in ("y", "t"):
                break
            print("   Ketik y atau t saja.")
        if jawab == "y":
            memori.append(f)
    return memori


def forward_chaining(daftar_aturan, memori):
    """Jalankan aturan satu per siklus sampai tidak ada aturan baru."""
    memori = list(memori)
    alasan = {}   # hasil -> (id aturan, syarat yang dipakai)
    log = []
    siklus = 0
    while True:
        siklus += 1
        cocok = []
        for a in daftar_aturan:
            if a["maka"] in memori:      # hasilnya sudah ada, jangan dijalankan lagi
                continue
            ok, dipakai = syarat_terpenuhi(a, memori)
            if ok:
                cocok.append((a, dipakai))
        if not cocok:
            log.append(f"Siklus {siklus}: tidak ada aturan baru, berhenti")
            break
        a, dipakai = cocok[0]            # ambil aturan pertama yang cocok
        memori.append(a["maka"])
        alasan[a["maka"]] = (a["id"], dipakai)
        log.append(f"Siklus {siklus}: {a['id']} -> {a['maka']}")
    return memori, alasan, log


def cetak_alasan(fakta, alasan, aturan_by_id, sudah, tingkat=0):
    """Cetak rantai alasan secara rekursif (dari kesimpulan turun ke fakta).
    'sudah' mencegah fakta yang sama dijelaskan berulang-ulang."""
    spasi = "  " * tingkat
    if fakta in sudah:
        print(f"{spasi}{fakta}  (sudah dijelaskan di atas)")
        return
    sudah.add(fakta)
    rid, dipakai = alasan[fakta]
    sumber = ",".join(aturan_by_id[rid]["sumber"])
    print(f"{spasi}{fakta}  <- {rid} [{sumber}] ({'; '.join(dipakai)})")
    for d in dipakai:
        if d in alasan:
            cetak_alasan(d, alasan, aturan_by_id, sudah, tingkat + 1)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    kb = muat(FILE_ATURAN)
    aturan = kb["aturan"]
    aturan_by_id = {a["id"]: a for a in aturan}

    print(kb["judul"])
    fakta_dasar = cari_fakta_dasar(aturan)
    memori_awal = tanya_user(fakta_dasar)

    print("\nFakta awal:", ", ".join(memori_awal) if memori_awal else "(tidak ada)")
    print()
    memori, alasan, log = forward_chaining(aturan, memori_awal)
    for baris in log:
        print(baris)

    # kesimpulan akhir = hasil aturan yang tidak dipakai sebagai syarat aturan lain
    dipakai_lagi = {s for a in aturan for s in a["jika"]}
    akhir = [h for h in alasan if h not in dipakai_lagi]

    print()
    if not akhir:
        print("Kesimpulan: tidak ada penyebab yang terdeteksi dari jawaban Anda.")
    else:
        print("Kesimpulan:")
        for k in akhir:
            print(f"- {k}")
        print("\nAlasan:")
        for k in akhir:
            cetak_alasan(k, alasan, aturan_by_id, set())
            print()

    print("Catatan batas keberlakuan:")
    print(kb["batas"])
    print("\nSumber:")
    for kode, ket in kb["sumber"].items():
        print(f"{kode}: {ket}")


if __name__ == "__main__":
    main()
