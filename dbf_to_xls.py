# Control de error de libreria
try:
    import xlwt
except ImportError:
    import sys
    try:
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror('Falta xlwt', 'El paquete xlwt no está instalado. Instálalo con "pip install xlwt".')
        root.destroy()
    except Exception:
        print('Falta xlwt. El paquete xlwt no está instalado. Instálalo con "pip install xlwt".')
    sys.exit(1)


import os
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from dbfread import DBF
import pandas as pd



def convert_dbf_to_xls(dbf_path):
    table = DBF(dbf_path, load=True)
    df = pd.DataFrame(iter(table))
    xls_path = os.path.splitext(dbf_path)[0] + '.xls'
    # Guardar como .xls usando xlwt
    df.to_excel(xls_path, index=False, engine='xlwt')
    return xls_path

def drop(event):
    files = root.tk.splitlist(event.data)
    for file in files:
        if file.lower().endswith('.dbf'):
            try:
                xls = convert_dbf_to_xls(file)
                status.set(f'Convertido: {os.path.basename(xls)}')
            except Exception as e:
                status.set(f'Error: {e}')
        else:
            status.set('Solo archivos .dbf')
import traceback

print("Iniciando script dbf_to_xls.py...")

try:
    print("Inicializando ventana...")
    root = TkinterDnD.Tk()
    root.title('Arrastra archivos DBF aquí')
    root.geometry('400x200')

    label = tk.Label(root, text='Arrastra aquí tus archivos .dbf', font=('Arial', 14))
    label.pack(pady=40)

    status = tk.StringVar()
    status_label = tk.Label(root, textvariable=status, fg='blue')
    status_label.pack(pady=10)

    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', drop)

    print("Mostrando ventana...")
    root.mainloop()
    print("Ventana cerrada.")
except Exception as e:
    print("Error al iniciar la ventana:", e)
    traceback.print_exc()
    try:
        import tkinter.messagebox as messagebox
        messagebox.showerror('Error', f'Error al iniciar la ventana:\n{e}')
    except Exception:
        pass