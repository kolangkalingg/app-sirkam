# main.py
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk as tkttk
from tkinter import simpledialog
from tkinter import filedialog
from PIL import Image, ImageTk
import winsound
import datetime

from reports_manager import (
    create_report, get_all_reports, find_reports,
    update_report_status, update_report, delete_report, sort_reports_by
)

APP_WIDTH = 960
APP_HEIGHT = 640

class SIRKAMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SIRKAM - Sistem Informasi & Report Kampus")
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.resizable(False, False)

        # gradient background like original
        grad = self._create_gradient(APP_WIDTH, APP_HEIGHT, (240,248,255), (255,255,255))
        self.bg_image = ImageTk.PhotoImage(grad)
        self.canvas = tk.Canvas(self.root, width=APP_WIDTH, height=APP_HEIGHT, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0,0,anchor="nw",image=self.bg_image)

        # sidebar
        self.sidebar = ttk.Frame(self.root, bootstyle="info")
        self.canvas.create_window(12,12,anchor="nw",window=self.sidebar,width=220,height=APP_HEIGHT-24)

        # main container
        self.container = ttk.Frame(self.root)
        self.canvas.create_window(244,12,anchor="nw",window=self.container,width=APP_WIDTH-256,height=APP_HEIGHT-24)

        self._build_sidebar()
        self.show_home()

    def _create_gradient(self,w,h,c1,c2):
        from PIL import Image
        img = Image.new("RGB",(w,h),c1)
        for y in range(h):
            t = y/(h-1)
            r = int(c1[0] + (c2[0]-c1[0])*t)
            g = int(c1[1] + (c2[1]-c1[1])*t)
            b = int(c1[2] + (c2[2]-c1[2])*t)
            for x in range(w):
                img.putpixel((x,y),(r,g,b))
        return img

    def _build_sidebar(self):
        ttk.Label(self.sidebar, text="📋 SIRKAM", font=("Helvetica",16,"bold")).grid(row=0,column=0,pady=(12,18),padx=10)
        menu_items = [
            ("🏠  Home", self.show_home),
            ("➕  Tambah Laporan", self.show_add_report),
            ("📄  Lihat Laporan", self.show_view_reports),
            ("🔍  Cari Laporan", self.show_search_reports),
            ("🔀  Urutkan Laporan", self.show_sort_reports),
            ("🚪  Keluar", self.keluar)
        ]
        for idx, (txt, cmd) in enumerate(menu_items, start=1):
            ttk.Button(self.sidebar, text=txt, command=cmd, bootstyle="secondary-outline").grid(row=idx, column=0, sticky="ew", pady=6, padx=10)

    def clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_home(self):
        self.clear_container()
        ttk.Label(self.container, text="🏠 Dashboard SIRKAM", font=("Helvetica",22,"bold"), foreground="#4A90E2").pack(pady=18)
        reports = get_all_reports()
        total = len(reports)
        status_counts = {"Menunggu":0,"Diproses":0,"Selesai":0}
        for r in reports:
            status_counts[r.get("Status","Menunggu")] = status_counts.get(r.get("Status","Menunggu"),0)+1
        frame = ttk.Frame(self.container,padding=12); frame.pack(fill="x", pady=6)
        ttk.Label(frame, text=f"Total Laporan: {total}", font=("Helvetica",14,"bold")).grid(row=0,column=0,sticky="w")
        ttk.Label(frame, text=f"Menunggu: {status_counts.get('Menunggu',0)}", font=("Helvetica",12)).grid(row=0,column=1,padx=20)
        ttk.Label(frame, text=f"Diproses: {status_counts.get('Diproses',0)}", font=("Helvetica",12)).grid(row=0,column=2,padx=20)
        ttk.Label(frame, text=f"Selesai: {status_counts.get('Selesai',0)}", font=("Helvetica",12)).grid(row=0,column=3,padx=20)
        info = ttk.Frame(self.container,padding=12); info.pack(fill="x", pady=10)
        ttk.Label(info, text="Info: Gunakan menu di kiri untuk mengelola laporan.", font=("Helvetica",12)).pack()

    def show_add_report(self):
        self.clear_container()
        ttk.Label(self.container, text="➕ Tambah Laporan", font=("Helvetica",20,"bold"), foreground="#198754").pack(pady=14)
        wrapper = ttk.Frame(self.container, padding=12, style="info.TFrame")
        wrapper.pack(padx=12, pady=8, fill="x")
        form = ttk.Frame(wrapper, padding=8)
        form.pack()

        # form fields
        labels = ["Nama Pelapor", "NIM", "Program Studi", "Tanggal (YYYY-MM-DD) [Kosong = hari ini]", "Jenis Laporan", "Detail Laporan", "Urgency"]
        for i,txt in enumerate(labels):
            ttk.Label(form, text=txt, font=("Helvetica",11,"bold")).grid(row=i, column=0, sticky="w", pady=6)
        self.nama_e = ttk.Entry(form, width=50); self.nim_e = ttk.Entry(form, width=50)
        self.prodi_e = ttk.Entry(form, width=50)
        self.tanggal_e = ttk.Entry(form, width=50)
        self.jenis_cmb = ttk.Combobox(form, values=["Barang Hilang","Keluhan Fasilitas","Kekerasan/Perundungan","Lainnya"], state="readonly", width=47)
        self.detail_txt = tk.Text(form, width=50, height=5)
        self.urgency_cmb = ttk.Combobox(form, values=["Rendah","Sedang","Tinggi"], state="readonly", width=47)

        self.nama_e.grid(row=0,column=1,padx=10)
        self.nim_e.grid(row=1,column=1,padx=10)
        self.prodi_e.grid(row=2,column=1,padx=10)
        self.tanggal_e.grid(row=3,column=1,padx=10)
        self.jenis_cmb.grid(row=4,column=1,padx=10)
        self.detail_txt.grid(row=5,column=1,padx=10)
        self.urgency_cmb.grid(row=6,column=1,padx=10)

        # anonym checkbox
        self.anon_var = tk.IntVar()
        ttk.Checkbutton(form, text="Laporkan secara anonim (sembunyikan identitas)", variable=self.anon_var).grid(row=7, column=1, sticky="w", pady=6)

        def simpan():
            nama = self.nama_e.get().strip()
            nim = self.nim_e.get().strip()
            prodi = self.prodi_e.get().strip()
            tanggal = self.tanggal_e.get().strip()
            jenis = self.jenis_cmb.get().strip()
            detail = self.detail_txt.get("1.0","end").strip()
            urgency = self.urgency_cmb.get().strip() or "Rendah"
            is_anon = bool(self.anon_var.get())
            if not jenis or not detail:
                Messagebox.show_warning("Peringatan","Jenis dan detail laporan wajib diisi.")
                return
            if not tanggal:
                tanggal = datetime.date.today().strftime("%Y-%m-%d")
            rid = create_report(nama, nim, prodi, tanggal, jenis, detail, urgency=urgency, is_anonymous=is_anon)
            Messagebox.show_info("Berhasil", f"Laporan berhasil disimpan dengan ID {rid}")
            # clear
            self.nama_e.delete(0,"end"); self.nim_e.delete(0,"end"); self.prodi_e.delete(0,"end")
            self.tanggal_e.delete(0,"end"); self.jenis_cmb.set(""); self.detail_txt.delete("1.0","end"); self.urgency_cmb.set("")

        ttk.Button(form, text="💾 Simpan Laporan", bootstyle="success-outline", command=simpan).grid(row=8, column=1, sticky="e", pady=10)

    def show_view_reports(self):
        self.clear_container()
        ttk.Label(self.container, text="📄 Lihat Laporan", font=("Helvetica",20,"bold"), foreground="#0d6efd").pack(pady=12)

        # setup table
        cols = ("ReportID","Nama","NIM","Prodi","Tanggal","Jenis","Status","Urgency")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica",11,"bold"))
        style.configure("Treeview", font=("Helvetica",10), rowheight=26)

        tbl = tkttk.Treeview(self.container, columns=cols, show="headings", height=16)
        for c in cols:
            tbl.heading(c, text=c)
            tbl.column(c, anchor="center", width=110)
        tbl.pack(fill="both", expand=True, padx=12, pady=6)

        # fill
        for r in get_all_reports():
            tbl.insert("", "end", values=(
                r.get("ReportID"), r.get("Nama"), r.get("NIM") or "", r.get("Prodi"),
                r.get("Tanggal"), r.get("Jenis"), r.get("Status"), r.get("Urgency")
            ))

        def on_view():
            sel = tbl.selection()
            if not sel:
                Messagebox.show_warning("Pilih Data", "Pilih laporan terlebih dahulu.")
                return
            item = tbl.item(sel[0])["values"]
            rid = item[0]
            # popup detail with options update/delete
            top = tk.Toplevel(self.root)
            top.title(f"Detail {rid}")
            top.geometry("520x420")
            top.resizable(False, False)
            # load full report
            reps = [x for x in get_all_reports() if x.get("ReportID")==rid]
            if not reps: 
                Messagebox.show_warning("Error","Data tidak ditemukan.")
                top.destroy()
                return
            rep = reps[0]
            ttk.Label(top, text=f"Detail Laporan {rid}", font=("Helvetica",14,"bold")).pack(pady=8)
            info_frame = ttk.Frame(top, padding=10)
            info_frame.pack(fill="both", expand=True)
            text = ""
            keys = ["Nama","NIM","Prodi","Tanggal","Jenis","Detail","Status","Urgency","CreatedAt","UpdatedAt"]
            for k in keys:
                text += f"{k}: {rep.get(k,'')}\n\n"
            txt = tk.Text(info_frame, height=12, wrap="word")
            txt.insert("1.0", text)
            txt.configure(state="disabled")
            txt.pack(fill="both", expand=True, padx=6, pady=6)

            # update status
            def do_update_status():
                choices = ["Menunggu","Diproses","Selesai"]
                new = simpledialog.askstring("Update Status","Masukkan status baru (Menunggu/Diproses/Selesai):",parent=top)
                if new and new in choices:
                    ok = update_report_status(rid, new)
                    if ok:
                        Messagebox.show_info("Sukses","Status diperbarui.")
                        top.destroy()
                        self.show_view_reports()
                else:
                    Messagebox.show_warning("Peringatan","Status tidak valid.")

            def do_update():
                # allow edit detail and urgency (simple)
                new_detail = simpledialog.askstring("Edit Detail","Masukkan detail baru:",initialvalue=rep.get("Detail",""),parent=top)
                new_urg = simpledialog.askstring("Edit Urgency","Masukkan urgency (Rendah/Sedang/Tinggi):",initialvalue=rep.get("Urgency","Rendah"),parent=top)
                if new_detail is not None and new_urg in ["Rendah","Sedang","Tinggi"]:
                    update_report(rid, Detail=new_detail, Urgency=new_urg)
                    Messagebox.show_info("Sukses","Laporan diperbarui.")
                    top.destroy()
                    self.show_view_reports()
                else:
                    Messagebox.show_warning("Peringatan","Data tidak valid atau dibatalkan.")

            def do_delete():
                confirm = Messagebox.ask_yesno("Konfirmasi","Yakin ingin menghapus laporan ini?")
                if confirm:
                    if delete_report(rid):
                        Messagebox.show_info("Sukses","Laporan dihapus.")
                        top.destroy()
                        self.show_view_reports()
                    else:
                        Messagebox.show_warning("Gagal","Gagal menghapus laporan.")

            btnfrm = ttk.Frame(top)
            btnfrm.pack(pady=6)
            ttk.Button(btnfrm, text="🔁 Update Status", bootstyle="warning-outline", command=do_update_status).grid(row=0,column=0,padx=6)
            ttk.Button(btnfrm, text="✏️ Edit Laporan", bootstyle="primary-outline", command=do_update).grid(row=0,column=1,padx=6)
            ttk.Button(btnfrm, text="🗑 Hapus Laporan", bootstyle="danger-outline", command=do_delete).grid(row=0,column=2,padx=6)

        ttk.Button(self.container, text="🔍 Lihat Detail / Kelola", bootstyle="primary-outline", command=on_view).pack(pady=8)

    def show_search_reports(self):
        self.clear_container()
        ttk.Label(self.container, text="🔍 Cari Laporan", font=("Helvetica",16)).pack(pady=8)
        frm = ttk.Frame(self.container); frm.pack(pady=6, padx=10, fill="x")
        kw = tkttk.Entry(frm, width=40); kw.pack(side="left", padx=(0,8))
        ttk.Button(frm, text="Cari", bootstyle=PRIMARY, command=lambda: self._do_search(kw.get().strip(), tbl)).pack(side="left")
        cols = ("ReportID","Nama","NIM","Prodi","Tanggal","Jenis","Status","Urgency")
        tbl = tkttk.Treeview(self.container, columns=cols, show="headings", height=16)
        for c in cols:
            tbl.heading(c, text=c); tbl.column(c, width=110, anchor="center")
        tbl.pack(fill="both", expand=True, padx=10, pady=6)

    def _do_search(self, keyword, table_widget):
        # clear
        table_widget.delete(*table_widget.get_children())
        if not keyword:
            Messagebox.show_info("Info","Masukkan kata kunci pencarian.")
            return
        res = find_reports(keyword)
        if not res:
            Messagebox.show_info("Hasil","Tidak ditemukan.")
            return
        for r in res:
            table_widget.insert("", "end", values=(
                r.get("ReportID"), r.get("Nama"), r.get("NIM") or "", r.get("Prodi"),
                r.get("Tanggal"), r.get("Jenis"), r.get("Status"), r.get("Urgency")
            ))

    def show_sort_reports(self):
        self.clear_container()
        ttk.Label(self.container, text="🔀 Urutkan Laporan", font=("Helvetica",16)).pack(pady=8)
        frm = ttk.Frame(self.container); frm.pack(pady=6, padx=10, fill="x")
        ttk.Label(frm, text="Pilih metode urut:").pack(side="left", padx=(0,8))
        cmb = ttk.Combobox(frm, values=["Tanggal","Nama","Status","Urgency"], state="readonly"); cmb.pack(side="left", padx=6)
        tblcols = ("ReportID","Nama","NIM","Prodi","Tanggal","Jenis","Status","Urgency")
        tbl = tkttk.Treeview(self.container, columns=tblcols, show="headings", height=16)
        for c in tblcols:
            tbl.heading(c, text=c); tbl.column(c, width=110, anchor="center")
        tbl.pack(fill="both", expand=True, padx=10, pady=6)
        def do_sort():
            method = cmb.get()
            if not method:
                Messagebox.show_warning("Peringatan","Pilih metode urut terlebih dahulu.")
                return
            rows = sort_reports_by(method)
            tbl.delete(*tbl.get_children())
            for r in rows:
                tbl.insert("", "end", values=(
                    r.get("ReportID"), r.get("Nama"), r.get("NIM") or "", r.get("Prodi"),
                    r.get("Tanggal"), r.get("Jenis"), r.get("Status"), r.get("Urgency")
                ))
        ttk.Button(frm, text="Urutkan", bootstyle=PRIMARY, command=do_sort).pack(side="left", padx=6)

    def keluar(self):
        if Messagebox.show_question("Konfirmasi","Yakin ingin keluar?",buttons=["yes","no"])=="yes":
            self.root.destroy()

if __name__ == "__main__":
    root = ttk.Window(themename="minty")
    app = SIRKAMApp(root)
    root.mainloop()
