import customtkinter as ctk
import logging
import mysql.connector
from src.constants import TREE_TAGS, ADD_ENTRY, UPDATE_ENTRY, LABEL_CONVERSION, LABELS
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
            if row[LABELS.index("Ubicación")] in TREE_TAGS.keys():
                self.table.insert("", "end", values=row, tags=(TREE_TAGS[row[LABELS.index("Ubicación")]],))
            else:
                self.table.insert("", "end", values=row)

        self.table.tree_label.configure(text=f"Total de equipos: {len(filtered_rows)}")   
        return

    try:
        devices = push_query(self.db,
                             "SELECT * FROM equipos", fetch=True)

        if not devices:
            self.table.insert("", "end", values=["" for i in range(len(LABELS)+1)])
            self.table.tree_label.configure(text=f"Total de equipos: 0")
            return

        for device in devices:
            if device[LABELS.index("Ubicación")] in TREE_TAGS.keys():
                self.table.insert("", "end", values=device, tags=(TREE_TAGS[device[LABELS.index("Ubicación")]],))
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
        
    try:
        campos = [entry.get() for entry in self.info.entries]
        serial = campos[LABELS.index("Serial*")]
        entry_exists = push_query(self.db,
                                  "SELECT * FROM `equipos` WHERE serial=%s",
                                  params=[serial], fetch=True)
        if entry_exists:
            if messagebox.askyesno("", f"Se ha encontrado un equipo con el serial {serial}. ¿Quiere actualizar sus campos?"):
                if not self.main_win.privs["UPDATE"]:
                    messagebox.showerror("","El usuario no tiene permisos para modificar entradas")
                    return

                campos.append(entry_exists[0][0])
                push_query(self.db,
                        UPDATE_ENTRY, params=campos)

                logger.info("Updated device with serial: %s and id: %s", serial, campos[-1])
                messagebox.showinfo("Éxito", "Equipo actualizado correctamente.")

        else:
            if not self.main_win.privs["INSERT"]:
                messagebox.showerror("","El usuario no tiene permisos para añadir entradas")
                return

            push_query(self.db,
                    ADD_ENTRY, params=campos)

            logger.info("Saved device with serial: %s in database", serial)
            messagebox.showinfo("Éxito", "Equipo guardado correctamente.")

    except mysql.connector.Error as err:
        messagebox.showerror("", f"Sucedió el siguiente error: {err}")

    except Exception as err:
        logger.exception("Error while trying to save/update device")
        messagebox.showerror("", f"Error: {err}")
    else:
        db_showentries(self)
        info_clear(self.info.entries)
        if not self.table.hidden:
            self.table.hide_show_dbinfo()

def db_loadrowinfo(self):
    if not self.db.cnx:
        messagebox.showerror("", "Conéctese a una base de datos primero")
        return

    selected_row = self.table.selection()
    if not selected_row:
        messagebox.showwarning("Seleccionar equipo", "Seleccione un equipo para cargar.")
        return
    
    row = self.table.item(selected_row)["values"]

    if len(row) != len(LABELS)+1:
        messagebox.showerror("Error", "El formato de datos no es el esperado.")
        return

    info_clear(self.info.entries)

    for i, entry in enumerate(self.info.entries, 1):
        if type(entry) == ctk.CTkEntry:
            entry.insert(0, row[i])
        elif type(entry) == ctk.CTkOptionMenu:
            entry.set(row[i])

def db_deleterow(self, rows_to_delete):
    if not self.db.cnx:
        messagebox.showerror("", "Conéctese a una base de datos primero")
        return

    if not rows_to_delete:
        messagebox.showerror("Error", "No se han encontrado equipos a eliminar.")
        return

    deleted_rows = []

    for row in rows_to_delete:
        try:
            serial = self.table.item(row)["values"][4]
            if not serial:
                messagebox.showwarning("Añadir serial", "Añada el serial del equipo para eliminarlo")
                continue

            affected_row = push_query(self.db,
                        "DELETE FROM `equipos` WHERE serial= %s", params=[serial])

            if not affected_row:
                logger.error("Tried to remove device with serial: %s, but it was not found in the database", serial)
                messagebox.showerror("Error", "No se ha encontrado el equipo con el serial seleccionado")

        except mysql.connector.Error as err:
            messagebox.showerror("", f"Sucedió el siguiente error: {err}")

        except Exception as err:
            logger.error("Error while trying to remove device from database", exc_info=True)
            messagebox.showerror("Error", f"Sucedió el siguiente error: {err}")
        else:
            deleted_rows.append(serial)
            logger.info("Device with serial: %s has been removed", serial)

    if deleted_rows:
        messagebox.showinfo("", f"Los siguientes equipos se han eliminado correctamente: {", ".join(deleted_rows)}")

    else:
        messagebox.showwarning("", "No se ha podido eliminar ningún equipo")

    db_showentries(self)
    info_clear(self.info.entries)
    if not self.table.hidden:
        self.table.hide_show_dbinfo()

def db_search(self, strict):
    if not self.db.cnx:
        messagebox.showerror("", "Conéctese a una base de datos primero")
        return

    search = self.table.search_bar.get()
    filter_s = LABEL_CONVERSION[self.table.search_filter.get()]

    if search == "":
        db_showentries(self)
        return

    try:
        search_query = f"SELECT * FROM `equipos` WHERE {filter_s} LIKE "
        strict_str = f"'{search}'"
        non_strict_str = f"'%{search}%'"

        if strict:
            search_query += strict_str
        else:
            search_query += non_strict_str

        affected_rows = push_query(self.db,
                                    search_query,
                                    fetch=True)

        if not affected_rows:
            self.table.delete(*self.table.get_children())
            self.table.insert("", "end", values=["" for i in range(len(LABELS)+1)])
            self.table.tree_label.configure(text=f"Total de equipos: 0")
            return

        db_showentries(self, affected_rows)

    except Exception as err:
        logger.error("Error while trying to search in the DeskBase table", exc_info=True)
        messagebox.showerror("Error", f"Error: {err}")
