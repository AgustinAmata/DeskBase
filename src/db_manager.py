import mysql.connector
import logging
from tkinter import messagebox
from mysql.connector import errorcode
from src.constants import TABLE_CREATION
import time

logger = logging.getLogger(__name__)

class DBManager():
    def __init__(self):
        self.cnx = None
        self.cursor = None
        self.usr = ""
        self.pwrd = ""
        self.hst = ""
        self.db_name = ""

    def connect_to(self, usr, pwrd, hst, db_name):
        logger.info("Trying to establish connection with database '%s' at host '%s' with user '%s'", db_name, hst, usr)
        try:
            self.cnx = mysql.connector.connect(user=usr,
                                               password=pwrd,
                                               host=hst,
                                               database=db_name,
                                               connection_timeout=10)
            self.cursor = self.cnx.cursor()

            if not self.check_table_exists():
                logger.warning("DeskBase table not found in database. Waiting for user input")
                if messagebox.askyesno("", message="No existe la tabla necesaria para el inventariado. ¿Desea crearla?"):
                    logger.info("User decided to create DeskBase table at database %s", db_name)
                    if not self.create_table():
                        self.close_connection(show_msg=False)
                        return False
                else:
                    logger.info("User declined creating a DeskBase table. Connection to database aborted")
                    messagebox.showwarning("", "Introduzca otra base de datos")
                    return False

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.error("Database '%s' does not exist", db_name)
                messagebox.showerror("", f"La base de datos '{db_name}' no existe")
            elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger.error("Incorrect user or password")
                messagebox.showerror("", "El usuario o la contraseña son incorrectos")
            else:
                logger.exception("MySQL error during connection")
                messagebox.showerror("", f"Error de MySQL: {err}")
            return False

        except Exception as e:
            logger.exception("Unexpected error during database connection")
            messagebox.showerror("", f"Error inesperado: {e}")
            return False

        else:
            if not self.cnx.is_connected():
                logger.error("Connection to database '%s' could not be established", db_name)
                messagebox.showerror("", "No se ha podido conectar a la base de datos")
                return False

            self.usr, self.pwrd, self.hst, self.db_name = usr, pwrd, hst, db_name

            logger.info("Connection to database established")
            messagebox.showinfo("", "Conexión correcta a la base de datos")
            return True

    def create_table(self):
        try:
            self.cursor.execute(TABLE_CREATION)

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLEACCESS_DENIED_ERROR:
                logger.error("Permission denied to create table")
                messagebox.showerror("", "El usuario no tiene el permiso necesario para crear la tabla")
            else:
                logger.exception("MySQL error while creating table")
                messagebox.showerror("", f"Error de MySQL: {err}")
            return False

        except Exception as err:
            logger.exception("Unexpected exception while creating DeskBase table")
            messagebox.showerror("", f"Error inesperado: {err}")
            return False

        else:
            logger.info("DeskBase table created")
            messagebox.showinfo("", "Tabla 'equipos' creada")
            return True

    def check_table_exists(self):
        self.cursor.execute("SHOW TABLES")
        result = [True for item in self.cursor.fetchall() if item[0] == "equipos"]
        return result

    def close_connection(self, show_msg=True):
        if self.cnx:
            self.cnx.close()
            self.cnx = None
            self.cursor = None
            self.usr = self.pwrd = self.hst = self.db_name = ""
            if show_msg:    
                logger.warning("Closed connection to database")
                messagebox.showinfo("", "Se ha cortado la conexión con la base de datos")
        else:
            messagebox.showinfo("", "No hay una base de datos conectada")

    def reconnect(self):
        self.cnx.close()
        logger.warning("Closed connection to database")
        self.connect_to(self.usr, self.pwrd, self.hst, self.db_name)

def push_query(db: DBManager, query, params=None, fetch=False):
    logger.info("Trying to send query \n%s\n with params: \n%s\nand fetch=%s", query, params, fetch)
    for n_try in range(5):
        try:
            if db.cnx is None:
                messagebox.showwarning("", "Establezca primero una conexión con una base de datos")
                return

            db.cursor.execute(query, params)
            logger.info("Executed query in database: \n%s", db.cursor.statement)

            if fetch:
                c_fetch = list(db.cursor.fetchall())
                db.cnx.commit()
                return c_fetch
            else:
                c_row = db.cursor.rowcount
                db.cnx.commit()
                return c_row

        except mysql.connector.Error as err:
            logger.error("Error while trying to send a query to database", exc_info=True)
            if "database is locked" in str(err):
                time.sleep(0.5)
                if db.cnx:
                    try:
                        logger.warning("Trying to reconnect to database to send a query")
                        db.cnx.reconnect()
                        logger.warning("Reconnected to database")
                    except:
                        pass

            else:
                logger.error("Error while trying to send a query to database", exc_info=True)
                raise err
            
        except Exception as err:
            logger.error("Error while trying to send a query to database", exc_info=True)
            raise err

    logger.error("Query to database could not be sent after multiple attempts")
    raise Exception("No se pudo acceder a la base de datos después de múltiples intentos")