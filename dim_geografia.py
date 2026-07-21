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
tabla_departamento = pd.read_sql_table('departamento', mensajeria)

tabla_departamento.head(10)
tabla_ciudad = pd.read_sql_table('ciudad', mensajeria)

tabla_ciudad.head(10)
dim_geografia = pd.merge(tabla_ciudad,tabla_departamento,left_on='departamento_id',right_on='departamento_id',how='left')

dim_geografia['key_geografia'] = range(1,len(dim_geografia)+1)

dim_geografia.drop(columns=['departamento_id'], inplace=True)

dim_geografia.rename(columns={'nombre_x':'ciudad','nombre_y':'departamento'},inplace=True)

dim_geografia.head(20)
dim_geografia.to_sql('dim_geografia', etl_conn, if_exists='replace', index=False)
dim_geografia.to_sql('dim_geografia', etl_conn, if_exists='replace', index=False)