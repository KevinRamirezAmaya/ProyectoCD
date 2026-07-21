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
tabla_novedades = pd.read_sql_table('mensajeria_novedadesservicio',mensajeria)



tabla_novedades['tipo_novedad_id'].value_counts()

tabla_novedades.head(10)
tabla_tiponovedad = pd.read_sql_table('mensajeria_tiponovedad', mensajeria)

tabla_tiponovedad.head(10)
dim_novedades= pd.merge(tabla_novedades,tabla_tiponovedad, left_on='tipo_novedad_id', right_on='id', how='left')

dim_novedades = dim_novedades.drop(columns=['id_y','mensajero_id','tipo_novedad_id'])

dim_novedades['key_novedad'] = range(1,len(dim_novedades)+1)

dim_novedades = dim_novedades.rename(columns={'id_x': 'novedad_id'})

dim_novedades.head(10)

#dim_novedades['descripcion'].value_counts()
pd.set_option('display.max_columns', None)

pd.set_option('display.max_rows', 10)

pd.set_option('display.width', None)

pd.set_option('display.max_colwidth', 50)

df = pd.read_sql_table('mensajeria_estadosservicio', mensajeria)

df[df['servicio_id'] == 21953].head(100).T

dim_novedades['descripcion'].value_counts()
dim_novedades.to_sql('dim_novedades', etl_conn, if_exists='replace', index=False)