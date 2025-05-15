import customtkinter as ctk
from src.logic import CenterWindowToDisplay

class About(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Acerca de")
        self.geometry(CenterWindowToDisplay(self, 400, 300, self._get_window_scaling()))
        self.wm_transient(master)
        self.about_frame = ctk.CTkFrame(self, fg_color="transparent")

        ctk.CTkLabel(self.about_frame,
                     text='''DeskBase:
Sistema de inventario de equipos''',
                     font=("Arial", 14, "bold")).pack()

        ctk.CTkLabel(self.about_frame,
                text='''Desarrollado en Python por
Agustín Amata
y
Francisco Mira-Perceval Maiquez''',
                font=("Arial", 10)).pack(pady=(20,0))

        ctk.CTkLabel(self.about_frame,
                text="MIT License",
                font=("Arial", 12, "bold")).pack(pady=(20,0))

        self.about_frame.pack(anchor="center", expand=True)