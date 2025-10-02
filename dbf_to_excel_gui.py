#!/usr/bin/env python3
"""
Pequeña aplicación GUI para arrastrar y soltar múltiples archivos .dbf (dBase IV) y crear
un fichero .xlsx por cada uno en la misma carpeta de origen.

Dependencias: pandas, dbfread, openpyxl. Para soporte de drag&drop en Windows se recomienda
instalar `tkinterdnd2` (opcional). Si no está disponible, la app ofrecerá un botón para
seleccionar archivos.
"""
import os
import sys
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from dbfread import DBF
except Exception as e:
    DBF = None

try:
    import pandas as pd
except Exception:
    pd = None

try:
    # tkinterdnd2 proporciona soporte para arrastrar/soltar en Windows
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False


def convert_dbf_to_excel(dbf_path, excel_path=None):
    """Convierte un fichero .dbf a .xlsx. Devuelve la ruta del fichero generado.

    - dbf_path: ruta al .dbf
    - excel_path: ruta de salida (si None, se crea junto al origen con extensión .xlsx)
    """
    if DBF is None or pd is None:
        raise RuntimeError("Faltan dependencias: instale dbfread y pandas (y openpyxl para xlsx)")

    if excel_path is None:
        base, _ = os.path.splitext(dbf_path)
        excel_path = base + ".xlsx"

    # dbfread maneja múltiples dialectos; forzamos ignorecase para nombres de campos si hace falta
    try:
        table = DBF(dbf_path, load=True, ignorechardecode=False)
    except TypeError:
        # versiones antiguas de dbfread no aceptan ignorechardecode
        table = DBF(dbf_path, load=True)

    records = list(table)

    # Si no hay registros, crear un DataFrame vacío con columnas definidas
    if records:
        df = pd.DataFrame(records)
    else:
        # obtener nombres de campos desde la meta del DBF
        try:
            cols = [f.name for f in table.field_names or []]
        except Exception:
            cols = []
        df = pd.DataFrame(columns=cols)

    # Decodificar columnas que vengan como bytes (a veces ocurre con ciertos codings)
    for col in df.columns:
        if df[col].dtype == object:
            if df[col].apply(lambda v: isinstance(v, (bytes, bytearray))).any():
                try:
                    df[col] = df[col].apply(lambda v: v.decode('latin1') if isinstance(v, (bytes, bytearray)) else v)
                except Exception:
                    df[col] = df[col].apply(lambda v: v.decode('latin1', errors='ignore') if isinstance(v, (bytes, bytearray)) else v)

    # Guardar a excel
    try:
        df.to_excel(excel_path, index=False, engine='openpyxl')
    except Exception:
        # intento sin engine explícito
        df.to_excel(excel_path, index=False)

    return excel_path


class DBFConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title('DBF → Excel (arrastrar y soltar)')
        self.root.geometry('700x420')

        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        info = ttk.Label(frm, text='Arrastra aquí archivos .dbf o usa "Agregar archivos"')
        info.pack(anchor=tk.W)

        self.listbox = tk.Listbox(frm, selectmode=tk.EXTENDED, height=14)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=8)

        # Configurar drop (si está disponible)
        if DND_AVAILABLE:
            try:
                # si usamos TkinterDnD, la raíz ya es una TkinterDnD.Tk
                self.listbox.drop_target_register(DND_FILES)
                self.listbox.dnd_bind('<<Drop>>', self._on_drop)
            except Exception:
                # fallback: no crash
                pass
        else:
            note = ttk.Label(frm, text='(Drag&Drop no disponible: instale `tkinterdnd2`. Puedes usar "Agregar archivos")', foreground='gray')
            note.pack(anchor=tk.W)

        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X, pady=6)

        add_btn = ttk.Button(btns, text='Agregar archivos', command=self._add_files)
        add_btn.pack(side=tk.LEFT)

        remove_btn = ttk.Button(btns, text='Quitar seleccionados', command=self._remove_selected)
        remove_btn.pack(side=tk.LEFT, padx=6)

        conv_btn = ttk.Button(btns, text='Convertir a Excel', command=self._convert_all)
        conv_btn.pack(side=tk.RIGHT)

        clear_btn = ttk.Button(btns, text='Limpiar lista', command=lambda: self.listbox.delete(0, tk.END))
        clear_btn.pack(side=tk.RIGHT, padx=6)

        self.status = ttk.Label(frm, text='Listo')
        self.status.pack(anchor=tk.W, pady=(6, 0))

    def _on_drop(self, event):
        # event.data contiene una lista de rutas; en windows vienen entre { } si contienen espacios
        data = event.data
        paths = self._parse_drop_data(data)
        self._add_paths(paths)

    def _parse_drop_data(self, data):
        # data puede ser una cadena con rutas separadas por espacios, y rutas con espacios encerradas en {}.
        parts = []
        cur = ''
        in_brace = False
        for ch in data:
            if ch == '{}':
                # no ocurre normalmente, mantener guardia
                pass
            if ch == '{':
                in_brace = True
                cur = ''
            elif ch == '}':
                in_brace = False
                parts.append(cur)
                cur = ''
            elif ch == ' ' and not in_brace:
                if cur:
                    parts.append(cur)
                    cur = ''
            else:
                cur += ch
        if cur:
            parts.append(cur)
        # limpiar comillas
        parts = [p.strip('"') for p in parts if p.strip()]
        return parts

    def _add_files(self):
        files = filedialog.askopenfilenames(title='Seleccionar archivos DBF', filetypes=[('DBF files', '*.dbf'), ('All files', '*.*')])
        self._add_paths(list(files))

    def _add_paths(self, paths):
        for p in paths:
            if os.path.isfile(p) and p.lower().endswith('.dbf'):
                if p not in self.listbox.get(0, tk.END):
                    self.listbox.insert(tk.END, p)
            else:
                # permitir carpetas conteniendo dbf: añadir todos los .dbf dentro
                if os.path.isdir(p):
                    for root, _, files in os.walk(p):
                        for f in files:
                            if f.lower().endswith('.dbf'):
                                full = os.path.join(root, f)
                                if full not in self.listbox.get(0, tk.END):
                                    self.listbox.insert(tk.END, full)

    def _remove_selected(self):
        sel = list(self.listbox.curselection())
        for i in reversed(sel):
            self.listbox.delete(i)

    def _convert_all(self):
        items = list(self.listbox.get(0, tk.END))
        if not items:
            messagebox.showinfo('Info', 'No hay archivos en la lista')
            return

        failed = []
        converted = []
        total = len(items)
        for idx, path in enumerate(items, 1):
            self.status.config(text=f'Convirtiendo {idx}/{total}: {os.path.basename(path)}')
            self.root.update_idletasks()
            try:
                out = convert_dbf_to_excel(path)
                converted.append(out)
            except Exception as e:
                failed.append((path, str(e)))

        msg = f'Convertidos: {len(converted)}\n'
        if failed:
            msg += f'Fallos: {len(failed)} (ver detalles en consola)'
            print('Errores al convertir:')
            for p, err in failed:
                print(p)
                traceback.print_exc()
        messagebox.showinfo('Resultado', msg)
        self.status.config(text='Listo')


def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app = DBFConverterApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
