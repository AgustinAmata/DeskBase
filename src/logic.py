import customtkinter as ctk
from customtkinter import CTk
import pandas as pd
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

def change_appearance(self, choice):
    ctk.set_appearance_mode(choice)
    if choice == "light":
        self.m3_appearance_menu.entryconfig("Oscuro", state="normal")
        self.m3_appearance_menu.entryconfig("Claro", state="disabled")
    else:
        self.m3_appearance_menu.entryconfig("Claro", state="normal")
        self.m3_appearance_menu.entryconfig("Oscuro", state="disabled")

def convert_to_excel(self):
        try:
            # Preguntar dónde guardar el archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                title="Guardar inventario como"
            )
            
            if not filename:  # Si el usuario cancela
                return
                
            # Usamos pandas para crear el dataframe directamente desde la base de datos
            query = "SELECT * FROM equipos"
            df = pd.read_sql_query(query, self.db.cnx)
            
            # Cambiar nombres de columnas para mejor presentación
            columnas = {
                'id': 'ID', 'nombre': 'Tipo', 'marca': 'Marca', 'modelo': 'Modelo',
                'serial': 'Serial', 'fecha_adquisicion': 'Fecha Adquisición', 'estado': 'Estado',
                'ubicacion': 'Ubicación', 'sistema_operativo': 'Sistema Operativo',
                'modelo_placa_base': 'Placa Base', 'tarjeta_grafica': 'Tarjeta Gráfica',
                'tipo_almacenamiento': 'Tipo Almacenamiento', 'capacidad_almacenamiento': 'Capacidad',
                'memoria_ram': 'Tipo RAM', 'capacidad_ram': 'Capacidad RAM'
            }
            df = df.rename(columns=columnas)
            
            # Exportar a Excel
            df.to_excel(filename, index=False)
            
            # Verificar si se creó el archivo
            if Path(filename).exists():
                messagebox.showinfo("Éxito", f"Inventario exportado exitosamente a {filename}")
            else:
                messagebox.showerror("Error", "No se pudo guardar el archivo Excel.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

def info_clear(entries):
    for i, entry in enumerate(entries):
        if type(entry) == ctk.CTkOptionMenu:
            entry.set(entry._values[0])
        elif type(entry) == ctk.CTkEntry:
            entry.delete(0, tk.END)

#From https://github.com/TomSchimansky/CustomTkinter/discussions/1820
def CenterWindowToDisplay(Screen: CTk, width: int, height: int, scale_factor: float = 1.0):
    """Centers the window to the main display/monitor"""
    screen_width = Screen.winfo_screenwidth()
    screen_height = Screen.winfo_screenheight()
    x = int(((screen_width//2) - (width//2)) * scale_factor)
    y = int(((screen_height//2) - (height//2)) * scale_factor)
    return f"{width}x{height}+{x}+{y}"