# DBF → Excel GUI

Pequeña herramienta para Windows que permite arrastrar y soltar múltiples archivos `.dbf` (dBase IV)
y generar un archivo `.xlsx` por cada uno en la misma carpeta de origen.

Requisitos
- Python 3.8+
- Paquetes (recomendado instalar desde `requirements.txt`):
  - pandas
  - dbfread
  - openpyxl
  - tkinterdnd2 (opcional, mejora soporte drag&drop en Windows)

Instalación (PowerShell):

```powershell
python -m pip install -r requirements.txt
```

Uso
- Ejecutar el script `dbf_to_excel_gui.py` desde el directorio del proyecto:

```powershell
python dbf_to_excel_gui.py
```

- Arrastrar y soltar archivos `.dbf` sobre la lista (si `tkinterdnd2` está instalado) o usar "Agregar archivos".
- Pulsar "Convertir a Excel". Se generará un `.xlsx` por cada `.dbf` en la misma carpeta del `.dbf`.

Notas
- Si encuentras problemas con codificaciones, el script intenta decodificar columnas de bytes usando `latin1`.
- `tkinterdnd2` puede instalarse con `pip` pero en Windows a veces necesita paquetes binarios; si no funciona, usa el diálogo de selección de archivos.
