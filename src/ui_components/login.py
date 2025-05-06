import customtkinter as ctk
from tkinter import messagebox
from src.data_controller import db_showentries
from src.db_manager import push_query, DBManager

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, master, db: DBManager, db_tab):
        super().__init__(master)
        self.master = master
        self.db = db
        self.db_tab = db_tab
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
                                          command=self.enter_db_data)
        self.connect_bttn.pack()
        self.bttn_frame.pack(side="bottom")
        self.info_frame.pack(fill="none", side="left", expand=True)
        self.entry_frame.pack(fill="none", side="right", expand=True)
        self.top_frame.place(anchor="center", relx=.5, rely=.5)
        self.bind("<Return>", lambda event: self.enter_db_data())
        self.protocol("WM_DELETE_WINDOW", self.close_everything)

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
            db_showentries(self.db_tab)
            self.destroy()
            self.master.deiconify()
    
    def close_everything(self):
        self.destroy()
        self.master.destroy()
