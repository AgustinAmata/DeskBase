import mysql.connector
from mysql.connector import errorcode
import time

class DBManager():
    def __init__(self):
        self.cnx = None
        self.cursor = None

    def connect_to():
        pass

    def create_database():
        pass

    def check_db_exists():
        pass

    def close_connection():
        pass

def push_query(db: DBManager, query, params=None, fetch=False):
    for n_try in range(5):
        try:
            if db.cnx is None:
                db.connect_to()

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