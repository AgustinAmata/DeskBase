import customtkinter as ctk
import re
import matplotlib.pyplot as plt
import sys
import os
from src.db_manager import DBManager
from src.ui_components.menubar import Menubar
from src.ui_components.db_tab import DBTab
from src.ui_components.login import LoginWindow
from src.ui_components.stats_tab import StatsTab
from src.constants import TEST_QUERIES
from src.db_manager import push_query
from src.data_controller import db_showentries
from src.logic import CenterWindowToDisplay

ctk.set_appearance_mode("light")

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DeskBase")
        self.iconbitmap(resource_path("assets/DeskBase_icon.ico"))
        self.geometry(CenterWindowToDisplay(self, 1080, 720, self._get_window_scaling()))
        self.db = DBManager()
        self.maintab = MainTab(self, self.db)
        self.db_tab = self.maintab.devices_tab
        self.login = LoginWindow(self, self.db, self.db_tab)
        self.menubar = Menubar(self, self.db, self.db_tab)
        self.privs = {
                      "SELECT": False,
                      "CREATE": False,
                      "UPDATE": False,
                      "DELETE": False,
                      "INSERT": False,
                      "DBInfo": False,
                      }
        self.protocol("WM_DELETE_WINDOW", self.close_everything)
        self.bind("<F5>", lambda e: db_showentries(self.db_tab))
        self.update_privileges()
        self.withdraw()

    def close_everything(self):
        if self.db.cnx:
            self.db.close_connection(show_msg=False)
        plt.close()
        self.quit()
        self.destroy()

    def check_privileges(self):
        grants = push_query(self.db, "SHOW GRANTS FOR current_user()", fetch=True)
    
        for key, priv_re in TEST_QUERIES.items():
            for grant in grants:
                priv_found = re.search(priv_re.format(db_name=self.db.db_name), grant[0])
                if priv_found:
                    self.privs[key] = True
                    break
                else:
                    self.privs[key] = False

    def update_privileges(self):
        sub_dict = {k:v for k,v in self.privs.items() if k in ["UPDATE", "DELETE", "INSERT"]}
        state_bool = {False: "disabled", True: "normal"}
        self.privs["DBInfo"] = any([False if v==False else True for v in sub_dict.values()])
        if not self.privs["DBInfo"]:
            self.maintab.devices_tab.table.device_add_bttn.configure(state="disabled")

            for i in ["Limpiar campos", "Eliminar equipo(s)", "Cargar equipo"]:
                self.menubar.m2.entryconfigure(i, state="disabled")
            self.maintab.devices_tab.info.options_clear.configure(state="disabled")
            self.maintab.devices_tab.info.options_addrow.configure(state="disabled")

        else:
            self.maintab.devices_tab.table.device_add_bttn.configure(state="normal")
            self.maintab.devices_tab.info.options_clear.configure(state="normal")
            self.maintab.devices_tab.info.options_addrow.configure(state=state_bool[sub_dict["UPDATE"]])
            self.menubar.m2.entryconfigure("Limpiar campos", state="normal")
            self.menubar.m2.entryconfigure("Cargar equipo", state="normal")
            self.menubar.m2.entryconfigure("Eliminar equipo(s)", state=state_bool[sub_dict["DELETE"]])

class MainTab(ctk.CTkTabview):
    def __init__(self, master, db: DBManager):
        super().__init__(master)
        self.master = master
        self.db = db
        self.devices_frame = self.add("Lista de equipos")
        self.devices_tab = DBTab(self.devices_frame, self.db, self.master)
        self.stats_frame = self.add("Estadísticas")
        self.stats_tab = StatsTab(self.stats_frame, self.db, self.master)

        self.pack(fill="both", expand=True)