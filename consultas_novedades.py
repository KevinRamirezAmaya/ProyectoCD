# ============================================================================
#  consultas_novedades.py
#  Consultas de análisis SOBRE LA TABLA DE HECHOS hecho_novedades
#  Sigue el mismo patrón que Notebooks/consultas.py del repositorio.
#  Cada consulta trae la SQL (para pd.read_sql) y su equivalente en pandas.
#  Colócalo en la carpeta del proyecto (donde está config.yml) y ejecútalo,
#  o copia bloque por bloque en un notebook.
# ============================================================================

import pandas as pd
import yaml
from sqlalchemy import create_engine

# ---------------------------------------------------------------------------
# 1) Conexión a la base de análisis (etl_process)
# ---------------------------------------------------------------------------
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

config_etl = config['ETL_PRO']

url = (
    f"{config_etl['drivername']}://"
    f"{config_etl['user']}:{config_etl['password']}@"
    f"{config_etl['host']}:{config_etl['port']}/"
    f"{config_etl['dbname']}"
)
etl_conn = create_engine(url)

# ---------------------------------------------------------------------------
# 2) Cargar las tablas que vamos a usar (para las versiones en pandas)
# ---------------------------------------------------------------------------
hecho_novedades = pd.read_sql_table('hecho_novedades', etl_conn)
dim_novedades   = pd.read_sql_table('dim_novedades',   etl_conn)
dim_mensajero   = pd.read_sql_table('dim_mensajero',   etl_conn)
dim_fecha       = pd.read_sql_table('dim_fecha',       etl_conn)

# Recordatorio del esquema de hecho_novedades (5 columnas):
#   key_novedad, key_dim_mensajero, key_trans_servicio,
#   key_dim_fecha_novedad, cantidad_novedades
# La medida a SUMAR siempre es cantidad_novedades (cada fila vale 1).


# ===========================================================================
#  CONSULTA 0 — Sanity check: ¿cuántas novedades hay en total?
#  (útil para arrancar la sustentación y validar que la tabla cargó)
# ===========================================================================
sql = """
SELECT
    COUNT(*)                    AS filas,
    SUM(cantidad_novedades)     AS total_novedades
FROM hecho_novedades;
"""
c0 = pd.read_sql(sql, etl_conn)
print("\n[0] Total de novedades")
print(c0)

# pandas equivalente:
c0_pd = pd.DataFrame({
    'filas': [len(hecho_novedades)],
    'total_novedades': [hecho_novedades['cantidad_novedades'].sum()]
})


# ===========================================================================
#  CONSULTA 1 — Novedades por GRUPO (la columna nueva grupo_novedad)
#  Es la consulta ESTRELLA: agrupa el texto libre en categorías legibles.
#  Necesita cruzar hecho_novedades -> dim_novedades por key_novedad.
# ===========================================================================
sql = """
SELECT
    dn.grupo_novedad,
    SUM(hn.cantidad_novedades) AS total_novedades
FROM hecho_novedades hn
JOIN dim_novedades dn
    ON hn.key_novedad = dn.key_novedad
GROUP BY dn.grupo_novedad
ORDER BY total_novedades DESC;
"""
c1 = pd.read_sql(sql, etl_conn)
print("\n[1] Novedades por grupo")
print(c1)

# pandas equivalente:
c1_pd = (
    hecho_novedades
    .merge(dim_novedades[['key_novedad', 'grupo_novedad']], on='key_novedad', how='left')
    .groupby('grupo_novedad')['cantidad_novedades'].sum()
    .sort_values(ascending=False)
    .reset_index(name='total_novedades')
)


# ===========================================================================
#  CONSULTA 2 — Novedades por TIPO (nombre del tipo de novedad)
#  'nombre' viene del catálogo mensajeria_tiponovedad dentro de dim_novedades.
# ===========================================================================
sql = """
SELECT
    dn.nombre AS tipo_novedad,
    SUM(hn.cantidad_novedades) AS total_novedades
FROM hecho_novedades hn
JOIN dim_novedades dn
    ON hn.key_novedad = dn.key_novedad
GROUP BY dn.nombre
ORDER BY total_novedades DESC;
"""
c2 = pd.read_sql(sql, etl_conn)
print("\n[2] Novedades por tipo (nombre)")
print(c2)


# ===========================================================================
#  CONSULTA 3 — Novedades por MES
#  Cruza hecho_novedades -> dim_fecha por key_dim_fecha_novedad.
#  Ojo: 'año' y 'nombre_mes' llevan tilde -> en Postgres se citan con comillas.
# ===========================================================================
sql = """
SELECT
    df.nombre_mes,
    SUM(hn.cantidad_novedades) AS total_novedades
FROM hecho_novedades hn
JOIN dim_fecha df
    ON hn.key_dim_fecha_novedad = df.key_fecha
GROUP BY df.nombre_mes, df.mes
ORDER BY df.mes;
"""
c3 = pd.read_sql(sql, etl_conn)
print("\n[3] Novedades por mes")
print(c3)

# pandas equivalente:
c3_pd = (
    hecho_novedades
    .merge(dim_fecha[['key_fecha', 'nombre_mes', 'mes']],
           left_on='key_dim_fecha_novedad', right_on='key_fecha', how='left')
    .groupby(['mes', 'nombre_mes'])['cantidad_novedades'].sum()
    .reset_index(name='total_novedades')
    .sort_values('mes')
)


# ===========================================================================
#  CONSULTA 4 — Novedades por DÍA DE LA SEMANA
#  Sirve para ver si hay más incidencias ciertos días.
# ===========================================================================
sql = """
SELECT
    df.nombre_dia,
    SUM(hn.cantidad_novedades) AS total_novedades
FROM hecho_novedades hn
JOIN dim_fecha df
    ON hn.key_dim_fecha_novedad = df.key_fecha
GROUP BY df.nombre_dia, df.dia_semana
ORDER BY df.dia_semana;
"""
c4 = pd.read_sql(sql, etl_conn)
print("\n[4] Novedades por día de la semana")
print(c4)


# ===========================================================================
#  CONSULTA 5 — Top 10 MENSAJEROS con más novedades
#  Cruza hecho_novedades -> dim_mensajero por key_dim_mensajero.
# ===========================================================================
sql = """
SELECT
    dm.nombre AS mensajero,
    SUM(hn.cantidad_novedades) AS total_novedades
FROM hecho_novedades hn
JOIN dim_mensajero dm
    ON hn.key_dim_mensajero = dm.key_mensajero
GROUP BY dm.nombre
ORDER BY total_novedades DESC
LIMIT 10;
"""
c5 = pd.read_sql(sql, etl_conn)
print("\n[5] Top 10 mensajeros con más novedades")
print(c5)

# pandas equivalente:
c5_pd = (
    hecho_novedades
    .merge(dim_mensajero[['key_mensajero', 'nombre']],
           left_on='key_dim_mensajero', right_on='key_mensajero', how='left')
    .groupby('nombre')['cantidad_novedades'].sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name='total_novedades')
)


# ===========================================================================
#  CONSULTA 6 — Novedades por CIUDAD DE OPERACIÓN del mensajero
# ===========================================================================
sql = """
SELECT
    dm.ciudad_operacion,
    SUM(hn.cantidad_novedades) AS total_novedades
FROM hecho_novedades hn
JOIN dim_mensajero dm
    ON hn.key_dim_mensajero = dm.key_mensajero
GROUP BY dm.ciudad_operacion
ORDER BY total_novedades DESC;
"""
c6 = pd.read_sql(sql, etl_conn)
print("\n[6] Novedades por ciudad de operación")
print(c6)


# ===========================================================================
#  CONSULTA 7 — Top SERVICIOS con más novedades
#  Un mismo servicio puede tener varias novedades: aquí se ve cuáles son
#  los más "problemáticos". Se agrupa por key_trans_servicio.
# ===========================================================================
sql = """
SELECT
    hn.key_trans_servicio,
    SUM(hn.cantidad_novedades) AS total_novedades
FROM hecho_novedades hn
WHERE hn.key_trans_servicio IS NOT NULL
GROUP BY hn.key_trans_servicio
ORDER BY total_novedades DESC
LIMIT 10;
"""
c7 = pd.read_sql(sql, etl_conn)
print("\n[7] Top 10 servicios con más novedades")
print(c7)


# ===========================================================================
#  CONSULTA 8 — Día hábil vs fin de semana
#  Usa el atributo es_fin_semana de dim_fecha.
# ===========================================================================
sql = """
SELECT
    CASE WHEN df.es_fin_semana THEN 'Fin de semana' ELSE 'Día hábil' END AS tipo_dia,
    SUM(hn.cantidad_novedades) AS total_novedades
FROM hecho_novedades hn
JOIN dim_fecha df
    ON hn.key_dim_fecha_novedad = df.key_fecha
GROUP BY 1
ORDER BY total_novedades DESC;
"""
c8 = pd.read_sql(sql, etl_conn)
print("\n[8] Novedades: día hábil vs fin de semana")
print(c8)


# ===========================================================================
#  CONSULTA 9 — Promedio de novedades por servicio
#  = total de novedades / número de servicios distintos que tuvieron novedad.
# ===========================================================================
sql = """
SELECT
    SUM(cantidad_novedades)::numeric
        / COUNT(DISTINCT key_trans_servicio)      AS novedades_por_servicio
FROM hecho_novedades
WHERE key_trans_servicio IS NOT NULL;
"""
c9 = pd.read_sql(sql, etl_conn)
print("\n[9] Promedio de novedades por servicio")
print(c9)


# ===========================================================================
#  CONSULTA 10 — CONTROL DE CALIDAD: filas huérfanas (llaves nulas)
#  Cuenta cuántas novedades no encontraron pareja en cada dimensión
#  (consecuencia de los LEFT JOIN). Excelente para defender el diseño.
# ===========================================================================
sql = """
SELECT
    COUNT(*) FILTER (WHERE key_novedad           IS NULL) AS sin_novedad,
    COUNT(*) FILTER (WHERE key_dim_mensajero     IS NULL) AS sin_mensajero,
    COUNT(*) FILTER (WHERE key_trans_servicio    IS NULL) AS sin_servicio,
    COUNT(*) FILTER (WHERE key_dim_fecha_novedad IS NULL) AS sin_fecha,
    COUNT(*)                                              AS total_filas
FROM hecho_novedades;
"""
c10 = pd.read_sql(sql, etl_conn)
print("\n[10] Control de calidad: llaves nulas (huérfanas)")
print(c10)

# pandas equivalente:
c10_pd = pd.DataFrame({
    'sin_novedad':   [hecho_novedades['key_novedad'].isna().sum()],
    'sin_mensajero': [hecho_novedades['key_dim_mensajero'].isna().sum()],
    'sin_servicio':  [hecho_novedades['key_trans_servicio'].isna().sum()],
    'sin_fecha':     [hecho_novedades['key_dim_fecha_novedad'].isna().sum()],
    'total_filas':   [len(hecho_novedades)]
})


# ===========================================================================
#  CONSULTA 11 — Novedades por AÑO y TRIMESTRE (evolución temporal)
# ===========================================================================
sql = """
SELECT
    df."año",
    df.trimestre,
    SUM(hn.cantidad_novedades) AS total_novedades
FROM hecho_novedades hn
JOIN dim_fecha df
    ON hn.key_dim_fecha_novedad = df.key_fecha
GROUP BY df."año", df.trimestre
ORDER BY df."año", df.trimestre;
"""
c11 = pd.read_sql(sql, etl_conn)
print("\n[11] Novedades por año y trimestre")
print(c11)


print("\n\n=== Todas las consultas se ejecutaron correctamente ===")
