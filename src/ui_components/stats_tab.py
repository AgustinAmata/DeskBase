import customtkinter as ctk
import matplotlib.pyplot as plt
import tkinter as tk
import calendar
import json
import os
from datetime import datetime
from pathlib import Path
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from tkinter import ttk
from tkinter import messagebox
from src.db_manager import DBManager, push_query
from src.constants import LABELS, RESTRICTION_CONDITIONS, NUMERIC_LABELS, RULETA, PLOT_OPTIONS, LABEL_CONVERSION
from src.create_plot import generate_plot

class StatsTab(ctk.CTkTabview):
    def __init__(self, master: ctk.CTkFrame, db: DBManager, main_win: ctk.CTk):
        super().__init__(master, anchor="s", border_width=2)
        self._segmented_button.configure(border_width=7, corner_radius=20)
        self.master = master
        self.db = db
        self.main_win = main_win

        self.fig_create_frame = self.add("Crear")
        self.fig_history_frame = self.add("Historial")
        self.fig_view_frame =self.add("Vista")
        self.fig_view = FigView(self.fig_view_frame, self.db, self.main_win)
        self.fig_history = FigHistory(self.fig_history_frame, self.db, self.main_win, self.fig_view, self)
        self.fig_create = FigCreate(self.fig_create_frame, self.db, self.main_win, self.fig_view, self)

        self.pack(fill="both", expand=True)

class FigView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame, db: DBManager, main_win: ctk.CTk):
        self.master = master
        self.db = db
        self.main_win = main_win

        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        self.axes_list = []
        self.fig, ax = plt.subplots()
        self.axes_list.append(ax)
        self.axes_list[0].spines["top"].set_visible(False)
        self.axes_list[0].spines["right"].set_visible(False)
        self.fig_canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.fig_canvas.draw()
        self.fig_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.toolbar_frame = ctk.CTkFrame(self.master)
        self.toolbar = NavigationToolbar2Tk(self.fig_canvas, self.toolbar_frame)
        self.toolbar_frame.grid(row=1, column=0)

class FigCreate(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame, db: DBManager, main_win: ctk.CTk, fig_view, stats_tab):
        self.master = master
        self.db = db
        self.main_win = main_win
        self.fig_view = fig_view
        self.stats_tab = stats_tab

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=4)
        self.master.grid_rowconfigure(2, weight=2)
        self.master.grid_columnconfigure(0, weight=1)

        self.int_entries = {}
        self.entries_error_msgs = {}

        self.plots_type_frame = ctk.CTkFrame(self.master)
        self.plots_type_frame.grid_columnconfigure([0,1], weight=1)
        self.plot_select_label = ctk.CTkLabel(self.plots_type_frame, text="Tipo de estadística:")
        self.plot_opts = ctk.CTkOptionMenu(self.plots_type_frame, values=[""]+list(PLOT_OPTIONS.keys()), command= lambda choice: self.is_plot_selected(choice))
        self.plot_select_label.grid(row=0, column=0, sticky="e", padx=(0,5))
        self.plot_opts.grid(row=0, column=1, sticky="w")
        self.plots_type_frame.grid(row=0, column=0, sticky="sew")

        self.restr_frame = ctk.CTkFrame(self.master)
        # self.restr_error_msg = ctk.CTkLabel(self.restr_frame, text="", fg_color="red", corner_radius=6)
        self.restr_frame.grid_columnconfigure([i for i in range(6)], weight=1)
        self.restr_frame.grid_rowconfigure(0, weight=1)
        self.restr_frame.grid_rowconfigure([1,2,3], weight=1)
        self.restr_label = ctk.CTkLabel(self.restr_frame, text="Restricciones", font=(ctk.CTkFont, 18, "bold"))
        self.restr_label.grid(row=0, column=0, columnspan=6, sticky="s")
        self.restr_groups_list = {}

        for i in range(6):
            opts = ctk.CTkOptionMenu(self.restr_frame, values=[""] + LABELS[:-1], state="disabled")
            opts.configure(command= lambda c, w=opts: self.select_restr_opts(c, w))
            conds = ctk.CTkOptionMenu(self.restr_frame, values=[""], state="disabled")
            params = ctk.CTkEntry(self.restr_frame, state="disabled")
            opts.grid(row=i%3+1, column=(i//3)*3, sticky="ew", padx=(10,2))
            conds.grid(row=i%3+1, column=(i//3)*3+1, sticky="ew", padx=(0,2))
            params.grid(row=i%3+1, column=(i//3)*3+2, sticky="w")
            self.restr_groups_list[opts] = [conds, params]

        self.restr_frame.grid(row=1, column=0, sticky="nsew")

        self.main_bttns_frame = ctk.CTkFrame(self.master)
        self.main_bttns_frame.grid_columnconfigure([0,1], weight=1)
        self.create_plot_bttn = ctk.CTkButton(self.main_bttns_frame, text="Crear figura", state="disabled", command=lambda: self.check_and_validate())
        self.clear_conf_bttn = ctk.CTkButton(self.main_bttns_frame, text="Limpiar campos", command=lambda: self.clear_conf(), state="disabled")
        self.create_plot_bttn.grid(row=0, column=0, sticky="e", padx=(0,5))
        self.clear_conf_bttn.grid(row=0, column=1, sticky="w", padx=(5,0))
        self.main_bttns_frame.grid(row=2, column=0, sticky="ew")

    def select_restr_opts(self, choice, widget):
        old_params = self.restr_groups_list[widget][1]
        par_grid_info = old_params.grid_info()
        self.restr_groups_list[widget].pop().destroy()
        conds = self.restr_groups_list[widget][0]

        if choice not in NUMERIC_LABELS and widget in self.int_entries.keys():
            self.int_entries.pop(widget)
            self.entries_error_msgs.pop(old_params)

        if choice not in RULETA:
            params = ctk.CTkEntry(self.restr_frame, state="normal")
            if not choice:
                conds.configure(values=[""], state= "disabled")
                params.configure(state="disabled")

            elif choice in NUMERIC_LABELS + ["Fecha de Adquisición"]:
                if choice in NUMERIC_LABELS:
                    msg = "Solo números"
                else:
                    msg= "aaaa-mm o aaaa"

                conds.configure(values=list(RESTRICTION_CONDITIONS.keys())[4:], state="normal")
                self.int_entries[widget] = False
                self.entries_error_msgs[params] = ctk.CTkLabel(self.restr_frame, text=msg, fg_color="red", corner_radius=6)

            else:
                conds.configure(values=list(RESTRICTION_CONDITIONS.keys())[:4], state="normal")

        else:
            conds.configure(values=list(RESTRICTION_CONDITIONS.keys())[1:4:2], state="normal")
            params = ctk.CTkOptionMenu(self.restr_frame, values=RULETA[choice])

        conds.set(conds._values[0])
        params.grid(**par_grid_info)
        self.restr_groups_list[widget].append(params)

    def clear_conf(self):
        self.plot_opts.set(self.plot_opts._values[0])
        for box in self.restr_groups_list.keys():
            box.set("")
            box.configure(state="disabled")
            self.select_restr_opts("", box)
        self.create_plot_bttn.configure(state="disabled")
        self.clear_conf_bttn.configure(state="disabled")

    def is_plot_selected(self, choice):
        if not choice:
            for box in self.restr_groups_list.keys():
                box.set(box._values[0])
                box.configure(state="disabled")
                self.select_restr_opts("", box)
            self.create_plot_bttn.configure(state="disabled")

        else:
            for box in self.restr_groups_list.keys():
                box.configure(state="normal")
            self.create_plot_bttn.configure(state="normal")
            self.clear_conf_bttn.configure(state="normal")

    def check_and_validate(self):
        invalid_entries = []

        for choice in self.int_entries.keys():
            entry = self.restr_groups_list[choice][1]
            is_valid = True
            if choice.get() in NUMERIC_LABELS:
                is_valid = entry.get().isdigit()
            else:
                try:
                    if len(entry.get()) == 4:
                        datetime.strptime(entry.get(), "%Y")
                    elif len(entry.get()) == 7:
                        datetime.strptime(entry.get(), "%Y-%m")
                    else:
                        is_valid = False
                except:
                    is_valid = False

            if not is_valid:
                self.int_entries[choice] = False
                entry.configure(border_color="red")
                invalid_entries.append(entry)
            else:
                self.int_entries[choice] = True
                entry.configure(border_color=ctk.ThemeManager.theme["CTkEntry"]["border_color"])
                self.entries_error_msgs[entry].place_forget()

        if invalid_entries != []:
            for invalid_entry in invalid_entries:
                error_msg = self.entries_error_msgs[invalid_entry]
                y = invalid_entry._current_height*1.5
                error_msg.place(in_=invalid_entry, relx=0.5, y=y, anchor="center", relwidth=1)
                error_msg.lift()
            return

        cols = PLOT_OPTIONS[self.plot_opts.get()]
        query = f"SELECT `id`, {"".join(cols)} FROM `equipos`"

        restrictions = {k: v for k, v in self.restr_groups_list.items() if k.get() != ""}

        if restrictions:
            query += " WHERE "

        for choice, (conds, params) in restrictions.items():
            conds_str = RESTRICTION_CONDITIONS[conds.get()]
            params_str = params.get()

            if choice.get() == "Última modificación por":
                query += "`usuario_ultima_mod`"
            elif choice.get() == "Fecha de Adquisición":
                if " = " in conds_str:
                    if len(params_str) == 4:
                        date_1 = f"{params_str}-01-01"
                        date_2 = f"{params_str}-12-31"
                    elif len(params_str) == 7:
                        y, m = params_str.split("-")
                        last_day = calendar.monthrange(int(y), int(m))[1]
                        date_1 = f"{params_str}-01"
                        date_2 = f"{params_str}-{last_day}"

                    conds_str = " BETWEEN '{date_1}' AND '{date_2}'".format(date_1=date_1, date_2=date_2)
                
                if len(params_str) == 4 and not " = " in conds_str:
                    if "< " in conds_str or ">=" in conds_str:
                        params_str += "-01-01"
                    elif "> " in conds_str or "<=" in conds_str:
                        params_str += "-12-31"

                elif len(params_str) == 7 and not " = " in conds_str:
                    if "< " in conds_str or ">=" in conds_str:
                        params_str += "-01"
                    elif "> " in conds_str or "<=" in conds_str:
                        y, m = params_str.split("-")
                        last_day = calendar.monthrange(int(y), int(m))[1]
                        params_str += f"-{last_day}"

                query += f"`{LABEL_CONVERSION[choice.get()]}`"

            else:
                query += f"`{LABEL_CONVERSION[choice.get()]}`"
                
            query += conds_str.format(value=params_str) + " AND "
        else:
            query = query.strip(" AND ")

        if push_query(self.db, query, fetch=True):
            generate_plot(self.plot_opts.get(), query, self.db, self.fig_view)
            self.stats_tab.fig_history.add_histentry(self.plot_opts.get(), restrictions, query)
            self.stats_tab.set("Vista")
        else:
            messagebox.showerror("", "No se han podido encontrar datos con las restricciones impuestas.")
            
class FigHistory(ctk.CTkFrame, ttk.Treeview):
    def __init__(self, master: ctk.CTkFrame, db: DBManager, main_win: ctk.CTk, fig_view, stats_tab):
        self.master = master
        self.db = db
        self.main_win = main_win
        self.fig_view = fig_view
        self.stats_tab = stats_tab

        self.master.grid_columnconfigure(0, weight=8)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        self.hist_entries = []

        self.history_frame = ctk.CTkFrame(self.master)
        self.history_frame.columnconfigure(0, weight=1)
        self.history_frame.rowconfigure(0,weight=1)
        self.hist_scrollbar_y = ctk.CTkScrollbar(self.history_frame, command=self.yview)
        self.hist_scrollbar_x = ctk.CTkScrollbar(self.history_frame, orientation="horizontal", command=self.xview)

        self.history = ttk.Treeview(self.history_frame,
                                    show="headings",
                                    columns=["Tipo de estadística", "Restricciones"],
                                    yscrollcommand=self.hist_scrollbar_y.set,
                                    xscrollcommand=self.hist_scrollbar_x.set)
        self.history.heading("Tipo de estadística", text="Tipo de estadística", command= lambda c="Tipo de estadística": self.col_sort(c, False))
        self.history.column("Tipo de estadística", width=400, minwidth=400, anchor="center", stretch=False)
        self.history.heading("Restricciones", text="Restricciones", command= lambda c="Restricciones": self.col_sort(c, False))
        self.history.column("Restricciones", width=400, minwidth=400, anchor="center", stretch=True)

        self.hist_scrollbar_x.grid(row=1, column=0, sticky="new")
        self.hist_scrollbar_y.grid(row=0, column=1, sticky="nse")
        self.history.grid(row=0, column=0, sticky="nsew")
        self.history_frame.grid(row=0, column=0, sticky="nsew")

        self.bttns_frame = ctk.CTkFrame(self.master)
        self.bttns_frame.grid_columnconfigure(0, weight=1)
        self.bttns_frame.grid_rowconfigure([0,1,2,3], weight=1)
        self.bttns_frame.grid_rowconfigure(4, weight=8)
        self.create_plot_bttn = ctk.CTkButton(self.bttns_frame, text="Crear figura", state="disabled", command=lambda: self.parse_and_create_plot())
        self.delete_histentry_bttn = ctk.CTkButton(self.bttns_frame, text="Eliminar entrada", state="disabled", command=lambda: self.delete_histentry())
        self.modify_histentry_bttn = ctk.CTkButton(self.bttns_frame, text="Modificar entrada", state="disabled", command=lambda: self.modify_histentry())
        self.hist_up = ctk.CTkButton(self.bttns_frame, text="Entrada anterior", state="disabled", command=lambda: self.entry_up())
        self.hist_down = ctk.CTkButton(self.bttns_frame, text="Siguiente entrada", state="disabled", command=lambda: self.entry_down())
        self.history.bind("<<TreeviewSelect>>", lambda e: self.select_histentry())
        self.main_win.bind("<Up>", lambda e: self.entry_up())
        self.main_win.bind("<Down>", lambda e: self.entry_down())
        self.create_plot_bttn.grid(row=0, column=0, pady=(50,0))
        self.delete_histentry_bttn.grid(row=1, column=0, sticky="s")
        self.modify_histentry_bttn.grid(row=2, column=0, sticky="n")
        self.hist_up.grid(row=3, column=0, sticky="s")
        self.hist_down.grid(row=4, column=0, sticky="n")
        self.bttns_frame.grid(row=0, column=1, sticky="nsew", rowspan=2)

        self.entryview_frame = ctk.CTkFrame(self.master)
        self.entryview_frame.grid_columnconfigure(0, weight=1)
        self.entryview_frame.grid_rowconfigure(0, weight=1)
        self.entryview = ctk.CTkTextbox(self.entryview_frame, state="disabled")
        self.entryview.grid(row=0, column=0, sticky="nsew")
        self.entryview_frame.grid(row=1, column=0, sticky="nsew")

        if Path("./DeskBase_history.json").exists():
            self.read_json_hist()
        else:
            json_filepath = "./DeskBase_history.json"
            Path(json_filepath).touch()
            with open(json_filepath, "r+", encoding="utf-8") as json_file:
                json_file.write("[\n\n]")

    def read_json_hist(self):
        with open("./DeskBase_history.json", encoding="utf-8") as json_file:
            self.hist_entries = json.load(json_file)

        if not self.hist_entries:
            return

        for i, entry in enumerate(self.hist_entries):
            fig = entry["plot_option"]
            restrictions = [" ".join(fields) for fields in entry["restrictions"]]
            self.history.insert("", "end", values=[fig, ", ".join(restrictions)], iid=i)

        self.is_hist_empty()

    def is_hist_empty(self):
        if not self.history.get_children():
            for child in self.bttns_frame.winfo_children():
                if type(child) == ctk.CTkButton:
                    child.configure(state="disabled")
        else:
            for child in self.bttns_frame.winfo_children():
                if type(child) == ctk.CTkButton:
                    child.configure(state="normal")

    def add_histentry(self, plot_opt, restrictions, query):
        restr_entries = []

        for choice, (conds, params) in restrictions.items():
            restr_entries.append([choice.get(), conds.get(), params.get()])

        json_dict = {"plot_option": plot_opt, "restrictions": restr_entries, "query": query}

        if json_dict in self.hist_entries:
            return

        with open("./DeskBase_history.json", mode="r+") as json_file:
            pos = json_file.seek(0, os.SEEK_END)
            json_file.seek(pos-3)
            if len(self.hist_entries) != 0:
                json_file.write(", \n")
            json.dump(json_dict, json_file, indent=2)
            json_file.write("\n]")

        self.hist_entries.append(json_dict)
        str_restrs = [" ".join(entry) for entry in restr_entries]
        self.history.insert("", "end", values=[plot_opt, ", ".join(str_restrs)], iid=len(self.hist_entries)-1)
        self.is_hist_empty()

    def select_histentry(self):
        rows = self.history.selection()
        self.entryview.configure(state="normal")
        if len(rows) != 1:
            self.entryview.delete("0.0", "end")
            self.entryview.configure(state="disabled")
            return
        
        self.entryview.delete("0.0", "end")

        entry = self.history.set(rows[0])
        for col, item in entry.items():
            if col == "Restricciones" and item:
                self.entryview.insert("end", text=col+":\n"+"\n".join(item.split(", ")))
            elif col == "Tipo de estadística":
                self.entryview.insert("end", text=col+":\n"+item+"\n\n")
        self.entryview.configure(state="disabled")

    def delete_histentry(self):
        rows = self.history.selection()
        if not rows or len(rows) != 1:
            messagebox.showwarning("", "Seleccione una entrada para eliminar")
            return

        confirm_msg = "¿Desea eliminar la entrada seleccionada?"
        if messagebox.askyesno("", confirm_msg):
            row_id = int(rows[0])
            self.hist_entries.pop(row_id)
            self.history.delete(rows[0])

            if len(self.hist_entries) == 0:
                return

            self.history.delete(*self.history.get_children())
            for i in range(len(self.hist_entries)):
                fig = self.hist_entries[i]["plot_option"]
                restrictions = [" ".join(fields) for fields in self.hist_entries[i]["restrictions"]]
                self.history.insert("", "end", values=[fig, ", ".join(restrictions)], iid=i)

            with open("./DeskBase_history.json", mode="w") as json_file:
                json.dump(self.hist_entries, json_file, indent=2)

    def modify_histentry(self):
        rows = self.history.selection()
        if not rows or len(rows) != 1:
            messagebox.showwarning("", "Seleccione una entrada para modificar")
            return

        row_dict = self.hist_entries[int(rows[0])]

        fig_create = self.stats_tab.fig_create
        fig_create.clear_conf()
        fig_create.plot_opts.set(row_dict["plot_option"])
        fig_create.is_plot_selected(row_dict["plot_option"])

        for widget, (choice, conds, params), i in zip(fig_create.restr_groups_list,
                                                     row_dict["restrictions"],
                                                     range(len(row_dict["restrictions"]))):
            widget.set(choice)
            fig_create.select_restr_opts(choice, widget)
            for wid, val in zip(fig_create.restr_groups_list[widget], [conds, params]):
                if type(wid) == ctk.CTkOptionMenu:
                    wid.set(val)
                elif type(wid) == ctk.CTkEntry:
                    wid.insert(0, val)

        self.stats_tab.set("Crear")

    def parse_and_create_plot(self):
        rows = self.history.selection()
        if not rows or len(rows) != 1:
            messagebox.showwarning("", "Seleccione una entrada para crear una figura")
            return

        row_dict = self.hist_entries[int(rows[0])]

        if push_query(self.db, row_dict["query"], fetch=True):
            generate_plot(row_dict["plot_option"], row_dict["query"], self.db, self.fig_view)
            self.stats_tab.set("Vista")
        else:
            messagebox.showerror("", "No se han podido encontrar datos con las restricciones impuestas.")

    def col_sort(self, col, descending):
        col_ids = [(self.history.set(item, col), item) for item in self.history.get_children("")]

        if col in NUMERIC_LABELS:
            col_ids.sort(key=lambda x: int(x[0]), reverse=descending)
        else:
            col_ids.sort(reverse=descending)

        for i, (val, item) in enumerate(col_ids):
            self.history.move(item, "",index=i)

        self.history.heading(col, command= lambda: self.col_sort(col, not descending))

    def entry_up(self):
        children = self.history.get_children()
        if not self.master.winfo_ismapped() or children == []:
            return
        
        rows = self.history.selection()
        if rows:
            rows = rows[0]

        if not rows or rows == children[0]:
            self.history.selection_set(children[-1])
        else:
            self.history.selection_set(self.history.prev(rows))

    def entry_down(self):
        children = self.history.get_children()
        if not self.master.winfo_ismapped() or children == []:
            return
        
        rows = self.history.selection()
        if rows:
            rows = rows[0]

        if not rows or rows == children[-1]:
            self.history.selection_set(children[0])
        else:
            self.history.selection_set(self.history.next(rows))