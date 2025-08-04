import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PyPDF2 import PdfMerger

def get_pdfs_in_folder(folder):
    pdfs = []
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            full_path = os.path.join(folder, file)
            creation_time = os.path.getctime(full_path)
            pdfs.append((file, creation_time))
    return sorted(pdfs, key=lambda x: x[1])

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)
        refresh_pdf_list()

def refresh_pdf_list():
    pdf_listbox.delete(0, tk.END)
    folder = folder_var.get()
    if folder:
        pdfs = get_pdfs_in_folder(folder)
        for pdf, _ in pdfs:
            pdf_listbox.insert(tk.END, pdf)

def move_up():
    sel = pdf_listbox.curselection()
    if not sel or sel[0] == 0:
        return
    i = sel[0]
    text = pdf_listbox.get(i)
    pdf_listbox.delete(i)
    pdf_listbox.insert(i - 1, text)
    pdf_listbox.selection_set(i - 1)

def move_down():
    sel = pdf_listbox.curselection()
    if not sel or sel[0] == pdf_listbox.size() - 1:
        return
    i = sel[0]
    text = pdf_listbox.get(i)
    pdf_listbox.delete(i)
    pdf_listbox.insert(i + 1, text)
    pdf_listbox.selection_set(i + 1)

def select_export_folder():
    folder = filedialog.askdirectory()
    if folder:
        export_var.set(folder)

def is_valid_filename(name):
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    reserved_names = {'CON', 'PRN', 'AUX', 'NUL'} | {f'COM{i}' for i in range(1, 10)} | {f'LPT{i}' for i in range(1, 10)}
    base_name = os.path.splitext(name)[0].upper()
    return not re.search(invalid_chars, name) and base_name not in reserved_names and name.strip() != ""

def merge_pdfs():
    folder = folder_var.get()
    export_folder = export_var.get()
    name = filename_entry.get().strip()

    if not folder or not name or not export_folder:
        messagebox.showerror("Error", "Please fill all fields.")
        return

    if not is_valid_filename(name):
        messagebox.showerror("Invalid name", "The filename is invalid or reserved.\nPlease avoid using characters like / \\ : * ? \" < > | and reserved names like AUX, COM1, NUL.")
        return

    if not name.lower().endswith(".pdf"):
        name += ".pdf"

    full_output_path = os.path.join(export_folder, name)

    merger = PdfMerger()
    for i in range(pdf_listbox.size()):
        file = pdf_listbox.get(i)
        full_path = os.path.join(folder, file)
        merger.append(full_path)

    try:
        merger.write(full_output_path)
        merger.close()
        messagebox.showinfo("Success", f"PDF merged and saved to:\n{full_output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save PDF:\n{e}")

app = ttk.Window(themename="cosmo")
app.title("Merge PDF Files")
app.geometry("600x500")

folder_var = tk.StringVar()
export_var = tk.StringVar()

ttk.Label(app, text="PDF Source Folder:", font=('Segoe UI', 10, 'bold')).pack(anchor=W, padx=10, pady=(10, 0))
folder_frame = ttk.Frame(app)
folder_frame.pack(fill=X, padx=10)
ttk.Entry(folder_frame, textvariable=folder_var, state='readonly').pack(side=LEFT, expand=True, fill=X)
ttk.Button(folder_frame, text="Select Folder", command=select_folder).pack(side=LEFT, padx=5)

ttk.Label(app, text="PDF Order:", font=('Segoe UI', 10, 'bold')).pack(anchor=W, padx=10, pady=(10, 0))
pdf_listbox = tk.Listbox(app, selectmode=SINGLE, height=10)
pdf_listbox.pack(fill=BOTH, expand=True, padx=10)

order_frame = ttk.Frame(app)
order_frame.pack(pady=5)
ttk.Button(order_frame, text="↑", width=3, command=move_up).pack(side=LEFT, padx=2)
ttk.Button(order_frame, text="↓", width=3, command=move_down).pack(side=LEFT, padx=2)

ttk.Label(app, text="New PDF Name:", font=('Segoe UI', 10, 'bold')).pack(anchor=W, padx=10, pady=(10, 0))
filename_entry = ttk.Entry(app)
filename_entry.pack(fill=X, padx=10)

ttk.Label(app, text="Export Folder:", font=('Segoe UI', 10, 'bold')).pack(anchor=W, padx=10, pady=(10, 0))
export_frame = ttk.Frame(app)
export_frame.pack(fill=X, padx=10)
ttk.Entry(export_frame, textvariable=export_var, state='readonly').pack(side=LEFT, expand=True, fill=X)
ttk.Button(export_frame, text="Select Export Folder", command=select_export_folder).pack(side=LEFT, padx=5)

ttk.Button(app, text="Merge PDFs", bootstyle=SUCCESS, command=merge_pdfs).pack(pady=20)

app.mainloop()
