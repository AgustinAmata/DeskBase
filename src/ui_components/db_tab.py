import customtkinter as ctk
import tkinter as tk
from src.constants import LABELS, RULETA
from src.data_controller import db_addentry, db_deleterow, db_loadrowinfo, db_search, db_showentries
from db_manager import DBManager
from src.logic import info_clear
from tkinter import ttk

class DBTab():
    def __init__(self, master, db: DBManager):
        self.master = master
        self.tree_frame = ctk.CTkFrame(master, fg_color="transparent")
        self.info_frame = ctk.CTkFrame(master, fg_color="transparent")
        self.table = self.DBView(self.tree_frame, self)
        self.info = self.DBInfo(self.info_frame, self)
        self.info_frame.pack(side="right", fill="both", expand=True)
        self.tree_frame.pack(after=self.info_frame, side="left", fill="both", expand=True)

    class DBView(ttk.Treeview):
        def __init__(self, master, db: DBManager):
            self.master = master
            self.db = db
            self.search_frame = ctk.CTkFrame(master, fg_color=None)
            self.search_label = ctk.CTkLabel(self.search_frame, text="Buscar:")
            self.search_filter = ctk.CTkComboBox(self.search_frame, values=LABELS)
            self.search_bar = ctk.CTkEntry(self.search_frame)
            self.search_bttn = ctk.CTkButton(self.search_frame, text="Buscar", command=lambda: db_search())
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
            self.bind("<Double-1>", lambda e: db_loadrowinfo())
            self.search_bar.bind("<Return>", lambda e: db_search())

        def clear_search(self):
            self.search_filter.set(self.search_filter._values[0])
            self.search_bar.delete(0, tk.END)

    class DBInfo(ctk.CTkFrame):
        def __init__(self, master, db: DBManager):
            super().__init__(master, fg_color=None)
            self.db = db
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
                    entry.bind("<Return>", lambda e: db_addentry())
                    self.entries.append(entry)
                else:
                    entry = ctk.CTkEntry(self.label_frame)
                    entry.grid(row=i+1, column=1, sticky="ew", padx=3)
                    entry.bind("<Return>", lambda e: db_addentry())
                    self.entries.append(entry)

                    if i == 4:
                        entry.configure(placeholder_text="dd/mm/aaaa")

            self.options_frame = ctk.CTkFrame(self, fg_color=None)
            self.options_frame.rowconfigure((0, 1), weight=1)
            self.options_frame.columnconfigure((0, 1), weight=1)
            self.options_addrow = ctk.CTkButton(self.options_frame, text="Guardar", command=lambda: db_addentry(self))
            self.options_clear = ctk.CTkButton(self.options_frame, text="Limpiar campos", command=lambda: info_clear(self.entries))
            self.options_loadrow = ctk.CTkButton(self.options_frame, text="Cargar equipo", command=lambda: db_loadrowinfo())
            self.options_deleterow = ctk.CTkButton(self.options_frame, text="Eliminar equipo", command=lambda: db_deleterow())
            self.options_addrow.grid(row=0, column=0)
            self.options_clear.grid(row=0, column=1)
            self.options_loadrow.grid(row=1, column=0)
            self.options_deleterow.grid(row=1, column=1)
            self.options_frame.pack(fill="both", expand=False)