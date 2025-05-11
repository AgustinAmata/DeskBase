import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from src.db_manager import DBManager
from src.constants import LABELS, RULETA
from src.data_controller import db_addentry, db_deleterow, db_loadrowinfo, db_search, db_showentries
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
        self.search_filter = ctk.CTkOptionMenu(self.search_frame, values=LABELS[:len(LABELS)-2])
        self.search_bar = ctk.CTkEntry(self.search_frame)
        self.strict_search = tk.BooleanVar(value=False)
        self.strict_search_box = ctk.CTkCheckBox(self.search_frame, text="Estricto", variable=self.strict_search, onvalue=True, offvalue=False, width=80)
        self.search_bttn = ctk.CTkButton(self.search_frame, text="Buscar", command=lambda: db_search(self.db_tab, self.strict_search.get()), width=60)
        self.clear_bttn = ctk.CTkButton(self.search_frame, text="Limpiar búsqueda", command= lambda: self.clear_search(), width=100)
        self.device_add_bttn = ctk.CTkButton(self.search_frame, text="Agregar/modificar equipo", command= lambda: self.hide_show_dbinfo())
        self.scrollbar_y = ctk.CTkScrollbar(master)
        self.scrollbar_x = ctk.CTkScrollbar(master, orientation="horizontal")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.scrollbar_y.configure(command=self.yview)
        self.scrollbar_x.configure(command=self.xview)
        self.tree_label_frame = ctk.CTkFrame(master, fg_color=None)
        self.tree_label = ctk.CTkLabel(self.tree_label_frame, text="Total de equipos: 0", anchor="w")
        self.update_list_bttn = ctk.CTkButton(self.tree_label_frame, text="Actualizar lista", command= lambda: db_showentries(self.db_tab), width=100)
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
        self.strict_search_box.pack(side="left")
        self.search_bttn.pack(side="left")
        self.clear_bttn.pack(side="left")
        self.device_add_bttn.pack(side="right")
        self.search_frame.pack(side="top", fill="x")
        self.pack(fill="both", expand=True)
        self.tree_label.pack(side="left", anchor="w")
        self.update_list_bttn.pack(side="right", anchor="e")
        self.tree_label_frame.pack(before=self.scrollbar_x, side="bottom", anchor="s", fill="x")
        self.scrollbar_y.pack(after=self.search_frame, side="right", fill="y")
        self.bind("<Double-1>", lambda e: self.load_selected_row())
        self.search_bar.bind("<Return>", lambda e: db_search(self.db_tab, self.strict_search.get()))

    def clear_search(self):
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

        for i, label in enumerate(LABELS[:len(LABELS)-2]):
            ctk.CTkLabel(self.label_frame, text=label).grid(row=i+1, column=0, sticky="ew", padx=3)

            if label in RULETA:
                entry = ctk.CTkOptionMenu(self.label_frame, values=RULETA[label], width=150)
                entry.grid(row=i+1, column=1, sticky="ew", padx=3)
                entry.bind("<Return>", lambda e: self.check_and_call_db_addentry())
                self.entries.append(entry)
            else:
                entry = ctk.CTkEntry(self.label_frame, width=150)
                entry.grid(row=i+1, column=1, sticky="ew", padx=3)
                entry.bind("<Return>", lambda e: self.check_and_call_db_addentry())
                self.entries.append(entry)

                if i == 4:
                    entry.configure(placeholder_text="dd/mm/aaaa")

        self.options_frame = ctk.CTkFrame(self, fg_color=None)
        self.options_frame.rowconfigure((0, 1), weight=1)
        self.options_frame.columnconfigure((0, 1), weight=1)
        self.options_addrow = ctk.CTkButton(self.options_frame, text="Guardar/Modificar", command=lambda e: self.check_and_call_db_addentry())
        self.options_clear = ctk.CTkButton(self.options_frame, text="Limpiar campos", command=lambda: info_clear(self.entries))
        self.options_loadrow = ctk.CTkButton(self.options_frame, text="Cargar equipo", command=lambda: db_loadrowinfo(self.db_tab))
        self.options_deleterow = ctk.CTkButton(self.options_frame, text="Eliminar equipo", command=lambda: db_deleterow(self.db_tab))
        self.options_addrow.grid(row=0, column=0)
        self.options_clear.grid(row=0, column=1)
        self.options_loadrow.grid(row=1, column=0)
        self.options_deleterow.grid(row=1, column=1)
        self.options_frame.pack(fill="both", expand=False)

    def check_and_call_db_addentry(self):
        campos_requeridos = (self.entries[0],
                                self.entries[1],
                                self.entries[2],
                                self.entries[3])

        for entry in campos_requeridos:
            if not entry.get().strip():
                messagebox.showwarning("Campos incompletos", "Por favor, completa al menos los campos marcados con * (tipo, serial, marca, modelo).")
                return
            
        if self.entries[4].get():
            try:
                datetime.strptime(self.entries[4].get(), "%d/%m/%Y")
            except Exception as err:
                messagebox.showerror("Error", "Inserta el formato de fecha adecuado: dd/mm/aaaa")
                return
            
        for int_entry, name in zip(self.entries[LABELS.index("RAM Tarjeta Gráfica (GB)")::2], LABELS[LABELS.index("RAM Tarjeta Gráfica (GB)"):len(LABELS)-2:2]):
            try:
                int(int_entry.get())

            except Exception as err:
                messagebox.showerror("", f"Inserte un número válido en {name}")
                return
            
        db_addentry(self.db_tab)