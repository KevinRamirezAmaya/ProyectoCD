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
tabla_cliente = pd.read_sql_table('cliente', mensajeria)

tabla_cliente.groupby('cliente_id')

tabla_cliente.tail(10)
dim_proveedor = tabla_cliente

dim_proveedor.rename(columns={'cliente_id':'id_proveedor','nombre':'nombre_proveedor'}, inplace=True)

#Se eliminan datos de la tabla clientes

dim_proveedor.drop(columns=['email','telefono','direccion','nombre_contacto','ciudad_id','tipo_cliente_id','activo','coordinador_id'], inplace=True)

#se eliminan los datos de la tabla sede

dim_proveedor.rename(columns={'nombre':'nombre_proveedor'},inplace=True)

dim_proveedor['key_proveedor']=range(1,len(dim_proveedor)+1)

dim_proveedor['sector']=dim_proveedor['sector'].replace('S','salud')

dim_proveedor.head()
dim_proveedor.to_sql('dim_proveedor', etl_conn, if_exists='replace', index=False)