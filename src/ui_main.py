import customtkinter as ctk
from src.db_manager import DBManager
from src.ui_components.menubar import Menubar
# from ui_components.db_tab import DBTab

ctk.set_appearance_mode("light")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1200x700")
        self.title("DeskBase")
        self.db = DBManager()
        self.menubar = Menubar(self, self.db)
        # self.maintab = DBTab(self)
        self.protocol("WM_DELETE_WINDOW", self.close_everything)

    def close_everything(self):
        if self.db.cnx:
            self.db.close_connection(show_msg=False)
        self.destroy()