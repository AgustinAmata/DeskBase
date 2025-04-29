LABELS = [
    "Tipo*", "Marca*", "Modelo*", "Serial*", 
    "Fecha de Adquisición", "Estado",
    "Ubicación", "Sistema Operativo", "Modelo Placa Base", "Tarjeta Gráfica",
    "Tipo de Almacenamiento", "Capacidad de Almacenamiento", "Memoria RAM", "Capacidad de RAM"
]

TABLE_LABELS = ["nombre", "marca", "modelo", "serial", "fecha_adquisicion", "estado",
                "ubicacion", "sistema_operativo", "modelo_placa_base", "tarjeta_grafica",
                "tipo_almacenamiento", "capacidad_almacenamiento", "memoria_ram", "capacidad_ram"]

LABEL_CONVERSION = {LABELS[i]:TABLE_LABELS[i] for i in range(14)}

TREE_TAGS = {"Operativo": "operativo", "En reparación": "reparacion",
             "En reparacion": "reparacion", "Baja": "baja"}

MARCAS = ["HP", "Dell", "Lenovo", "Asus", "Acer", "Apple", "MSI", "Otro"]

SISTEMAS_OPERATIVOS = ["Windows", "Linux", "MacOS", "ChromeOS", "Otro"]

TIPOS_ALMACENAMIENTO = ["HDD", "SSD", "M2", "NVMe", "Otro"]

TIPOS_RAM = ["DDR", "DDR2", "DDR3", "DDR4", "DDR5", "Otro"]

TIPO_GRAFICA = ["Integrada", "Dedicada"]

ESTADOS = ["Operativo", "En reparación", "En mantenimiento", "Baja", "Reserva"]

RULETA = {"Marca*": MARCAS, "Sistema Operativo": SISTEMAS_OPERATIVOS, "Tarjeta Gráfica": TIPO_GRAFICA,
          "Tipo de Almacenamiento": TIPOS_ALMACENAMIENTO, "Memoria RAM": TIPOS_RAM, "Estado": ESTADOS}

TABLE_CREATION = f'''CREATE TABLE equipos (
                    `id` INTEGER AUTO_INCREMENT,
                    `nombre` VARCHAR(255),
                    `marca` VARCHAR(255),
                    `modelo` VARCHAR(255),
                    `serial` VARCHAR(255) UNIQUE,
                    `fecha_adquisicion` VARCHAR(255),
                    `estado` VARCHAR(255),
                    `ubicacion` VARCHAR(255),
                    `sistema_operativo` VARCHAR(255),
                    `modelo_placa_base` VARCHAR(255),
                    `tarjeta_grafica` VARCHAR(255),
                    `tipo_almacenamiento` VARCHAR(255),
                    `capacidad_almacenamiento` VARCHAR(255),
                    `memoria_ram` VARCHAR(255),
                    `capacidad_ram` VARCHAR(255),
                    PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB'''

ADD_ENTRY = '''INSERT INTO `equipos`
               (`nombre`, `marca`, `modelo`, `serial`,
               `fecha_adquisicion`, `estado`, `ubicacion`,
               `sistema_operativo`, `modelo_placa_base`,
               `tarjeta_grafica`, `tipo_almacenamiento`,
               `capacidad_almacenamiento`, `memoria_ram`,
               `capacidad_ram`)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

UPDATE_ENTRY = '''UPDATE `equipos` SET
        nombre=%s,
        marca=%s,
        modelo=%s,
        serial=%s,
        fecha_adquisicion=%s,
        estado=%s,
        ubicacion=%s,
        sistema_operativo=%s,
        modelo_placa_base=%s,
        tarjeta_grafica=%s,
        tipo_almacenamiento=%s,
        capacidad_almacenamiento=%s,
        memoria_ram=%s,
        capacidad_ram=%s
        WHERE `id`=%s
'''