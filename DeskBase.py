import customtkinter as ctk
import mysql.connector
import pandas as pd
from pathlib import Path
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from mysql.connector import errorcode

ctk.set_appearance_mode("light")

LABELS = [
    "Tipo*", "Marca*", "Modelo*", "Serial*", 
    "Fecha de Adquisición", "Estado",
    "Ubicación", "Sistema Operativo", "Modelo Placa Base", "Tarjeta Gráfica",
    "Tipo de Almacenamiento", "Capacidad de Almacenamiento", "Memoria RAM", "Capacidad de RAM"
]

TABLE_LABELS = ["nombre", "marca", "modelo", "serial", "fecha_adquisicion", "estado",
                "ubicacion", "sistema_operativo", "modelo_placa_base", "tarjeta_grafica",
                "tipo_almacenamiento", "capacidad_almacenamiento", "memoria_ram", "capacidad_ram"]

LABEL_CONVERSION = {LABELS[i]:TABLE_LABELS[i] for i in range(14)}

TREE_TAGS = {"Operativo": "operativo", "En reparación": "reparacion",
             "En reparacion": "reparacion", "Baja": "baja"}

MARCAS = ["HP", "Dell", "Lenovo", "Asus", "Acer", "Apple", "MSI", "Otro"]
SISTEMAS_OPERATIVOS = ["Windows", "Linux", "MacOS", "ChromeOS", "Otro"]
TIPOS_ALMACENAMIENTO = ["HDD", "SSD", "M2", "NVMe", "Otro"]
TIPOS_RAM = ["DDR", "DDR2", "DDR3", "DDR4", "DDR5", "Otro"]
ESTADOS = ["Operativo", "En reparación", "En mantenimiento", "Baja", "Reserva"]
RULETA = {"Marca*": MARCAS, "Sistema Operativo": SISTEMAS_OPERATIVOS, "Tipo de almacenamiento": TIPOS_ALMACENAMIENTO,
          "Memoria RAM": TIPOS_RAM, "Estado": ESTADOS}

TABLE_CREATION = f'''CREATE TABLE equipos (
                    `id` INTEGER AUTO_INCREMENT,
                    `nombre` VARCHAR(255),
                    `marca` VARCHAR(255),
                    `modelo` VARCHAR(255),
                    `serial` VARCHAR(255) UNIQUE,
                    `fecha_adquisicion` VARCHAR(255),
                    `estado` VARCHAR(255),
                    `ubicacion` VARCHAR(255),
                    `sistema_operativo` VARCHAR(255),
                    `modelo_placa_base` VARCHAR(255),
                    `tarjeta_grafica` VARCHAR(255),
                    `tipo_almacenamiento` VARCHAR(255),
                    `capacidad_almacenamiento` VARCHAR(255),
                    `memoria_ram` VARCHAR(255),
                    `capacidad_ram` VARCHAR(255),
                    PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB'''

ADD_ENTRY = '''INSERT INTO `equipos`
               (`nombre`, `marca`, `modelo`, `serial`,
               `fecha_adquisicion`, `estado`, `ubicacion`,
               `sistema_operativo`, `modelo_placa_base`,
               `tarjeta_grafica`, `tipo_almacenamiento`,
               `capacidad_almacenamiento`, `memoria_ram`,
               `capacidad_ram`)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

UPDATE_ENTRY = '''INSERT INTO `equipos`
    (`nombre`, `marca`, `modelo`, `serial`,
     `fecha_adquisicion`, `estado`, `ubicacion`,
     `sistema_operativo`, `modelo_placa_base`,
     `tarjeta_grafica`, `tipo_almacenamiento`,
     `capacidad_almacenamiento`, `memoria_ram`,
     `capacidad_ram`)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        nombre=VALUES(nombre),
        marca=VALUES(marca),
        modelo=VALUES(modelo),
        fecha_adquisicion=VALUES(fecha_adquisicion),
        estado=VALUES(estado),
        ubicacion=VALUES(ubicacion),
        sistema_operativo=VALUES(sistema_operativo),
        modelo_placa_base=VALUES(modelo_placa_base),
        tarjeta_grafica=VALUES(tarjeta_grafica),
        tipo_almacenamiento=VALUES(tipo_almacenamiento),
        capacidad_almacenamiento=VALUES(capacidad_almacenamiento),
        memoria_ram=VALUES(memoria_ram),
        capacidad_ram=VALUES(capacidad_ram)
'''


def push_query(cnx_container, connection, cursor, query, params=None, fetch=False):
    for n_try in range(5):
        try:
            if connection is None:
                cnx_container.connect_database()
            
            cursor.execute(query, params)
            
            if fetch:
                c_fetch = list(cursor.fetchall())
                connection.commit()
                return c_fetch
            else:
                c_row = cursor.rowcount
                connection.commit()
                return c_row
            
        except mysql.connector.Error as err:
            if "database is locked" in str(err):
                time.sleep(0.5)
                if connection:
                    try:
                        connection.close()
                    except:
                        pass
                connection = None
            else:
                raise err
            
        except Exception as err:
            raise err
    
    raise Exception("No se pudo acceder a la base de datos después de múltiples intentos")

def info_clear(entries):
    for entry in entries:
        if type(entry) == ctk.CTkComboBox:
            entry.set(entry._values[0])
        elif type(entry) == ctk.CTkEntry:
            entry.delete(0, tk.END)

class MenuBar(tk.Menu):
    def __init__(self, master):
        tk.Menu.__init__(self, master, tearoff=0)
        self.master = master
        self.m1 = tk.Menu(self, tearoff=0)
        self.m1.add_command(label="Conectar a base de datos", command=self.create_dbwindow)
        self.m1.add_command(label="Desconectar base de datos", command=self.close_database)
        self.m1.add_separator()
        self.m1.add_command(label="Exportar a Excel", command=self.convert_to_excel)
        master.config(menu=self)
        self.add_cascade(label="Archivo", menu=self.m1)

        self.m2 = tk.Menu(self, tearoff=0)
        self.m2.add_command(label="Limpiar campos", command=lambda: info_clear(self.master.maintab.devices_obj.info.entries))
        self.m2.add_separator()
        self.m2.add_command(label="Eliminar equipo", command=lambda: self.master.maintab.devices_obj.db_deleterow())
        self.m2.add_command(label="Cargar equipo", command=lambda: self.master.maintab.devices_obj.db_loadrowinfo())
        self.m2.add_separator()
        self.m2.add_command(label="Mostrar equipos", command=lambda: self.master.maintab.devices_obj.db_showentries())
        self.add_cascade(label="Editar", menu=self.m2)

        self.m3 = tk.Menu(self, tearoff=0)
        self.m3_appearance_menu = tk.Menu(self.m3, tearoff=0)
        self.m3.add_cascade(menu=self.m3_appearance_menu, label="Apariencia")
        self.m3_appearance_menu.add_command(label="Claro", command=lambda: self.change_appearance("light"), state="disabled")
        self.m3_appearance_menu.add_command(label="Oscuro", command=lambda: self.change_appearance("dark"))
        self.add_cascade(label="Ver", menu=self.m3)

        self.m4 = tk.Menu(self, tearoff=0)
        self.m4.add_command(label="Acerca de", command=self.create_about)
        self.add_cascade(label="Ayuda", menu=self.m4)

        self.dbwin = None
        self.about = None

    def create_dbwindow(self):
        if self.dbwin is None or not self.dbwin.winfo_exists():
            self.dbwin = DBWindow(self.master)
        else:
            self.dbwin.focus()

    def create_about(self):
        if self.about is None or not self.about.winfo_exists():
            self.about = About(self.master)
        else:
            self.about.focus()

    def close_database(self):
        if self.master.cnx:
            self.master.cnx.close()
            messagebox.showinfo("", "Se ha cortado la conexión con la base de datos")
        else:
            messagebox.showinfo("", "No hay una base de datos conectada")

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
            df = pd.read_sql_query(query, self.master.cnx)
            
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

    def change_appearance(self, choice):
        ctk.set_appearance_mode(choice)
        if choice == "light":
            self.m3_appearance_menu.entryconfig("Oscuro", state="normal")
            self.m3_appearance_menu.entryconfig("Claro", state="disabled")
        else:
            self.m3_appearance_menu.entryconfig("Claro", state="normal")
            self.m3_appearance_menu.entryconfig("Oscuro", state="disabled")

class DBWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.geometry("400x300")
        self.title("Conectar a base de datos")
        self.wm_transient(master)
        self.top_frame = ctk.CTkFrame(self, fg_color=None)
        self.info_frame = ctk.CTkFrame(self.top_frame, fg_color=None)
        self.entry_frame = ctk.CTkFrame(self.top_frame, fg_color=None)
        self.info_user = ctk.CTkLabel(self.info_frame, text="Usuario:")
        self.info_user.pack(fill="both")
        self.entry_user = ctk.CTkEntry(self.entry_frame)
        self.entry_user.pack(fill="x")
        self.info_host = ctk.CTkLabel(self.info_frame, text="Host:")
        self.info_host.pack(fill="both")
        self.entry_host = ctk.CTkEntry(self.entry_frame)
        self.entry_host.pack(fill="x")
        self.info_db = ctk.CTkLabel(self.info_frame, text="Base de datos:")
        self.info_db.pack(fill="both")
        self.entry_db = ctk.CTkEntry(self.entry_frame)
        self.entry_db.pack(fill="x")
        self.info_pwrd = ctk.CTkLabel(self.info_frame, text="Contraseña:")
        self.info_pwrd.pack(fill="both")
        self.entry_pwrd = ctk.CTkEntry(self.entry_frame)
        self.entry_pwrd.pack(fill="x")
        self.bttn_frame = ctk.CTkFrame(self.top_frame, fg_color=None)
        self.connect_bttn = ctk.CTkButton(self.bttn_frame, text="Conectar",
                                          command=self.connect_database)
        self.connect_bttn.pack()
        self.bttn_frame.pack(side="bottom")
        self.info_frame.pack(fill="none", side="left", expand=True)
        self.entry_frame.pack(fill="none", side="right", expand=True)
        self.top_frame.place(anchor="center", relx=.5, rely=.5)
        self.bind("<Return>", lambda event: self.connect_database())

    def connect_database(self):
        usr = self.entry_user.get()
        hst = self.entry_host.get()
        db = self.entry_db.get()
        pwrd = self.entry_pwrd.get()

        try:
            self.master.cnx = mysql.connector.connect(user=usr,
                                        password=pwrd,
                                        host=hst,
                                        database=db,
                                        connection_timeout=10)
            self.master.cursor = self.master.cnx.cursor()
            self.master.cursor.execute(f'''SHOW TABLES''')
            result = [True for item in self.master.cursor.fetchall() if item[0] == "equipos"]

            if not result:
                ans = messagebox.askyesno("", message= '''
                                    La tabla "equipos", necesaria para el programa, no existe.
                                    ¿Desea crearla?''')

                if ans == True:
                    try:
                        self.master.cursor.execute(TABLE_CREATION)

                    except mysql.connector.Error as err:
                        messagebox.showerror("", err)
                    else:
                        messagebox.showinfo("", "Tabla 'equipos' creada")
                        self.master.maintab.devices_obj.db_showentries()
                        self.destroy()
                
        except mysql.connector.Error as err:

            if err.errno == errorcode.ER_BAD_DB_ERROR:
                ans = messagebox.askyesno("", message= f'''
                                    La base de datos {db} no existe.
                                    ¿Desea crearla?''')

                if ans == True:
                    try:
                        self.master.cnx = mysql.connector.connect(user=usr,
                                                    password=pwrd,
                                                    host=hst,
                                                    connection_timeout=10)
                        self.master.cursor = self.master.cnx.cursor()
                        self.master.cursor.execute(f"CREATE DATABASE {db}")
                        self.master.cnx.database = db
                        self.master.cursor = self.master.cnx.cursor()
                        self.master.cursor.execute(TABLE_CREATION)

                    except mysql.connector.Error as err:
                        messagebox.showerror("", err)
                    else:
                        messagebox.showinfo("", f"Base de datos '{db}' creada")
                        self.master.maintab.devices_obj.db_showentries()
                        self.destroy()
                else:
                    messagebox.showinfo("", "Introduzca otra base de datos")
                pass
            elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                messagebox.showerror("", "El usuario o la contraseña son incorrectos")
                pass
            else:
                messagebox.showerror("", err)
        else:
            if self.master.cnx.is_connected():
                messagebox.showinfo("", "Conexión correcta a la base de datos")
                self.master.maintab.devices_obj.db_showentries()
            else:
                messagebox.showerror("", err)
            self.destroy()

class DBTab():
    def __init__(self, master):
        self.master = master
        self.tree_frame = ctk.CTkFrame(master, fg_color="transparent")
        self.info_frame = ctk.CTkFrame(master, fg_color="transparent")
        self.table = self.DBView(self.tree_frame, self)
        self.info = self.DBInfo(self.info_frame, self)
        self.info_frame.pack(side="right", fill="both", expand=True)
        self.tree_frame.pack(after=self.info_frame, side="left", fill="both", expand=True)


    class DBView(ttk.Treeview):
        def __init__(self, master, controller):
            self.controller = controller
            self.master = master
            self.search_frame = ctk.CTkFrame(master, fg_color=None)
            self.search_label = ctk.CTkLabel(self.search_frame, text="Buscar:")
            self.search_filter = ctk.CTkComboBox(self.search_frame, values=LABELS)
            self.search_bar = ctk.CTkEntry(self.search_frame)
            self.search_bttn = ctk.CTkButton(self.search_frame, text="Buscar", command=lambda: self.controller.db_search())
            self.clear_bttn = ctk.CTkButton(self.search_frame, text="Limpiar búsqueda", command= lambda: self.clear_search())
            self.scrollbar_y = ctk.CTkScrollbar(master)
            self.scrollbar_x = ctk.CTkScrollbar(master, orientation="horizontal")
            self.scrollbar_x.pack(side="bottom", fill="x")
            self.scrollbar_y.configure(command=self.yview)
            self.scrollbar_x.configure(command=self.xview)
            self.tree_label_frame = ctk.CTkFrame(master, fg_color=None)
            self.tree_label = ctk.CTkLabel(self.tree_label_frame, text="Número de equipos: 0", anchor="w")

            super().__init__(master,
                columns=["ID"] + LABELS, 
                show="headings",
                height=10,
                yscrollcommand=self.scrollbar_y.set,
                xscrollcommand=self.scrollbar_x.set)

            self.tag_configure("operativo", background="#E8F5E9")  # Verde claro
            self.tag_configure("reparacion", background="#FFF3E0")  # Naranja claro
            self.tag_configure("baja", background="#FFEBEE")  # Rojo claro

            self.heading("ID", text="ID")
            self.column("ID", width=40, anchor="center")

            for col in LABELS:
                self.heading(col, text=col)
                self.column(col, width=90,anchor="center")
            self.search_label.pack(side="left")
            self.search_filter.pack(side="left")
            self.search_bar.pack(side="left")
            self.search_bttn.pack(side="left")
            self.clear_bttn.pack(side="left")
            self.search_frame.pack(side="top", fill="x")
            self.pack(fill="both", expand=True)
            self.tree_label.pack(side="bottom", fill="x", anchor="s")
            self.tree_label_frame.pack(before=self.scrollbar_x, side="bottom", fill="x", anchor="s")
            self.scrollbar_y.pack(after=self.search_frame, side="right", fill="y")
            self.bind("<Double-1>", lambda e: self.controller.db_loadrowinfo())
            self.search_bar.bind("<Return>", lambda e: self.controller.db_search())

        def clear_search(self):
            self.search_filter.set(self.search_filter._values[0])
            self.search_bar.delete(0, tk.END)

    class DBInfo(ctk.CTkFrame):
        def __init__(self, master, controller):
            super().__init__(master, fg_color=None)
            self.controller = controller
            self.master = master
            self.entries = []

            self.title = ctk.CTkLabel(master, text="Datos del equipo", font=("Arial", 18))
            self.title.pack(fill="x")

            self.label_frame = ctk.CTkFrame(
                self,
                border_width=2,
                corner_radius=8,
                border_color=ctk.ThemeManager.theme["CTkFrame"]["border_color"],
                fg_color=None
            )
            self.label_frame.pack(fill="both", expand=True)
            self.pack(fill="both", expand=True)
            self.label_frame.grid_columnconfigure(1, weight=1)

            # Título interno del frame
            self.label_frame_title = ctk.CTkLabel(self.label_frame, text="Información", font=("Arial", 14, "bold"), anchor="w", padx=20, pady=10)
            self.label_frame_title.grid(row=0, column=0, columnspan=2, pady=(3, 10), sticky="ew", padx=3)

            for i, label in enumerate(LABELS):
                ctk.CTkLabel(self.label_frame, text=label).grid(row=i+1, column=0, sticky="ew", padx=3)

                if label in RULETA:
                    entry = ctk.CTkComboBox(self.label_frame, values=RULETA[label])
                    entry.grid(row=i+1, column=1, sticky="ew", padx=3)
                    entry.bind("<Return>", lambda e: self.controller.db_addentry())
                    self.entries.append(entry)
                else:
                    entry = ctk.CTkEntry(self.label_frame)
                    entry.grid(row=i+1, column=1, sticky="ew", padx=3)
                    entry.bind("<Return>", lambda e: self.controller.db_addentry())
                    self.entries.append(entry)

                    if i == 4:
                        entry.configure(placeholder_text="dd/mm/aaaa")

            self.options_frame = ctk.CTkFrame(self, fg_color=None)
            self.options_frame.rowconfigure((0, 1), weight=1)
            self.options_frame.columnconfigure((0, 1), weight=1)
            self.options_addrow = ctk.CTkButton(self.options_frame, text="Guardar", command=lambda: self.controller.db_addentry())
            self.options_clear = ctk.CTkButton(self.options_frame, text="Limpiar campos", command=lambda: info_clear(self.entries))
            self.options_loadrow = ctk.CTkButton(self.options_frame, text="Cargar equipo", command=lambda: self.controller.db_loadrowinfo())
            self.options_deleterow = ctk.CTkButton(self.options_frame, text="Eliminar equipo", command=lambda: self.controller.db_deleterow())
            self.options_addrow.grid(row=0, column=0)
            self.options_clear.grid(row=0, column=1)
            self.options_loadrow.grid(row=1, column=0)
            self.options_deleterow.grid(row=1, column=1)
            self.options_frame.pack(fill="both", expand=False)

    def db_showentries(self, filtered_rows=None):
        self.table.delete(*self.table.get_children())

        if filtered_rows:
            for row in filtered_rows:
                if row[6] in TREE_TAGS.keys():
                    self.table.insert("", "end", values=row, tags=(TREE_TAGS[row[6]],))
                else:
                    self.table.insert("", "end", values=row)

            self.table.tree_label.configure(text=f"Total de equipos: {len(filtered_rows)}")   
            return

        try:
            devices = push_query(self.master.master.master.menubar.dbwin,
                                    self.master.master.master.cnx,
                                    self.master.master.master.cursor,
                                    "SELECT * FROM equipos", fetch=True)
            self.master.master.master.cnx.commit()
            if not devices:
                self.table.insert("", "end", values=["" for i in range(14)])
                self.table.tree_label.configure(text=f"Total de equipos: 0")
                return

            for device in devices:
                if device[6] in TREE_TAGS.keys():
                    self.table.insert("", "end", values=device, tags=(TREE_TAGS[device[6]],))
                else:
                    self.table.insert("", "end", values=device)

            self.table.tree_label.configure(text=f"Total de equipos: {len(devices)}")

        except Exception as err:
            messagebox.showerror("", f"Error al cargar los equipos: {err}")

    def db_addentry(self):
        campos_requeridos = (self.info.entries[0],
                                self.info.entries[1],
                                self.info.entries[2],
                                self.info.entries[3])

        for entry in campos_requeridos:
            if not entry.get().strip():
                messagebox.showwarning("Campos incompletos", "Por favor, completa al menos los campos marcados con * (tipo, serial, marca, modelo).")
                return
            
        if self.info.entries[4].get():
            try:
                datetime.strptime(self.info.entries[4].get(), "%d/%m/%Y")
            except Exception as err:
                messagebox.showerror("Error", "Inserta el formato de fecha adecuado: dd/mm/aaaa")
                return
            
        try:
            campos = [entry.get() for entry in self.info.entries]
            serial = campos[3]
            entry_exists = push_query(self.master.master.master.menubar.dbwin,
                                      self.master.master.master.cnx,
                                      self.master.master.master.cursor,
                                      "SELECT * FROM `equipos` WHERE serial=%s",
                                      params=[serial], fetch=True)
            if entry_exists:
                if messagebox.askyesno("", f"Se ha encontrado un equipo con el serial {serial}. ¿Quiere actualizar sus campos?"):
                    push_query(self.master.master.master.menubar.dbwin,
                            self.master.master.master.cnx,
                            self.master.master.master.cursor,
                            UPDATE_ENTRY, params=campos)
                    self.master.master.master.cnx.commit()
                    messagebox.showinfo("Éxito", "Equipo actualizado correctamente.")

            else:
                push_query(self.master.master.master.menubar.dbwin,
                        self.master.master.master.cnx,
                        self.master.master.master.cursor,
                        ADD_ENTRY, params=campos)
                self.master.master.master.cnx.commit()
                messagebox.showinfo("Éxito", "Equipo guardado correctamente.")

        except Exception as err:
            messagebox.showerror("", f"Error: {err}")
        else:
            self.db_showentries()
            info_clear(self.info.entries)

    def db_loadrowinfo(self):
        selected_row = self.table.selection()
        if not selected_row:
            messagebox.showwarning("Seleccionar equipo", "Seleccione un equipo para cargar.")
            return
        
        row = self.table.item(selected_row)["values"]

        if len(row) != 15:
            messagebox.showerror("Error", "El formato de datos no es el esperado.")
            return

        info_clear(self.info.entries)

        for i, entry in enumerate(self.info.entries, 1):
            if type(entry) == ctk.CTkEntry:
                entry.insert(0, row[i])
            elif type(entry) == ctk.CTkComboBox:
                entry.set(row[i])

    def db_deleterow(self):
        selected_row = self.table.selection()
        if not selected_row:
            messagebox.showerror("Error", "No se puede identificar el equipo seleccionado.")
            return
        
        serial = self.table.item(selected_row)["values"][4]

        if not serial:
            messagebox.showwarning("Añadir serial", "Añada el serial del equipo para eliminarlo")
            return

        if messagebox.askyesno("Eliminar equipo", f"¿Quiere eliminar el equipo con serial {serial}?"):
            try:
                affected_rows = push_query(self.master.master.master.menubar.dbwin,
                        self.master.master.master.cnx,
                        self.master.master.master.cursor,
                        "DELETE FROM `equipos` WHERE serial= %s", params=[serial])

                if not affected_rows:
                    messagebox.showerror("Error", "No se ha encontrado el equipo con el serial seleccionado")
                    return

            except Exception as err:
                messagebox.showerror("Error", f"Sucedió el siguiente error: {err}")
            else:
                messagebox.showinfo("", "Equipo eliminado correctamente")
                self.db_showentries()
                info_clear(self.info.entries)

    def db_search(self):
        search = self.table.search_bar.get()
        filter_s = LABEL_CONVERSION[self.table.search_filter.get()]

        if search == "":
            self.db_showentries()
            return

        try:
            affected_rows = push_query(self.master.master.master.menubar.dbwin,
                                       self.master.master.master.cnx,
                                       self.master.master.master.cursor,
                                       f"SELECT * FROM `equipos` WHERE {filter_s} LIKE %s",
                                       params=(search,), fetch=True)

            if not affected_rows:
                self.table.delete(*self.table.get_children())
                self.table.insert("", "end", values=["" for i in range(14)])
                self.table.tree_label.configure(text=f"Total de equipos: 0")
                return

            self.db_showentries(affected_rows)

        except Exception as err:
            messagebox.showerror("Error", f"Error: {err}")

class MainTab(ctk.CTkTabview):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.devices_tab = self.add("Lista de equipos")
        self.devices_obj = DBTab(self.devices_tab)
        self.stats_tab = self.add("Estadísticas")

        self.pack(fill="both", expand=True)

class About(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Acerca de")
        self.wm_transient(master)

        ctk.CTkLabel(self,
                     text="Sistema de inventario de equipos",
                     font=("Arial", 14, "bold")).pack()
        ctk.CTkLabel(self,
                text="Desarrollado en Python con Tkinter y CustomTkinter",
                font=("Arial", 10)).pack()

class MainApp(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("1200x700")
        self.title("Inventariado de equipos")
        self.cnx = None
        self.cursor = None
        self.menubar = MenuBar(self)
        self.maintab = MainTab(self)
        self.protocol("WM_DELETE_WINDOW", self.close_everything)

    def close_everything(self):
        if self.cnx:
            self.cnx.close()
        self.destroy()


if __name__ == "__main__":
    app = MainApp()
    # Centro de la pantalla
    window_width = 1080
    window_height = 720
    position_right = app.winfo_screenwidth()//2 - window_width/2
    position_down = app.winfo_screenheight()//2 - window_height/2
    app.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
    app.mainloop()
