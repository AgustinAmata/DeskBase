import customtkinter as ctk
from datetime import datetime
from src.constants import TREE_TAGS, ADD_ENTRY, UPDATE_ENTRY, LABEL_CONVERSION
from src.db_manager import push_query
from src.logic import info_clear
from tkinter import messagebox

def db_showentries(self, filtered_rows=None):
    self.table.delete(*self.table.get_children())

    if filtered_rows:
        for row in filtered_rows:
            if row[6] in TREE_TAGS.keys():
                self.table.insert("", "end", values=row, tags=(TREE_TAGS[row[6]],))
            else:
                self.table.insert("", "end", values=row)

        self.table.tree_label.configure(text=f"Total de equipos: {len(filtered_rows)}")   
        return

    try:
        devices = push_query(self.master.master.master.menubar.dbwin,
                                self.master.master.master.cnx,
                                self.master.master.master.cursor,
                                "SELECT * FROM equipos", fetch=True)
        self.master.master.master.cnx.commit()
        if not devices:
            self.table.insert("", "end", values=["" for i in range(14)])
            self.table.tree_label.configure(text=f"Total de equipos: 0")
            return

        for device in devices:
            if device[6] in TREE_TAGS.keys():
                self.table.insert("", "end", values=device, tags=(TREE_TAGS[device[6]],))
            else:
                self.table.insert("", "end", values=device)

        self.table.tree_label.configure(text=f"Total de equipos: {len(devices)}")

    except Exception as err:
        messagebox.showerror("", f"Error al cargar los equipos: {err}")

def db_addentry(self):
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
        
    try:
        campos = [entry.get() for entry in self.entries]
        serial = campos[3]
        entry_exists = push_query(self.master.master.master.menubar.dbwin,
                                    self.master.master.master.cnx,
                                    self.master.master.master.cursor,
                                    "SELECT * FROM `equipos` WHERE serial=%s",
                                    params=[serial], fetch=True)
        if entry_exists:
            if messagebox.askyesno("", f"Se ha encontrado un equipo con el serial {serial}. ¿Quiere actualizar sus campos?"):
                push_query(self.master.master.master.menubar.dbwin,
                        self.master.master.master.cnx,
                        self.master.master.master.cursor,
                        UPDATE_ENTRY, params=campos)
                self.master.master.master.cnx.commit()
                messagebox.showinfo("Éxito", "Equipo actualizado correctamente.")

        else:
            push_query(self.master.master.master.menubar.dbwin,
                    self.master.master.master.cnx,
                    self.master.master.master.cursor,
                    ADD_ENTRY, params=campos)
            self.master.master.master.cnx.commit()
            messagebox.showinfo("Éxito", "Equipo guardado correctamente.")

    except Exception as err:
        messagebox.showerror("", f"Error: {err}")
    else:
        self.db_showentries()
        info_clear(self.entries)

def db_loadrowinfo(self):
    selected_row = self.table.selection()
    if not selected_row:
        messagebox.showwarning("Seleccionar equipo", "Seleccione un equipo para cargar.")
        return
    
    row = self.table.item(selected_row)["values"]

    if len(row) != 15:
        messagebox.showerror("Error", "El formato de datos no es el esperado.")
        return

    info_clear(self.info.entries)

    for i, entry in enumerate(self.info.entries, 1):
        if type(entry) == ctk.CTkEntry:
            entry.insert(0, row[i])
        elif type(entry) == ctk.CTkComboBox:
            entry.set(row[i])

def db_deleterow(self):
    selected_row = self.table.selection()
    if not selected_row:
        messagebox.showerror("Error", "No se puede identificar el equipo seleccionado.")
        return
    
    serial = self.table.item(selected_row)["values"][4]

    if not serial:
        messagebox.showwarning("Añadir serial", "Añada el serial del equipo para eliminarlo")
        return

    if messagebox.askyesno("Eliminar equipo", f"¿Quiere eliminar el equipo con serial {serial}?"):
        try:
            affected_rows = push_query(self.master.master.master.menubar.dbwin,
                    self.master.master.master.cnx,
                    self.master.master.master.cursor,
                    "DELETE FROM `equipos` WHERE serial= %s", params=[serial])

            if not affected_rows:
                messagebox.showerror("Error", "No se ha encontrado el equipo con el serial seleccionado")
                return

        except Exception as err:
            messagebox.showerror("Error", f"Sucedió el siguiente error: {err}")
        else:
            messagebox.showinfo("", "Equipo eliminado correctamente")
            self.db_showentries()
            info_clear(self.info.entries)

def db_search(self):
    if not self.master.master.master.cnx:
        messagebox.showerror("", "Conéctese a una base de datos primero")
        return

    search = self.table.search_bar.get()
    filter_s = LABEL_CONVERSION[self.table.search_filter.get()]

    if search == "":
        self.db_showentries()
        return

    try:
        affected_rows = push_query(self.master.master.master.menubar.dbwin,
                                    self.master.master.master.cnx,
                                    self.master.master.master.cursor,
                                    f"SELECT * FROM `equipos` WHERE {filter_s} LIKE %s",
                                    params=(search,), fetch=True)

        if not affected_rows:
            self.table.delete(*self.table.get_children())
            self.table.insert("", "end", values=["" for i in range(14)])
            self.table.tree_label.configure(text=f"Total de equipos: 0")
            return

        self.db_showentries(affected_rows)

    except Exception as err:
        messagebox.showerror("Error", f"Error: {err}")