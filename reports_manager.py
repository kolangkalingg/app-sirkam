# reports_manager.py
import os
import json
from datetime import datetime

DATA_FILE = "laporan.json"

def ensure_datafile():
    folder = os.path.dirname(os.path.abspath(DATA_FILE))
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

def load_reports():
    ensure_datafile()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            return []

def save_reports(reports):
    ensure_datafile()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=4, ensure_ascii=False)

def generate_report_id(prefix="SRK"):
    # SRK-2025-001 style
    reports = load_reports()
    year = datetime.now().year
    same_year = [r for r in reports if r.get("ReportID","").startswith(f"{prefix}-{year}-")]
    idx = len(same_year) + 1
    return f"{prefix}-{year}-{idx:03d}"

# CRUD
def create_report(nama, nim, prodi, tanggal, jenis, detail, urgency="Rendah", is_anonymous=False):
    reports = load_reports()
    rid = generate_report_id()
    created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = {
        "ReportID": rid,
        "Nama": "Anonim" if is_anonymous else nama,
        "NIM": None if is_anonymous else nim,
        "Prodi": prodi,
        "Tanggal": tanggal if tanggal else created.split(" ")[0],
        "Jenis": jenis,
        "Detail": detail,
        "Status": "Menunggu",
        "Urgency": urgency,
        "CreatedAt": created,
        "UpdatedAt": created,
        "IsAnonymous": bool(is_anonymous)
    }
    reports.append(report)
    save_reports(reports)
    return rid

def get_all_reports(order_by=None):
    reports = load_reports()
    if order_by:
        # order_by: 'Tanggal','Nama','Status','Urgency'
        key = order_by
        reverse = False
        if key == "Tanggal":
            # sort by CreatedAt descending
            reports.sort(key=lambda r: r.get("CreatedAt",""), reverse=True)
        elif key == "Nama":
            reports.sort(key=lambda r: (r.get("Nama") or "").lower())
        elif key == "Status":
            reports.sort(key=lambda r: r.get("Status",""))
        elif key == "Urgency":
            # define urgency order High > Medium > Low
            order_map = {"Tinggi":0,"Sedang":1,"Rendah":2}
            reports.sort(key=lambda r: order_map.get(r.get("Urgency","Rendah"),2))
    return reports

def find_reports(keyword):
    kw = (keyword or "").strip().lower()
    if not kw:
        return []
    reports = load_reports()
    res = []
    for r in reports:
        if (r.get("ReportID","").lower().find(kw) != -1
            or (r.get("Nama") and kw in r.get("Nama","").lower())
            or (r.get("NIM") and kw in (r.get("NIM") or "").lower())
            or (r.get("Jenis") and kw in r.get("Jenis","").lower())
            or (r.get("Detail") and kw in r.get("Detail","").lower())):
            res.append(r)
    return res

def update_report_status(report_id, new_status, note=None):
    reports = load_reports()
    for r in reports:
        if r.get("ReportID") == report_id:
            r["Status"] = new_status
            r["UpdatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # optionally keep note
            if note:
                r.setdefault("Notes", []).append({
                    "note": note,
                    "at": r["UpdatedAt"]
                })
            save_reports(reports)
            return True
    return False

def update_report(report_id, **kwargs):
    # kwargs may include Nama, NIM, Prodi, Tanggal, Jenis, Detail, Urgency, IsAnonymous
    reports = load_reports()
    for r in reports:
        if r.get("ReportID") == report_id:
            for k,v in kwargs.items():
                if k in r:
                    r[k] = v
            r["UpdatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_reports(reports)
            return True
    return False

def delete_report(report_id):
    reports = load_reports()
    new = [r for r in reports if r.get("ReportID") != report_id]
    if len(new) < len(reports):
        save_reports(new)
        return True
    return False

def sort_reports_by(field):
    return get_all_reports(order_by=field)
