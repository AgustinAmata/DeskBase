import mysql.connector
from tkinter import messagebox
from mysql.connector import errorcode
from src.constants import TABLE_CREATION
import time

class DBManager():
    def __init__(self):
        self.cnx = None
        self.cursor = None

    def connect_to(self, usr, pwrd, hst, db_name):
        try:
            self.cnx = mysql.connector.connect(user=usr,
                                               password=pwrd,
                                               host=hst,
                                               database=db_name,
                                               connection_timeout=10)
            self.cursor = self.cnx.cursor()
            if not self.check_db_exists():
                if messagebox.askyesno("", message="No existe la tabla necesaria para el inventariado. ¿Desea crearla?"):
                    self.create_table()
                else:
                    messagebox.showwarning("", "Introduzca otra base de datos")
                    return False

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                messagebox.showerror("", f"La base de datos '{db_name}' no existe")
            elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                messagebox.showerror("", "El usuario o la contraseña son incorrectos")
            else:
                messagebox.showerror("", err)
            return False

        else:
            if not self.cnx.is_connected():
                messagebox.showerror("", "No se ha podido conectar a la base de datos")
                return False
            
            messagebox.showinfo("", "Conexión correcta a la base de datos")
            return True

    def create_table(self):
        try:
            self.cursor.execute(TABLE_CREATION)
        except Exception as err:
            messagebox.showerror("", err)
        else:
            messagebox.showinfo("", "Tabla 'equipos' creada")

    def check_db_exists(self):
        self.cursor.execute("SHOW TABLES")
        result = [True for item in self.cursor.fetchall() if item[0] == "equipos"]
        return result

    def close_connection(self, show_msg=True):
        if self.cnx:
            self.cnx.close()
            self.cnx = None
            self.cursor = None
            if show_msg:    
                messagebox.showinfo("", "Se ha cortado la conexión con la base de datos")
        else:
            messagebox.showinfo("", "No hay una base de datos conectada")

def push_query(db: DBManager, query, params=None, fetch=False):
    for n_try in range(5):
        try:
            if db.cnx is None:
                messagebox.showwarning("", "Establezca primero una conexión con una base de datos")
                return

            db.cursor.execute(query, params)

            if fetch:
                c_fetch = list(db.cursor.fetchall())
                db.cnx.commit()
                return c_fetch
            else:
                c_row = db.cursor.rowcount
                db.cnx.commit()
                return c_row

        except mysql.connector.Error as err:
            if "database is locked" in str(err):
                time.sleep(0.5)
                if db.cnx:
                    try:
                        db.cnx.close()
                    except:
                        pass
                db.cnx = None
            else:
                raise err
            
        except Exception as err:
            raise err
        
    raise Exception("No se pudo acceder a la base de datos después de múltiples intentos")