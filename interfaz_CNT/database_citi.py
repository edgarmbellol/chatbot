# app/database.py
# En este archivo se pasaran las consultas a la base de datos
import pyodbc
from interfaz_CNT.config import SQL_SERVER, SQL_DATABASE, SQL_USERNAME, SQL_PASSWORD
# from interfaz_CNT.config import SQL_SERVER, SQL_DATABASE, SQL_USERNAME, SQL_PASSWORD

def obtener_conexion():
    conn_str = (
        f'DRIVER={{SQL Server}};'
        f'SERVER={SQL_SERVER};'
        f'DATABASE={SQL_DATABASE};'
        f'UID={SQL_USERNAME};'
        f'PWD={SQL_PASSWORD};'
    )
    return pyodbc.connect(conn_str)

def paciente_por_cedula(cedula):
    try:
        # Conexión a la base de datos
        conn = obtener_conexion()
        cursor = conn.cursor()

        # Ejecutar el procedimiento almacenado
        cursor.execute("EXEC BuscarPacientePorCedula @Cedula = ?", cedula)

        # Obtener todas las filas
        rows = cursor.fetchall()

        # Si no se encuentran datos
        if not rows:
            return []

        # Convertir las filas en una lista de diccionarios
        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        # Cerrar la conexión
        cursor.close()
        conn.close()

        return result

    except Exception as e:
        print(f"Error al buscar el paciente: {e}")
        return []
    

def tomar_nombre_usuario(lista):
    # Tomar los campos necesarios
    persona = lista[0]
    nombre_completo = f"{persona['DE_PRAP_PAC'].strip()} {persona['DE_SGAP_PAC'].strip()} {persona['NO_NOMB_PAC'].strip()} {persona['NO_SGNO_PAC'].strip()}"

    print(nombre_completo)
    return nombre_completo



# --------------------------------------------------------

def ejecutar_consulta(query,ad):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(query,ad)
    rows = cursor.fetchall()
    conn.close()
    return rows

# FUNCION PARA ACTUALIZAR POR NUMERO DE URGENCIA U HOSPITALIZACION
def actualizar_admision(query,Cantidad,Consumido,Cobrable,admision,HistClin,NOrden,Consecutivo,CProced):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(query,(Cantidad,Consumido,Cobrable,admision,HistClin,NOrden,Consecutivo,CProced))
    conn.commit()
    conn.close()

# Función para ejecutar un procedimiento almacenado que no devuelve resultados
def ejecutar_procedimiento(query, params):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return "Proceso Exitoso"
    except Exception as e:
        return f"Error al ejecutar el procedimiento: {str(e)}"
    finally:
        if conn:
            conn.close()

# Función para ejecutar un procedimiento almacenado que devuelve resultados
def ejecutar_procedimiento_con_resultados(query, params):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

# FUNCION PARA VERIFICAR SI ES UN USUARIO AUTORIZADO
def autenticacion(query,usuario):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(query,(usuario))
    # FUNCION PARA TOMAR SOLO LA PRIMERA COLUMNA
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    return row

# Funcion para ejecutar insert en base de datos
def insertar_con_resultado(query, params):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(query,(params))
    # FUNCION PARA TOMAR SOLO LA PRIMERA COLUMNA
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    return row