import customtkinter as ctk
import sys
import os
from tkinter import messagebox
from src.data_controller import db_showentries
from src.db_manager import DBManager
from src.ui_components.db_tab import DBTab
from src.logic import info_clear, CenterWindowToDisplay

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    return os.path.join(base_path, relative_path)

class DBWindow(ctk.CTkToplevel):
    def __init__(self, master, db: DBManager, db_tab: DBTab):
        super().__init__(master)
        self.after(250, lambda: self.iconbitmap(resource_path("assets/DeskBase_icon.ico")))
        print(resource_path("assets/DeskBase_icon.ico"))
        self.master = master
        self.db = db
        self.db_tab = db_tab
        self.geometry(CenterWindowToDisplay(self, 400, 300, self._get_window_scaling()))
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
                                          command=self.enter_db_data)
        self.connect_bttn.pack()
        self.bttn_frame.pack(side="bottom")
        self.info_frame.pack(fill="none", side="left", expand=True)
        self.entry_frame.pack(fill="none", side="right", expand=True)
        self.top_frame.place(anchor="center", relx=.5, rely=.5)
        self.bind("<Return>", lambda event: self.enter_db_data())

    def enter_db_data(self):
        user = self.entry_user.get()
        host = self.entry_host.get()
        pwrd = self.entry_pwrd.get()
        db_name = self.entry_db.get()
        if not db_name:
            messagebox.showerror("", "Inserte una base de datos")
            return
        if self.db.connect_to(user, pwrd, host, db_name):
            self.master.check_privileges()
            if self.master.privs["SELECT"] == False:
                messagebox.showwarning("", "El usuario no tiene el permiso necesario (SELECT) para visualizar los equipos, inténtelo con otro usuario")
                self.db.close_connection(show_msg=False)
                return
            self.master.update_privileges()
            if not self.db_tab.table.hidden:
                self.db_tab.table.hide_show_dbinfo()
            info_clear(self.db_tab.info.entries)
            self.db_tab.table.tree_deselect()
            db_showentries(self.db_tab)
            self.destroy()
