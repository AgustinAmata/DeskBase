import customtkinter as ctk
from src.db_manager import DBManager
from src.ui_components.menubar import Menubar
from src.ui_components.db_tab import DBTab

ctk.set_appearance_mode("light")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1200x700")
        self.title("DeskBase")
        self.db = DBManager()
        self.maintab = MainTab(self, self.db)
        self.db_tab = self.maintab.devices_obj
        self.menubar = Menubar(self, self.db, self.db_tab)
        self.protocol("WM_DELETE_WINDOW", self.close_everything)

    def close_everything(self):
        if self.db.cnx:
            self.db.close_connection(show_msg=False)
        self.destroy()

class MainTab(ctk.CTkTabview):
    def __init__(self, master, db: DBManager):
        super().__init__(master)
        self.master = master
        self.db = db
        self.devices_tab = self.add("Lista de equipos")
        self.devices_obj = DBTab(self.devices_tab, self.db)
        self.stats_tab = self.add("Estadísticas")

        self.pack(fill="both", expand=True)