import customtkinter as ctk
import tkinter as tk
from src.db_manager import DBManager
from src.logic import change_appearance, convert_to_excel, info_clear
from src.data_controller import db_deleterow, db_loadrowinfo, db_showentries
from src.ui_components.about import About
from src.ui_components.db_window import DBWindow

class Menubar(tk.Menu):
    def __init__(self, master, db: DBManager):
        super().__init__(master, tearoff=0)
        self.master = master
        self.db = db
        self.m1 = tk.Menu(self, tearoff=0)
        self.m1.add_command(label="Conectar a base de datos", command=self.create_dbwindow)
        self.m1.add_command(label="Desconectar base de datos", command=self.db.close_connection)
        self.m1.add_separator()
        self.m1.add_command(label="Exportar a Excel", command=convert_to_excel)
        master.config(menu=self)
        self.add_cascade(label="Archivo", menu=self.m1)

        self.m2 = tk.Menu(self, tearoff=0)
        self.m2.add_command(label="Limpiar campos")
        self.m2.add_separator()
        self.m2.add_command(label="Eliminar equipo")
        self.m2.add_command(label="Cargar equipo")
        self.m2.add_separator()
        self.m2.add_command(label="Mostrar equipos")
        self.add_cascade(label="Editar", menu=self.m2)

        self.m3 = tk.Menu(self, tearoff=0)
        self.m3_appearance_menu = tk.Menu(self.m3, tearoff=0)
        self.m3.add_cascade(menu=self.m3_appearance_menu, label="Apariencia")
        self.m3_appearance_menu.add_command(label="Claro", command=lambda: change_appearance(self, "light"), state="disabled")
        self.m3_appearance_menu.add_command(label="Oscuro", command=lambda: change_appearance(self, "dark"))
        self.add_cascade(label="Ver", menu=self.m3)

        self.m4 = tk.Menu(self, tearoff=0)
        self.m4.add_command(label="Acerca de", command=self.create_about)
        self.add_cascade(label="Ayuda", menu=self.m4)

        self.dbwin = None
        self.about = None

    def create_dbwindow(self):
        if self.dbwin is None or not self.dbwin.winfo_exists():
            self.dbwin = DBWindow(self.master, self.db)
        else:
            self.dbwin.focus()

    def create_about(self):
        if self.about is None or not self.about.winfo_exists():
            self.about = About(self.master)
        else:
            self.about.focus()