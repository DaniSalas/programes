import importlib
mods = ['pandas','dbfread','openpyxl','tkinterdnd2']
res = {}
for m in mods:
    try:
        importlib.import_module(m)
        res[m] = 'OK'
    except Exception as e:
        res[m] = str(e)

print('Dependencias comprobadas:')
for k,v in res.items():
    print(f'{k}: {v}')
