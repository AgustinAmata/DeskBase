import customtkinter as ctk

def change_appearance(self, choice):
    ctk.set_appearance_mode(choice)
    if choice == "light":
        self.m3_appearance_menu.entryconfig("Oscuro", state="normal")
        self.m3_appearance_menu.entryconfig("Claro", state="disabled")
    else:
        self.m3_appearance_menu.entryconfig("Claro", state="normal")
        self.m3_appearance_menu.entryconfig("Oscuro", state="disabled")

def convert_to_excel():
    pass

def info_clear(entries):
    pass