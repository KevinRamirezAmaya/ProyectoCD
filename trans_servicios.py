import pandas as pd

import numpy as np

import psycopg2

import sqlalchemy as db

from sqlalchemy import create_engine

import yaml
with open('.\\config.yml', 'r') as f:

    config = yaml.safe_load(f)

    config_co = config['mensajeria']

    config_etl = config['ETL_PRO']



# Construct the database URL

url_co = (f"{config_co['drivername']}://{config_co['user']}:{config_co['password']}@{config_co['host']}:"

          f"{config_co['port']}/{config_co['dbname']}")

url_etl = (f"{config_etl['drivername']}://{config_etl['user']}:{config_etl['password']}@{config_etl['host']}:"

           f"{config_etl['port']}/{config_etl['dbname']}")

# Create the SQLAlchemy Engine

mensajeria = create_engine(url_co)

etl_conn = create_engine(url_etl)
pd.set_option('display.max_columns', None)

pd.set_option('display.max_rows', None)

pd.set_option('display.width', None)

pd.set_option('display.max_colwidth', 50)

tabla_servicios = pd.read_sql_table('mensajeria_servicio', mensajeria)

 

tabla_estados=pd.read_sql_table('mensajeria_estadosservicio', mensajeria)

tabla_sede = pd.read_sql_table('clientes_usuarioaquitoy', mensajeria)



tabla_servicios.rename(columns={'id':'servicio_id'}, inplace=True)



tabla_servicios["key_trans_servicio"] = range(1,len(tabla_servicios)+1 )





tabla_servicios.drop(columns=['novedades', 'fecha_deseada', 'hora_deseada','nombre_recibe','telefono_recibe','hora_visto_por_mensajero',

                              'descripcion_pago','ida_y_regreso','tipo_pago_id','prioridad','visto_por_mensajero','multiples_origenes',

                              'descripcion_cancelado','descripcion_multiples_origenes','activo','asignar_mensajero','es_prueba',

                              'nombre_solicitante','descripcion','origen_id','destino_id','tipo_vehiculo_id','tipo_servicio_id'], inplace=True)







tabla_servicios = tabla_servicios.merge(tabla_sede[['cliente_id','user_id','sede_id']],

                                        left_on=['cliente_id','usuario_id'], right_on=['cliente_id','user_id'], how='left')



tabla_servicios['mensajero_id']=tabla_servicios['mensajero_id'].fillna(0).astype(int)

tabla_servicios['mensajero2_id']=tabla_servicios['mensajero2_id'].fillna(0).astype(int)

tabla_servicios['mensajero3_id']=tabla_servicios['mensajero3_id'].fillna(0).astype(int)



print(tabla_servicios['mensajero_id'].value_counts()) 

tabla_servicios.info()

print(len(tabla_servicios))  

tabla_estados_pivot_fecha = tabla_estados.pivot_table(

    index='servicio_id',

    columns='estado_id',

    values='fecha',

    aggfunc='first'      

).reset_index()

print(len(tabla_servicios))  



tabla_estados_pivot_hora = tabla_estados.pivot_table(

    index='servicio_id',

    columns='estado_id',

    values='hora',

    aggfunc='first'      

).reset_index()

trans_servicios = tabla_servicios.merge(tabla_estados_pivot_fecha, on='servicio_id', how='left')

print(len(tabla_servicios))  

trans_servicios.drop(columns=[3], inplace=True)

trans_servicios.rename(columns={1:'fecha_iniciado', 2:'fecha_mensajero_asignado', 4:'fecha_recogido_mensajero',

                                 5:'fecha_entregado',6:'fecha_finalizado_completo'}, inplace=True)

trans_servicios = trans_servicios.merge(tabla_estados_pivot_hora, on='servicio_id', how='left')

trans_servicios.drop(columns=[3], inplace=True)

trans_servicios.rename(columns={1:'hora_iniciado', 2:'hora_mensajero_asignado', 4:'hora_recogido_mensajero',

                                 5:'hora_entregado',6:'hora_finalizado_completo'}, inplace=True)

trans_servicios['sede_id'] = trans_servicios['sede_id'].fillna(0).astype(int)

trans_servicios['user_id'] = trans_servicios['user_id'].fillna(0).astype(int)

trans_servicios.info()  

# Combinar fecha y hora de inicio para la comparación

dt_iniciado = pd.to_datetime(

    trans_servicios['fecha_iniciado'].dt.date.astype(str) + ' ' + trans_servicios['hora_iniciado'].astype(str),

    format='%Y-%m-%d %H:%M:%S',

    errors='coerce'

)



# Inicializar máscara de inconsistencia

inconsistente = pd.Series(False, index=trans_servicios.index)



# 1. Verificar si la solicitud ocurrió después del inicio (iniciado antes de la solicitud)

dt_solicitud = pd.to_datetime(

    trans_servicios['fecha_solicitud'].dt.date.astype(str) + ' ' + trans_servicios['hora_solicitud'].astype(str),

    format='%Y-%m-%d %H:%M:%S',

    errors='coerce'

)

inconsistente = inconsistente | (dt_iniciado < dt_solicitud)



# 2. Verificar si alguna etapa posterior ocurrió antes del inicio

etapas_posteriores = [

    ('fecha_mensajero_asignado', 'hora_mensajero_asignado'),

    ('fecha_recogido_mensajero', 'hora_recogido_mensajero'),

    ('fecha_entregado', 'hora_entregado'),

    ('fecha_finalizado_completo', 'hora_finalizado_completo')

]



for f_col, h_col in etapas_posteriores:

    dt_etapa = pd.to_datetime(

        trans_servicios[f_col].dt.date.astype(str) + ' ' + trans_servicios[h_col].astype(str),

        format='%Y-%m-%d %H:%M:%S',

        errors='coerce'

    )

    inconsistente = inconsistente | (dt_etapa < dt_iniciado)



# Eliminar filas inconsistentes

print(f"Filas antes de la limpieza: {len(trans_servicios)}")

trans_servicios = trans_servicios[~inconsistente]

print(f"Filas después de la limpieza: {len(trans_servicios)}")

trans_servicios['mensajero_id'].value_counts()
# --- NUEVO CÓDIGO: Cálculo de métricas (Minutos) ---

dt_solicitud = pd.to_datetime(trans_servicios['fecha_solicitud'].dt.date.astype(str) + ' ' + trans_servicios['hora_solicitud'].astype(str), format='%Y-%m-%d %H:%M:%S', errors='coerce')

dt_iniciado = pd.to_datetime(trans_servicios['fecha_iniciado'].dt.date.astype(str) + ' ' + trans_servicios['hora_iniciado'].astype(str), format='%Y-%m-%d %H:%M:%S', errors='coerce')

dt_mensajero_asignado = pd.to_datetime(trans_servicios['fecha_mensajero_asignado'].dt.date.astype(str) + ' ' + trans_servicios['hora_mensajero_asignado'].astype(str), format='%Y-%m-%d %H:%M:%S', errors='coerce')

dt_recogido = pd.to_datetime(trans_servicios['fecha_recogido_mensajero'].dt.date.astype(str) + ' ' + trans_servicios['hora_recogido_mensajero'].astype(str), format='%Y-%m-%d %H:%M:%S', errors='coerce')

dt_entregado = pd.to_datetime(trans_servicios['fecha_entregado'].dt.date.astype(str) + ' ' + trans_servicios['hora_entregado'].astype(str), format='%Y-%m-%d %H:%M:%S', errors='coerce')

dt_cerrado = pd.to_datetime(trans_servicios['fecha_finalizado_completo'].dt.date.astype(str) + ' ' + trans_servicios['hora_finalizado_completo'].astype(str), format='%Y-%m-%d %H:%M:%S', errors='coerce')

trans_servicios['minutos_solicitud_iniciado'] = (dt_iniciado - dt_solicitud).dt.total_seconds() / 60

trans_servicios['minutos_iniciado_asignado'] = (dt_mensajero_asignado - dt_iniciado).dt.total_seconds() / 60

trans_servicios['minutos_asignado_recogido'] = (dt_recogido - dt_mensajero_asignado).dt.total_seconds() / 60

trans_servicios['minutos_recogido_entregado'] = (dt_entregado - dt_recogido).dt.total_seconds() / 60

trans_servicios['minutos_entregado_cerrado'] = (dt_cerrado - dt_entregado).dt.total_seconds() / 60

trans_servicios['minutos_totales_servicio'] = (dt_cerrado - dt_solicitud).dt.total_seconds() / 60

# -----------------------------------------------------

trans_servicios.to_sql('trans_servicio', etl_conn, if_exists='replace', index=False)


