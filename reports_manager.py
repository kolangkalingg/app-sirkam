# reports_manager.py
import os
import json
from datetime import datetime
import re

BERKAS_DATA = "laporan.json"

def pastikan_berkas_data():
    folder = os.path.dirname(os.path.abspath(BERKAS_DATA))
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(BERKAS_DATA):
        with open(BERKAS_DATA, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

def muat_laporan():
    pastikan_berkas_data()
    with open(BERKAS_DATA, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            return []

def simpan_laporan(laporan):
    pastikan_berkas_data()
    with open(BERKAS_DATA, "w", encoding="utf-8") as f:
        json.dump(laporan, f, indent=4, ensure_ascii=False)

def buat_id_laporan(prefix="SRK"):
    # format: SRK-2025-001
    daftar = muat_laporan()
    tahun = datetime.now().year
    sama_tahun = [r for r in daftar if r.get("ReportID", "").startswith(f"{prefix}-{tahun}-")]
    idx = len(sama_tahun) + 1
    return f"{prefix}-{tahun}-{idx:03d}"


# Algoritma sorting dan searching kustom (sesuai permintaan):
def selection_sort(daftar, key_func=lambda x: x, reverse=False):
    """
    Selection sort sederhana yang mengembalikan salinan daftar yang diurutkan.
    - `key_func` : fungsi yang menerima elemen dan mengembalikan nilai pembanding.
    - `reverse` : jika True, urutkan menurun.
    """
    arr = daftar[:]  # salinan sehingga tidak mengubah daftar asli
    n = len(arr)
    for i in range(n):
        sel = i
        for j in range(i + 1, n):
            a = key_func(arr[j])
            b = key_func(arr[sel])
            if reverse:
                if a > b:
                    sel = j
            else:
                if a < b:
                    sel = j
        if sel != i:
            arr[i], arr[sel] = arr[sel], arr[i]
    return arr


def binary_search_exact(daftar, field, target):
    """
    Binary search untuk nilai exact pada `field`.
    Mengasumsikan `daftar` sudah diurutkan menaik berdasarkan `field`.
    Mengembalikan index jika ditemukan, atau -1 jika tidak.
    Perbandingan case-insensitive.
    """
    lo = 0
    hi = len(daftar) - 1
    t = (target or "").lower()
    while lo <= hi:
        mid = (lo + hi) // 2
        val = (daftar[mid].get(field) or "").lower()
        if val == t:
            return mid
        if val < t:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

# Operasi CRUD
def buat_laporan(nama, nim, prodi, tanggal, jenis, detail, urgency="Rendah", is_anonymous=False):
    daftar = muat_laporan()
    id_laporan = buat_id_laporan()
    dibuat_pada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    laporan = {
        "ReportID": id_laporan,
        "Nama": "Anonim" if is_anonymous else nama,
        "NIM": None if is_anonymous else nim,
        "Prodi": prodi,
        "Tanggal": tanggal if tanggal else dibuat_pada.split(" ")[0],
        "Jenis": jenis,
        "Detail": detail,
        "Status": "Menunggu",
        "Urgency": urgency,
        "CreatedAt": dibuat_pada,
        "UpdatedAt": dibuat_pada,
        "IsAnonymous": bool(is_anonymous)
    }
    daftar.append(laporan)
    simpan_laporan(daftar)
    return id_laporan

def semua_laporan(order_by=None):
    daftar = muat_laporan()
    if order_by:
        key = order_by
        if key == "Tanggal":
            # urutkan berdasarkan CreatedAt menurun (paling baru dulu)
            daftar = selection_sort(daftar, key_func=lambda r: r.get("CreatedAt", ""), reverse=True)
        elif key == "Nama":
            daftar = selection_sort(daftar, key_func=lambda r: (r.get("Nama") or "").lower())
        elif key == "Status":
            daftar = selection_sort(daftar, key_func=lambda r: r.get("Status", ""))
        elif key == "Urgency":
            urutan = {"Tinggi": 0, "Sedang": 1, "Rendah": 2}
            daftar = selection_sort(daftar, key_func=lambda r: urutan.get(r.get("Urgency", "Rendah"), 2))
    return daftar

def cari_laporan(keyword):
    kw = (keyword or "").strip()
    if not kw:
        return []
    daftar = muat_laporan()

    # Jika keyword berbentuk ReportID exact (contoh: SRK-2025-001), gunakan binary search
    if re.match(r'^[A-Za-z]+-\d{4}-\d+$', kw):
        sorted_by_id = selection_sort(daftar, key_func=lambda r: (r.get("ReportID") or "").lower())
        idx = binary_search_exact(sorted_by_id, "ReportID", kw)
        if idx != -1:
            return [sorted_by_id[idx]]

    # Jika keyword adalah angka (mungkin NIM), coba binary search pada NIM
    if kw.isdigit():
        daftar_nim = [r for r in daftar if r.get("NIM")]
        sorted_by_nim = selection_sort(daftar_nim, key_func=lambda r: (r.get("NIM") or "").lower())
        idx = binary_search_exact(sorted_by_nim, "NIM", kw)
        if idx != -1:
            return [sorted_by_nim[idx]]

    # Fallback: pencarian substring linear (sebagian besar use-case pencarian kata kunci)
    hasil = []
    lower_kw = kw.lower()
    for r in daftar:
        if (lower_kw in (r.get("ReportID", "") or "").lower()
            or (r.get("Nama") and lower_kw in r.get("Nama", "").lower())
            or (r.get("NIM") and lower_kw in (r.get("NIM") or "").lower())
            or (r.get("Jenis") and lower_kw in r.get("Jenis", "").lower())
            or (r.get("Detail") and lower_kw in r.get("Detail", "").lower())):
            hasil.append(r)
    return hasil

def perbarui_status_laporan(report_id, status_baru, catatan=None):
    daftar = muat_laporan()
    for r in daftar:
        if r.get("ReportID") == report_id:
            r["Status"] = status_baru
            r["UpdatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if catatan:
                r.setdefault("Notes", []).append({
                    "note": catatan,
                    "at": r["UpdatedAt"]
                })
            simpan_laporan(daftar)
            return True
    return False

def perbarui_laporan(report_id, **kwargs):
    # kwargs bisa berisi Nama, NIM, Prodi, Tanggal, Jenis, Detail, Urgency, IsAnonymous
    daftar = muat_laporan()
    for r in daftar:
        if r.get("ReportID") == report_id:
            for k, v in kwargs.items():
                if k in r:
                    r[k] = v
            r["UpdatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            simpan_laporan(daftar)
            return True
    return False

def hapus_laporan(report_id):
    daftar = muat_laporan()
    baru = [r for r in daftar if r.get("ReportID") != report_id]
    if len(baru) < len(daftar):
        simpan_laporan(baru)
        return True
    return False

def urutkan_laporan_berdasarkan(field):
    return semua_laporan(order_by=field)
