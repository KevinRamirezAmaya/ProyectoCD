import pandas as pd

import yaml

from sqlalchemy import create_engine
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
hecho_servicios = pd.read_sql_table('hecho_servicios', etl_conn)

hecho_novedades = pd.read_sql_table('hecho_novedades', etl_conn)



dim_fecha = pd.read_sql_table('dim_fecha', etl_conn)

dim_hora = pd.read_sql_table('dim_hora', etl_conn)

dim_proveedor = pd.read_sql_table('dim_proveedor', etl_conn)

dim_mensajero = pd.read_sql_table('dim_mensajero', etl_conn)

dim_sede = pd.read_sql_table('dim_sede', etl_conn)

dim_novedades = pd.read_sql_table('dim_novedades', etl_conn)
consulta = """

SELECT

    df.nombre_mes,

    COUNT(*) AS total_servicios

FROM hecho_servicios hs

JOIN dim_fecha df

    ON hs.key_dim_fecha_solicitud = df.key_fecha

GROUP BY df.nombre_mes

ORDER BY total_servicios DESC;

"""



resultado = pd.read_sql(consulta, etl_conn)

resultado
consulta = """

SELECT

    df.nombre_dia,

    COUNT(*) AS total_servicios

FROM hecho_servicios hs

JOIN dim_fecha df

    ON hs.key_dim_fecha_solicitud = df.key_fecha

GROUP BY df.nombre_dia

ORDER BY total_servicios DESC;

"""



resultado = pd.read_sql(consulta, etl_conn)

resultado
consulta = """

SELECT 

    CASE 

        WHEN hora_num BETWEEN 0 AND 2 THEN '00-02'

        WHEN hora_num BETWEEN 3 AND 5 THEN '03-05'

        WHEN hora_num BETWEEN 6 AND 8 THEN '06-08'

        WHEN hora_num BETWEEN 9 AND 11 THEN '09-11'

        WHEN hora_num BETWEEN 12 AND 14 THEN '12-14'

        WHEN hora_num BETWEEN 15 AND 17 THEN '15-17'

        WHEN hora_num BETWEEN 18 AND 20 THEN '18-20'

        ELSE '21-23'

    END AS rango_hora,

    COUNT(*) AS total_servicios_activos

FROM (

    SELECT 

        EXTRACT(HOUR FROM gs) AS hora_num

    FROM hecho_servicios hs

    LEFT JOIN dim_fecha fa ON hs.key_dim_fecha_mensajero_asignado = fa.key_fecha

    LEFT JOIN dim_hora ha ON hs.key_dim_hora_mensajero_asignado = ha.key_hora

    LEFT JOIN dim_fecha fc ON hs.key_dim_fecha_finalizado_completo = fc.key_fecha

    LEFT JOIN dim_hora hc ON hs.key_dim_hora_finalizado_completo = hc.key_hora

    CROSS JOIN LATERAL generate_series(

        date_trunc('hour', fa.fecha_completa + ha.hora_completa),

        date_trunc('hour', fc.fecha_completa + hc.hora_completa),

        '1 hour'::interval

    ) gs

    WHERE fa.fecha_completa IS NOT NULL AND fc.fecha_completa IS NOT NULL

) horas_ocupadas

GROUP BY 1 

ORDER BY total_servicios_activos DESC;

"""



resultado = pd.read_sql(consulta, etl_conn)

resultado
consulta = """

SELECT

    dp.nombre_proveedor,

    df.nombre_mes,

    COUNT(*) AS total_servicios

FROM hecho_servicios hs

JOIN dim_proveedor dp

    ON hs.key_dim_proveedor = dp.key_proveedor

JOIN dim_fecha df

    ON hs.key_dim_fecha_solicitud = df.key_fecha

GROUP BY

    dp.nombre_proveedor,

    df.nombre_mes

ORDER BY

    dp.nombre_proveedor,

    df.nombre_mes;

"""



resultado = pd.read_sql(consulta, etl_conn)

resultado
consulta = """

SELECT

    dm.nombre,

    COUNT(*) AS servicios_realizados

FROM hecho_servicios hs

JOIN dim_mensajero dm

    ON hs.key_mensajero_1 = dm.key_mensajero

GROUP BY dm.nombre

ORDER BY servicios_realizados DESC;

"""



resultado = pd.read_sql(consulta, etl_conn)

resultado
consulta = """

SELECT

    dp.nombre_proveedor,

    ds.nombre,

    COUNT(*) AS total_servicios

FROM hecho_servicios hs

JOIN dim_proveedor dp

    ON hs.key_dim_proveedor = dp.key_proveedor

JOIN dim_sede ds

    ON hs.key_sede = ds.key_sede

GROUP BY

    dp.nombre_proveedor,

    ds.nombre

ORDER BY

    dp.nombre_proveedor,

    total_servicios DESC;

"""



resultado = pd.read_sql(consulta, etl_conn)

resultado
consulta = """

SELECT

    AVG(

        (ff.fecha_completa + hf.hora_completa)

        -

        (fs.fecha_completa + hs_time.hora_completa)

    ) AS tiempo_promedio

FROM hecho_servicios hs

JOIN dim_fecha fs ON hs.key_dim_fecha_solicitud = fs.key_fecha

JOIN dim_hora hs_time ON hs.key_dim_hora_solicitud = hs_time.key_hora

JOIN dim_fecha ff ON hs.key_dim_fecha_finalizado_completo = ff.key_fecha

JOIN dim_hora hf ON hs.key_dim_hora_finalizado_completo = hf.key_hora;

"""



resultado = pd.read_sql(consulta, etl_conn)

resultado
consulta = """

WITH promedios AS (

    SELECT

        ROUND(CAST(EXTRACT(EPOCH FROM AVG((fa.fecha_completa + ha.hora_completa) - (fi.fecha_completa + hi.hora_completa))) / 60 AS NUMERIC), 2) AS iniciado_asignado,

        ROUND(CAST(EXTRACT(EPOCH FROM AVG((fr.fecha_completa + hr.hora_completa) - (fa.fecha_completa + ha.hora_completa))) / 60 AS NUMERIC), 2) AS asignado_recogido,

        ROUND(CAST(EXTRACT(EPOCH FROM AVG((fe.fecha_completa + he.hora_completa) - (fr.fecha_completa + hr.hora_completa))) / 60 AS NUMERIC), 2) AS recogido_entregado,

        ROUND(CAST(EXTRACT(EPOCH FROM AVG((fc.fecha_completa + hc.hora_completa) - (fe.fecha_completa + he.hora_completa))) / 60 AS NUMERIC), 2) AS entregado_cerrado

    FROM hecho_servicios hs

    LEFT JOIN dim_fecha fi ON hs.key_dim_fecha_iniciado = fi.key_fecha

    LEFT JOIN dim_hora hi ON hs.key_dim_hora_iniciado = hi.key_hora

    LEFT JOIN dim_fecha fa ON hs.key_dim_fecha_mensajero_asignado = fa.key_fecha

    LEFT JOIN dim_hora ha ON hs.key_dim_hora_mensajero_asignado = ha.key_hora

    LEFT JOIN dim_fecha fr ON hs.key_dim_fecha_recogido_mensajero = fr.key_fecha

    LEFT JOIN dim_hora hr ON hs.key_dim_hora_recogido_mensajero = hr.key_hora

    LEFT JOIN dim_fecha fe ON hs.key_dim_fecha_entregado = fe.key_fecha

    LEFT JOIN dim_hora he ON hs.key_dim_hora_entregado = he.key_hora

    LEFT JOIN dim_fecha fc ON hs.key_dim_fecha_finalizado_completo = fc.key_fecha

    LEFT JOIN dim_hora hc ON hs.key_dim_hora_finalizado_completo = hc.key_hora

)

SELECT 

    iniciado_asignado,

    asignado_recogido,

    recogido_entregado,

    entregado_cerrado,

    CASE GREATEST(iniciado_asignado, asignado_recogido, recogido_entregado, entregado_cerrado)

        WHEN iniciado_asignado THEN 'iniciado_asignado'

        WHEN asignado_recogido THEN 'asignado_recogido'

        WHEN recogido_entregado THEN 'recogido_entregado'

        WHEN entregado_cerrado THEN 'entregado_cerrado'

    END AS etapa_mas_demorada

FROM promedios;

"""



resultado = pd.read_sql(consulta, etl_conn)

resultado
consulta = """

SELECT

    dn.key_novedad,

    COUNT(*) AS total_novedades

FROM hecho_novedades hn

JOIN dim_novedades dn

    ON hn.key_novedad = dn.key_novedad

GROUP BY dn.key_novedad

ORDER BY total_novedades DESC;

"""

resultado = pd.read_sql(consulta, etl_conn)

resultado