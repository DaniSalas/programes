import tkinter as tk
from tkinter import messagebox

# Funciones de ejemplo
def accion_1a():
    messagebox.showinfo("Acción", "Has ejecutado Acción 1A")

def accion_1b():
    messagebox.showinfo("Acción", "Has ejecutado Acción 1B")

def accion_2a():
    messagebox.showinfo("Acción", "Has ejecutado Acción 2A")

def accion_2b():
    messagebox.showinfo("Acción", "Has ejecutado Acción 2B")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Menú anidado")
ventana.geometry("500x300")

# Crear barra de menú
barra_menu = tk.Menu(ventana)

# Menú "Archivo"
menu_archivo = tk.Menu(barra_menu, tearoff=0)

# Submenú dentro de "Archivo"
submenu_1 = tk.Menu(menu_archivo, tearoff=0)
submenu_1.add_command(label="Acción 1A", command=accion_1a)
submenu_1.add_command(label="Acción 1B", command=accion_1b)
menu_archivo.add_cascade(label="📁 Submenú 1", menu=submenu_1)

# Otro submenú dentro de "Archivo"
submenu_2 = tk.Menu(menu_archivo, tearoff=0)
submenu_2.add_command(label="Acción 2A", command=accion_2a)
submenu_2.add_command(label="Acción 2B", command=accion_2b)
menu_archivo.add_cascade(label="Submenú 2 🛠️", menu=submenu_2)

# Añadir "Archivo" a la barra principal
barra_menu.add_cascade(label="Menú Principal 🔽", menu=menu_archivo)

# Asignar barra de menú a la ventana
ventana.config(menu=barra_menu)

ventana.mainloop()