import customtkinter as ctk
import re
from src.db_manager import DBManager
from src.ui_components.menubar import Menubar
from src.ui_components.db_tab import DBTab
from src.ui_components.login import LoginWindow
from src.constants import TEST_QUERIES
from src.db_manager import push_query

ctk.set_appearance_mode("light")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1200x700")
        self.title("DeskBase")
        self.db = DBManager()
        self.maintab = MainTab(self, self.db)
        self.db_tab = self.maintab.devices_obj
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
        self.update_privileges()
        self.withdraw()

    def close_everything(self):
        if self.db.cnx:
            self.db.close_connection(show_msg=False)
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
            self.maintab.devices_obj.table.device_add_bttn.configure(state="disabled")

            for i in ["Limpiar campos", "Eliminar equipo(s)", "Cargar equipo"]:
                self.menubar.m2.entryconfigure(i, state="disabled")
            self.maintab.devices_obj.info.options_clear.configure(state="disabled")
            self.maintab.devices_obj.info.options_addrow.configure(state="disabled")

        else:
            self.maintab.devices_obj.table.device_add_bttn.configure(state="normal")
            self.maintab.devices_obj.info.options_clear.configure(state="normal")
            self.maintab.devices_obj.info.options_addrow.configure(state=state_bool[sub_dict["UPDATE"]])
            self.menubar.m2.entryconfigure("Limpiar campos", state="normal")
            self.menubar.m2.entryconfigure("Cargar equipo", state="normal")
            self.menubar.m2.entryconfigure("Eliminar equipo(s)", state=state_bool[sub_dict["DELETE"]])

class MainTab(ctk.CTkTabview):
    def __init__(self, master, db: DBManager):
        super().__init__(master)
        self.master = master
        self.db = db
        self.devices_tab = self.add("Lista de equipos")
        self.devices_obj = DBTab(self.devices_tab, self.db, self.master)
        self.stats_tab = self.add("Estadísticas")

        self.pack(fill="both", expand=True)