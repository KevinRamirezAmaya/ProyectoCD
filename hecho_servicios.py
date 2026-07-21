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
dim_proveedor=pd.read_sql_table('dim_proveedor', etl_conn)

dim_mensajero=pd.read_sql_table('dim_mensajero', etl_conn)

dim_sede=pd.read_sql_table('dim_sede', etl_conn)

dim_hora=pd.read_sql_table('dim_hora', etl_conn)    

dim_geografia=pd.read_sql_table('dim_geografia', etl_conn)

dim_fecha=pd.read_sql_table('dim_fecha', etl_conn)

dim_usuario=pd.read_sql_table('dim_usuario', etl_conn)

trans_servicio=pd.read_sql_table('trans_servicio', etl_conn)



tabla_sede=pd.read_sql_table('clientes_usuarioaquitoy', mensajeria)

tabla_estados=pd.read_sql_table('mensajeria_estadosservicio', mensajeria)
trans_servicio.head()

hecho_servicios= trans_servicio.merge(dim_proveedor[['id_proveedor','key_proveedor']], left_on='cliente_id',right_on='id_proveedor', how='left') \

    .rename(columns={'key_proveedor':'key_dim_proveedor'}) \

    .merge(dim_mensajero[['id_operaciones','key_mensajero']], left_on='mensajero_id',right_on='id_operaciones', how='left') \

    .rename(columns={'key_mensajero':'key_mensajero_1'}) \

    .merge(dim_mensajero[['id_operaciones','key_mensajero']], left_on='mensajero2_id', right_on='id_operaciones', how='left') \

    .rename(columns={'key_mensajero':'key_mensajero_2'}) \

    .merge(dim_mensajero[['id_operaciones','key_mensajero']], left_on='mensajero3_id', right_on='id_operaciones', how='left')  \

    .rename(columns={'key_mensajero':'key_mensajero_3'}) \

    .merge(dim_sede[['sede_id','key_sede']], left_on='sede_id', right_on='sede_id', how='left') \

    .merge(dim_geografia[['ciudad_id','key_geografia']], left_on='ciudad_origen_id',right_on='ciudad_id', how='left') \

    .rename(columns={'key_geografia':'key_geografia_origen'}) \

    .merge(dim_geografia[['ciudad_id','key_geografia']], left_on='ciudad_destino_id',right_on='ciudad_id', how='left') \

    .rename(columns={'key_geografia':'key_geografia_destino'})



hecho_servicios['key_mensajero_1'].value_counts()
#####Merge con dim_fecha y dim_hora para cada fecha y hora relevante en hecho_servicios



# --- Bloque: solicitud ---

hecho_servicios = hecho_servicios.merge(dim_fecha[['fecha_completa','key_fecha']], left_on='fecha_solicitud', right_on='fecha_completa', how='left') \

                                .merge(dim_hora[['hora_completa','key_hora']], left_on='hora_solicitud', right_on='hora_completa', how='left')



hecho_servicios = hecho_servicios.rename(columns={'key_fecha':'key_dim_fecha_solicitud','key_hora':'key_dim_hora_solicitud'}, inplace=False)

hecho_servicios.drop(columns=['fecha_completa','hora_completa'], inplace=True)



# --- Bloque: iniciado ---

hecho_servicios = hecho_servicios.merge(dim_fecha[['fecha_completa','key_fecha']], left_on='fecha_iniciado', right_on='fecha_completa', how='left') \

                                .merge(dim_hora[['hora_completa','key_hora']], left_on='hora_iniciado', right_on='hora_completa', how='left')



hecho_servicios = hecho_servicios.rename(columns={'key_fecha':'key_dim_fecha_iniciado','key_hora':'key_dim_hora_iniciado'}, inplace=False)

hecho_servicios.drop(columns=['fecha_completa','hora_completa'], inplace=True)





# --- Bloque: mensajero_asignado ---

hecho_servicios = hecho_servicios.merge(dim_fecha[['fecha_completa','key_fecha']], left_on='fecha_mensajero_asignado', right_on='fecha_completa', how='left') \

                                .merge(dim_hora[['hora_completa','key_hora']], left_on='hora_mensajero_asignado', right_on='hora_completa', how='left')



hecho_servicios = hecho_servicios.rename(columns={'key_fecha':'key_dim_fecha_mensajero_asignado','key_hora':'key_dim_hora_mensajero_asignado'}, inplace=False)

hecho_servicios.drop(columns=['fecha_completa','hora_completa'], inplace=True)





# --- Bloque: recogido_mensajero ---

hecho_servicios = hecho_servicios.merge(dim_fecha[['fecha_completa','key_fecha']], left_on='fecha_recogido_mensajero', right_on='fecha_completa', how='left') \

                                .merge(dim_hora[['hora_completa','key_hora']], left_on='hora_recogido_mensajero', right_on='hora_completa', how='left')



hecho_servicios = hecho_servicios.rename(columns={'key_fecha':'key_dim_fecha_recogido_mensajero','key_hora':'key_dim_hora_recogido_mensajero'}, inplace=False)

hecho_servicios.drop(columns=['fecha_completa','hora_completa'], inplace=True)





# --- Bloque: entregado ---

hecho_servicios = hecho_servicios.merge(dim_fecha[['fecha_completa','key_fecha']], left_on='fecha_entregado', right_on='fecha_completa', how='left') \

                                .merge(dim_hora[['hora_completa','key_hora']], left_on='hora_entregado', right_on='hora_completa', how='left')



hecho_servicios = hecho_servicios.rename(columns={'key_fecha':'key_dim_fecha_entregado','key_hora':'key_dim_hora_entregado'}, inplace=False)

hecho_servicios.drop(columns=['fecha_completa','hora_completa'], inplace=True)





# --- Bloque: finalizado_completo ---

hecho_servicios = hecho_servicios.merge(dim_fecha[['fecha_completa','key_fecha']], left_on='fecha_finalizado_completo', right_on='fecha_completa', how='left') \

                                .merge(dim_hora[['hora_completa','key_hora']], left_on='hora_finalizado_completo', right_on='hora_completa', how='left')



hecho_servicios = hecho_servicios.rename(columns={'key_fecha':'key_dim_fecha_finalizado_completo','key_hora':'key_dim_hora_finalizado_completo'}, inplace=False)

hecho_servicios.drop(columns=['fecha_completa','hora_completa'], inplace=True)





hecho_servicios.drop(columns=['id_proveedor','id_operaciones_x','id_operaciones_y','id_operaciones','ciudad_id_x','ciudad_id_y',

                              'mensajero_id','mensajero2_id','mensajero3_id','ciudad_origen_id','ciudad_destino_id','sede_id','cliente_id','usuario_id',

                                'user_id','hora_entregado','hora_iniciado','servicio_id','fecha_solicitud','fecha_iniciado','hora_solicitud','hora_iniciado','fecha_entregado','fecha_finalizado_completo','hora_finalizado_completo',

                                'fecha_mensajero_asignado','fecha_recogido_mensajero',

                                'hora_mensajero_asignado','hora_recogido_mensajero'

                              ], inplace=True)





hecho_servicios.info()
columnas_keys_fecha_hora = [

    'key_dim_fecha_solicitud', 'key_dim_hora_solicitud',

    'key_dim_fecha_iniciado', 'key_dim_hora_iniciado',

    'key_dim_fecha_mensajero_asignado', 'key_dim_hora_mensajero_asignado',

    'key_dim_fecha_recogido_mensajero', 'key_dim_hora_recogido_mensajero',

    'key_dim_fecha_entregado', 'key_dim_hora_entregado',

    'key_dim_fecha_finalizado_completo', 'key_dim_hora_finalizado_completo'

]



for col in columnas_keys_fecha_hora:

    hecho_servicios[col] = hecho_servicios[col].astype('Int64')


print(hecho_servicios['key_dim_hora_iniciado'].value_counts())
hecho_servicios.head()
hecho_servicios['key_dim_fecha_entregado'].value_counts()
# Compara los sets de valores únicos

  # si esto es 0 o muy bajo, ahí está el problema

# Compara valores "iguales" carácter por carácter

val_a = trans_servicio['hora_iniciado'].iloc[0]

val_b = dim_hora['hora_completa'].iloc[0]

print(repr(val_a), repr(val_b))   # repr muestra comillas, espacios ocultos, tipo exacto

print(type(val_a), type(val_b))
hecho_servicios.to_sql('hecho_servicios', etl_conn, if_exists='replace', index=False)

print(f'hecho_novedades cargada correctamente: {hecho_servicios.shape[0]} filas, {hecho_servicios.shape[1]} columnas')