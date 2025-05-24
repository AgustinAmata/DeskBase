LABELS = [
    "Tipo*", "Marca*", "Modelo*", "Serial*", 
    "Fecha de Adquisición", "Estado",
    "Ubicación", "Sistema Operativo", "Modelo CPU", "Modelo Placa Base",
    "Tarjeta Gráfica", "Modelo Tarjeta Gráfica", "RAM Tarjeta Gráfica (GB)",
    "Tipo de Almacenamiento", "Capacidad de Almacenamiento (GB)", "Memoria RAM",
    "Capacidad de RAM (GB)", "Última modificación por", "Fecha última modificación"
]

TABLE_LABELS = [
                "nombre", "marca", "modelo", "serial", "fecha_adquisicion", "estado",
                "ubicacion", "sistema_operativo", "modelo_cpu", "modelo_placa_base",
                "tarjeta_grafica", "modelo_tarjeta_grafica", "ram_tarjeta", "tipo_almacenamiento",
                "capacidad_almacenamiento", "memoria_ram", "capacidad_ram"
]

NUMERIC_LABELS = [
    "RAM Tarjeta Gráfica (GB)",
    "Capacidad de Almacenamiento (GB)",
    "Capacidad de RAM (GB)"
]

LABEL_CONVERSION = {LABELS[i]:TABLE_LABELS[i] for i in range(len(LABELS)-2)}

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

#First item -> x axis, second item -> y axis
PLOT_OPTIONS = {
    "Cantidad total de equipos por tipo": ["nombre", ""],
    "Distribución de equipos por marca": ["marca", ""],
    "Cantidad de equipos por ubicación": ["ubicacion", ""],
    "Distribución de equipos por estado": ["estado", ""],
    "Número de equipos por antigüedad": ["fecha_adquisicion", ""],
    "Número de equipos por sistema operativo": ["sistema_operativo", ""]
}

RESTRICTION_CONDITIONS = {
    "que contenga:": " LIKE '%{value}%'",
    "que sea exacto a:": " LIKE '{value}'",
    "que no contenga:": " NOT LIKE '%{value}%'",
    "que no sea exacto a:": " NOT LIKE '{value}'",
    "mayor que:": " > '{value}'",
    "mayor o igual que:": " >= '{value}'",
    "menor que:": " < '{value}'",
    "menor o igual que:": " <= '{value}'",
    "igual que:": " = '{value}'"
}

TABLE_CREATION = f'''CREATE TABLE equipos (
                    `id` INTEGER AUTO_INCREMENT,
                    `nombre` VARCHAR(255),
                    `marca` VARCHAR(255),
                    `modelo` VARCHAR(255),
                    `serial` VARCHAR(255) UNIQUE,
                    `fecha_adquisicion` DATE,
                    `estado` VARCHAR(255),
                    `ubicacion` VARCHAR(255),
                    `sistema_operativo` VARCHAR(255),
                    `modelo_cpu` VARCHAR(255),
                    `modelo_placa_base` VARCHAR(255),
                    `tarjeta_grafica` VARCHAR(255),
                    `modelo_tarjeta_grafica` VARCHAR(255),
                    `ram_tarjeta` INTEGER DEFAULT 0,
                    `tipo_almacenamiento` VARCHAR(255),
                    `capacidad_almacenamiento` INTEGER,
                    `memoria_ram` VARCHAR(255),
                    `capacidad_ram` INTEGER,
                    `usuario_ultima_mod` VARCHAR(255) DEFAULT (USER()),
                    `fecha_ultima_mod` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB;
                    
                    DELIMITER //
                    CREATE TRIGGER equipos_before_update
                    BEFORE UPDATE ON equipos
                    FOR EACH ROW
                    BEGIN
                        SET NEW.usuario_ultima_mod = USER();
                    END;
                    //
                    DELIMITER;'''

ADD_ENTRY = '''INSERT INTO `equipos`
               (`nombre`, `marca`, `modelo`, `serial`,
               `fecha_adquisicion`, `estado`, `ubicacion`,
               `sistema_operativo`, `modelo_cpu`,
               `modelo_placa_base`, `tarjeta_grafica`,
               `modelo_tarjeta_grafica`, `ram_tarjeta`,
               `tipo_almacenamiento`, `capacidad_almacenamiento`,
               `memoria_ram`, `capacidad_ram`)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

UPDATE_ENTRY = '''UPDATE `equipos` SET
        {update_vals}
        WHERE `id`=%s
'''

TEST_QUERIES = {
                "SELECT": r"(SELECT(,| ON )).*((\*.\*)|((|`){db_name}(|`).\*))",
                "CREATE": r"(CREATE(,| ON)).*((\*.\*)|((|`){db_name}(|`).\*))",
                "UPDATE": r"(UPDATE(,| ON)).*((\*.\*)|((|`){db_name}(|`).\*))",
                "DELETE": r"(DELETE(,| ON)).*((\*.\*)|((|`){db_name}(|`).\*))",
                "INSERT": r"(INSERT(,| ON)).*((\*.\*)|((|`){db_name}(|`).\*))"
                }