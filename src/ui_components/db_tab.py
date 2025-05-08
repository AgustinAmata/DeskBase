import customtkinter as ctk
import tkinter as tk
import tkinter as tk
from src.db_manager import DBManager
from src.constants import LABELS, RULETA
from src.data_controller import db_addentry, db_deleterow, db_loadrowinfo, db_search
from src.logic import info_clear
from tkinter import ttk

class DBTab():
    def __init__(self, master: tk.Frame, db: DBManager):
        self.master = master
        self.db = db
        self.tree_frame = ctk.CTkFrame(master, fg_color="transparent")
        self.info_frame = ctk.CTkFrame(master, fg_color="transparent")
        self.info = DBInfo(self.info_frame, self.db, self)
        self.table = DBView(self.tree_frame, self.db, self)
        self.master.grid_columnconfigure(0, weight=3)
        self.master.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid(row=0, column=0, sticky="nsew")

class DBView(ttk.Treeview):
    def __init__(self, master, db: DBManager, db_tab: DBTab):
        self.master = master
        self.db = db
        self.db_tab = db_tab
        self.search_frame = ctk.CTkFrame(master, fg_color=None)
        self.search_label = ctk.CTkLabel(self.search_frame, text="Buscar:")
        self.search_filter = ctk.CTkComboBox(self.search_frame, values=LABELS[:16])
        self.search_bar = ctk.CTkEntry(self.search_frame)
        self.search_bttn = ctk.CTkButton(self.search_frame, text="Buscar", command=lambda: db_search(self.db_tab), width=70)
        self.clear_bttn = ctk.CTkButton(self.search_frame, text="Limpiar búsqueda", command= lambda: self.clear_search())
        self.device_add_bttn = ctk.CTkButton(self.search_frame, text="Agregar/modificar equipo", command= lambda: self.hide_show_dbinfo())
        self.scrollbar_y = ctk.CTkScrollbar(master)
        self.scrollbar_x = ctk.CTkScrollbar(master, orientation="horizontal")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.scrollbar_y.configure(command=self.yview)
        self.scrollbar_x.configure(command=self.xview)
        self.tree_label_frame = ctk.CTkFrame(master, fg_color=None)
        self.tree_label = ctk.CTkLabel(self.tree_label_frame, text="Número de equipos: 0", anchor="w")
        self.hidden = True

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
        self.device_add_bttn.pack(side="right")
        self.search_frame.pack(side="top", fill="x")
        self.pack(fill="both", expand=True)
        self.tree_label.pack(side="bottom", fill="x", anchor="s")
        self.tree_label_frame.pack(before=self.scrollbar_x, side="bottom", fill="x", anchor="s")
        self.scrollbar_y.pack(after=self.search_frame, side="right", fill="y")
        self.bind("<Double-1>", lambda e: self.load_selected_row())
        self.search_bar.bind("<Return>", lambda e: db_search(self.db_tab))

    def clear_search(self):
        self.search_filter.set(self.search_filter._values[0])
        self.search_bar.delete(0, tk.END)

    def hide_show_dbinfo(self):
        if not self.hidden:
            self.db_tab.info_frame.grid_remove()
            self.hidden = True
        else:
            self.db_tab.info_frame.grid(row=0, column=1, sticky="nsew")
            self.hidden = False

    def load_selected_row(self):
        db_loadrowinfo(self.db_tab)
        if self.hidden:
            self.hide_show_dbinfo()

class DBInfo(ctk.CTkFrame):
    def __init__(self, master, db: DBManager, db_tab: DBTab):
        super().__init__(master, fg_color=None)
        self.db = db
        self.master = master
        self.db_tab = db_tab
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

        self.label_frame_title = ctk.CTkLabel(self.label_frame, text="Información", font=("Arial", 14, "bold"), anchor="w", padx=20, pady=10)
        self.label_frame_title.grid(row=0, column=0, columnspan=2, pady=(3, 10), sticky="ew", padx=3)

        for i, label in enumerate(LABELS[:16]):
            ctk.CTkLabel(self.label_frame, text=label).grid(row=i+1, column=0, sticky="ew", padx=3)

            if label in RULETA:
                entry = ctk.CTkComboBox(self.label_frame, values=RULETA[label])
                entry.grid(row=i+1, column=1, sticky="ew", padx=3)
                entry.bind("<Return>", lambda e: db_addentry(self.db_tab))
                self.entries.append(entry)
            else:
                entry = ctk.CTkEntry(self.label_frame)
                entry.grid(row=i+1, column=1, sticky="ew", padx=3)
                entry.bind("<Return>", lambda e: db_addentry(self.db_tab))
                self.entries.append(entry)

                if i == 4:
                    entry.configure(placeholder_text="dd/mm/aaaa")

        self.options_frame = ctk.CTkFrame(self, fg_color=None)
        self.options_frame.rowconfigure((0, 1), weight=1)
        self.options_frame.columnconfigure((0, 1), weight=1)
        self.options_addrow = ctk.CTkButton(self.options_frame, text="Guardar/Modificar", command=lambda: db_addentry(self.db_tab))
        self.options_clear = ctk.CTkButton(self.options_frame, text="Limpiar campos", command=lambda: info_clear(self.entries))
        self.options_loadrow = ctk.CTkButton(self.options_frame, text="Cargar equipo", command=lambda: db_loadrowinfo(self.db_tab))
        self.options_deleterow = ctk.CTkButton(self.options_frame, text="Eliminar equipo", command=lambda: db_deleterow(self.db_tab))
        self.options_addrow.grid(row=0, column=0)
        self.options_clear.grid(row=0, column=1)
        self.options_loadrow.grid(row=1, column=0)
        self.options_deleterow.grid(row=1, column=1)
        self.options_frame.pack(fill="both", expand=False)