import customtkinter as ctk
import os
import sys
from src.logic import CenterWindowToDisplay

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    return os.path.join(base_path, relative_path)

class About(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.after(250, lambda: self.iconbitmap(resource_path("assets/DeskBase_icon.ico")))
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

        ctk.CTkLabel(self.about_frame,
                text='''Icono de DeskBase creado por
kerismaker en www.flaticon.com''',
                font=("Arial", 10)).pack(pady=(20,0))

        self.about_frame.pack(anchor="center", expand=True)