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



url_co = (f"{config_co['drivername']}://{config_co['user']}:{config_co['password']}@{config_co['host']}:"

          f"{config_co['port']}/{config_co['dbname']}")

url_etl = (f"{config_etl['drivername']}://{config_etl['user']}:{config_etl['password']}@{config_etl['host']}:"

           f"{config_etl['port']}/{config_etl['dbname']}")



mensajeria = create_engine(url_co)

etl_conn   = create_engine(url_etl)
novedades_raw = pd.read_sql_table('mensajeria_novedadesservicio', mensajeria)



dim_novedades  = pd.read_sql_table('dim_novedades',  etl_conn)

dim_mensajero  = pd.read_sql_table('dim_mensajero',  etl_conn)

dim_fecha      = pd.read_sql_table('dim_fecha',      etl_conn)

trans_servicio = pd.read_sql_table('trans_servicio', etl_conn)
novedades_raw.head()
novedades_raw.info()
novedades_raw = novedades_raw[novedades_raw['es_prueba'] == False].copy()



novedades_raw = novedades_raw.rename(columns={'id': 'novedad_id'})



dim_fecha['fecha_completa'] = pd.to_datetime(dim_fecha['fecha_completa']).dt.normalize()

novedades_raw['fecha_novedad'] = pd.to_datetime(novedades_raw['fecha_novedad']).dt.tz_convert(None).dt.normalize()



val_a = novedades_raw['fecha_novedad'].iloc[0]

val_b = dim_fecha['fecha_completa'].iloc[0]

print(repr(val_a), repr(val_b))

print(type(val_a), type(val_b))



novedades_raw.head()
hecho_novedades = novedades_raw.merge(

    dim_novedades[['novedad_id', 'key_novedad']],

    on='novedad_id',

    how='left'

)



hecho_novedades = hecho_novedades.merge(

    dim_mensajero[['id_operaciones', 'key_mensajero']],

    left_on='mensajero_id',

    right_on='id_operaciones',

    how='left'

).rename(columns={'key_mensajero': 'key_dim_mensajero'})



hecho_novedades = hecho_novedades.merge(

    trans_servicio[['servicio_id', 'key_trans_servicio']],

    on='servicio_id',

    how='left'

)



hecho_novedades = hecho_novedades.merge(

    dim_fecha[['fecha_completa', 'key_fecha']],

    left_on='fecha_novedad',

    right_on='fecha_completa',

    how='left'

).rename(columns={'key_fecha': 'key_dim_fecha_novedad'})

hecho_novedades.drop(columns=['fecha_completa'], inplace=True)



hecho_novedades['key_novedad'].value_counts()
hecho_novedades['cantidad_novedades'] = 1



cols_to_drop = [

    'novedad_id',

    'mensajero_id',

    'tipo_novedad_id',

    'descripcion',

    'servicio_id',

    'es_prueba',

    'fecha_novedad',

    'id_operaciones'

]

hecho_novedades.drop(

    columns=[c for c in cols_to_drop if c in hecho_novedades.columns],

    inplace=True

)





key_cols = ['key_novedad', 'key_dim_mensajero', 'key_trans_servicio', 'key_dim_fecha_novedad']

for col in key_cols:

    hecho_novedades[col] = hecho_novedades[col].astype('Int64')



hecho_novedades.info()
hecho_novedades.head()
hecho_novedades.to_sql('hecho_novedades', etl_conn, if_exists='replace', index=False)

print(f'hecho_novedades cargada correctamente: {hecho_novedades.shape[0]} filas, {hecho_novedades.shape[1]} columnas')