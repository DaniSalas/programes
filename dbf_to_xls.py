import os
import tkinter as tk
from tkinter import filedialog, messagebox
import traceback

# Imports opcionales/externos
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False

try:
    from dbfread import DBF
except Exception:
    DBF = None

try:
    import pandas as pd
except Exception:
    pd = None

# Detectar availability de engines
try:
    import xlwt
    XLWT_AVAILABLE = True
except Exception:
    XLWT_AVAILABLE = False

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except Exception:
    OPENPYXL_AVAILABLE = False


def convert_dbf_to_xls(dbf_path):
    if DBF is None or pd is None:
        raise RuntimeError('Faltan dependencias: instale dbfread y pandas (y xlwt/openpyxl según el formato)')

    # Asegurar ruta sin llaves que a veces añade el drag&drop
    dbf_path = dbf_path.strip('{}')

    table = DBF(dbf_path, load=True)
    df = pd.DataFrame(list(table))

    # Preferir .xls si xlwt está disponible, sino .xlsx
    if XLWT_AVAILABLE:
        out_path = os.path.splitext(dbf_path)[0] + '.xls'
        df.to_excel(out_path, index=False, engine='xlwt')
        return out_path
    elif OPENPYXL_AVAILABLE:
        out_path = os.path.splitext(dbf_path)[0] + '.xlsx'
        df.to_excel(out_path, index=False, engine='openpyxl')
        return out_path
    else:
        # Intentar dejar que pandas escoja el engine (fallará si no hay ninguno)
        out_path = os.path.splitext(dbf_path)[0] + '.xlsx'
        df.to_excel(out_path, index=False)
        return out_path


def handle_files(paths, status_var):
    for file in paths:
        file = file.strip('{}')
        if file.lower().endswith('.dbf') and os.path.isfile(file):
            try:
                out = convert_dbf_to_xls(file)
                status_var.set(f'Convertido: {os.path.basename(out)}')
            except Exception as e:
                status_var.set(f'Error: {e}')
                print(f'Error convirtiendo {file}:', e)
                traceback.print_exc()
        else:
            status_var.set('Solo archivos .dbf existentes')


def create_gui():
    print('Inicializando ventana...')
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    root.title('Arrastra archivos DBF aquí')
    root.geometry('580x360')

    label = tk.Label(root, text='Arrastra aquí tus archivos .dbf o usa "Agregar archivos"', font=('Arial', 12))
    label.pack(pady=12)

    status = tk.StringVar()
    status_label = tk.Label(root, textvariable=status, fg='blue')
    status_label.pack(pady=6)

    # Listbox para mostrar ficheros (opcional)
    listbox = tk.Listbox(root, height=10)
    listbox.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

    def drop(event):
        try:
            files = root.tk.splitlist(event.data)
        except Exception:
            files = [event.data]
        for f in files:
            listbox.insert(tk.END, f)
        handle_files(files, status)

    def add_files():
        files = filedialog.askopenfilenames(title='Seleccionar archivos DBF', filetypes=[('DBF', '*.dbf'), ('All', '*.*')])
        if files:
            for f in files:
                listbox.insert(tk.END, f)
            handle_files(files, status)

    btn_frame = tk.Frame(root)
    btn_frame.pack(fill=tk.X, padx=8, pady=6)

    add_btn = tk.Button(btn_frame, text='Agregar archivos', command=add_files)
    add_btn.pack(side=tk.LEFT)

    clear_btn = tk.Button(btn_frame, text='Limpiar lista', command=lambda: listbox.delete(0, tk.END))
    clear_btn.pack(side=tk.LEFT, padx=6)

    if DND_AVAILABLE:
        try:
            root.drop_target_register(DND_FILES)
            root.dnd_bind('<<Drop>>', drop)
        except Exception as e:
            print('Warning: fallo al registrar DnD:', e)

    print('Mostrando ventana...')
    root.mainloop()
    print('Ventana cerrada.')


if __name__ == '__main__':
    print('Iniciando script dbf_to_xls.py...')
    try:
        create_gui()
    except Exception as e:
        print('Error al iniciar la ventana:', e)
        traceback.print_exc()
        try:
            messagebox.showerror('Error', f'Error al iniciar la ventana:\n{e}')
        except Exception:
            pass