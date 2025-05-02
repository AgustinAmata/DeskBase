import customtkinter as ctk
import logging
from datetime import datetime
from src.constants import TREE_TAGS, ADD_ENTRY, UPDATE_ENTRY, LABEL_CONVERSION
from src.db_manager import push_query
from src.logic import info_clear
from tkinter import messagebox

logger = logging.getLogger(__name__)

def db_showentries(self, filtered_rows=None):
    self.table.delete(*self.table.get_children())

    if not self.db.cnx:
        messagebox.showerror("", "Conéctese a una base de datos primero")
        return

    if filtered_rows:
        for row in filtered_rows:
            if row[6] in TREE_TAGS.keys():
                self.table.insert("", "end", values=row, tags=(TREE_TAGS[row[6]],))
            else:
                self.table.insert("", "end", values=row)

        self.table.tree_label.configure(text=f"Total de equipos: {len(filtered_rows)}")   
        return

    try:
        devices = push_query(self.db,
                             "SELECT * FROM equipos", fetch=True)

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
        logger.error("Error while trying to load device list into DeskBase", exc_info=True)
        messagebox.showerror("", f"Error al cargar los equipos: {err}")

def db_addentry(self):
    if not self.db.cnx:
        messagebox.showerror("", "Conéctese a una base de datos primero")
        return

    campos_requeridos = (self.info.entries[0],
                            self.info.entries[1],
                            self.info.entries[2],
                            self.info.entries[3])

    for entry in campos_requeridos:
        if not entry.get().strip():
            messagebox.showwarning("Campos incompletos", "Por favor, completa al menos los campos marcados con * (tipo, serial, marca, modelo).")
            return
        
    if self.info.entries[4].get():
        try:
            datetime.strptime(self.info.entries[4].get(), "%d/%m/%Y")
        except Exception as err:
            messagebox.showerror("Error", "Inserta el formato de fecha adecuado: dd/mm/aaaa")
            return
        
    try:
        campos = [entry.get() for entry in self.info.entries]
        serial = campos[3]
        entry_exists = push_query(self.db,
                                  "SELECT * FROM `equipos` WHERE serial=%s",
                                  params=[serial], fetch=True)
        if entry_exists:
            if messagebox.askyesno("", f"Se ha encontrado un equipo con el serial {serial}. ¿Quiere actualizar sus campos?"):
                campos.append(entry_exists[0][0])
                push_query(self.db,
                        UPDATE_ENTRY, params=campos)

                logger.info("Updated device with serial: %s and id: %s", serial, campos[-1])
                messagebox.showinfo("Éxito", "Equipo actualizado correctamente.")

        else:
            push_query(self.db,
                    ADD_ENTRY, params=campos)

            logger.info("Saved device with serial: %s in database", serial)
            messagebox.showinfo("Éxito", "Equipo guardado correctamente.")

    except Exception as err:
        logger.error("Error while trying to save/update device", exc_info=True)
        messagebox.showerror("", f"Error: {err}")
    else:
        db_showentries(self)
        info_clear(self.info.entries)

def db_loadrowinfo(self):
    if not self.db.cnx:
        messagebox.showerror("", "Conéctese a una base de datos primero")
        return

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
    if not self.db.cnx:
        messagebox.showerror("", "Conéctese a una base de datos primero")
        return

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
            affected_rows = push_query(self.db,
                    "DELETE FROM `equipos` WHERE serial= %s", params=[serial])

            if not affected_rows:
                logger.error("Tried to remove device with serial: %s, but it was not found in the database", serial)
                messagebox.showerror("Error", "No se ha encontrado el equipo con el serial seleccionado")
                return

        except Exception as err:
            logger.error("Error while trying to remove device from database", exc_info=True)
            messagebox.showerror("Error", f"Sucedió el siguiente error: {err}")
        else:
            logger.info("Device with serial: %s has been removed", serial)
            messagebox.showinfo("", "Equipo eliminado correctamente")
            db_showentries(self)
            info_clear(self.info.entries)

def db_search(self):
    if not self.db.cnx:
        messagebox.showerror("", "Conéctese a una base de datos primero")
        return

    search = self.table.search_bar.get()
    filter_s = LABEL_CONVERSION[self.table.search_filter.get()]

    if search == "":
        db_showentries(self)
        return

    try:
        affected_rows = push_query(self.db,
                                    f"SELECT * FROM `equipos` WHERE {filter_s} LIKE %s",
                                    params=(search,), fetch=True)

        if not affected_rows:
            self.table.delete(*self.table.get_children())
            self.table.insert("", "end", values=["" for i in range(14)])
            self.table.tree_label.configure(text=f"Total de equipos: 0")
            return

        db_showentries(self, affected_rows)

    except Exception as err:
        logger.error("Error while trying to search in the DeskBase table", exc_info=True)
        messagebox.showerror("Error", f"Error: {err}")
