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
dim_persona = pd.read_sql_table('clientes_datosmensajero', mensajeria)

dim_persona.head(10)


df = pd.read_sql_table('mensajeria_estado', mensajeria)

df.head
pd.set_option('display.max_columns', None)

pd.set_option('display.max_rows', 10)

pd.set_option('display.width', None)

pd.set_option('display.max_colwidth', 50)

df = pd.read_sql_table('mensajeria_novedadesservicio', mensajeria)

df.head(100).T
tabla_estados = pd.read_sql_table('mensajeria_estadosservicio', mensajeria)

tabla_estados.head(100)
tabla_estados['estado_id'].value_counts()
columnas_hora = [

    'hora_iniciado',

    'hora_mensajero_asignado',

    'hora_recogido_mensajero',

    'hora_entregado',

    'hora_finalizado_completo'

]



for col in columnas_hora:

    if col in trans_servicio.columns:

        trans_servicio[col] = trans_servicio[col].apply(

            lambda t: t.strftime('%H:%M:%S') if pd.notna(t) else t

        )
