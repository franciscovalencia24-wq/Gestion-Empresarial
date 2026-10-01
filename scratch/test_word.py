import win32com.client
import os
import time

filepath = r"C:\Users\franc\OneDrive\Documentos\MALENTIN KARIME\BANCO CREDITO\FER LORCA en ROSITA (Rosita)\ANA LUISA TODO\CANCELACION\ULISES ROBLES A INMB. COLOMBRES (CANCELACION PARCIAL).doc"

word = win32com.client.DispatchEx("Word.Application")
word.Visible = True  # We want to see the error dialog if any!
word.DisplayAlerts = -1 # wdAlertsAll

try:
    print(f"Abriendo {filepath}...")
    doc = word.Documents.Open(filepath, ReadOnly=True)
    print("Abierto correctamente!")
    time.sleep(2)
    doc.Close(False)
except Exception as e:
    print(f"Error: {e}")
finally:
    word.Quit()
